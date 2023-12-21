import shutil
import tarfile
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union

from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from nonebot.log import logger
from starlette.routing import Mount

from ..lib.store import cache_dir, static_dir
from ..model.api import FaildResponse, Response
from .base import app

webui_dir = cache_dir.joinpath("webui")
webui_dir.mkdir(parents=True, exist_ok=True)


@app.get("/webui")
async def read_html():
    return HTMLResponse(static_dir.joinpath("upload-webui.html").read_text(encoding="utf-8"))


@app.post("/webui/update")
async def upload_file(file: UploadFile = File(...)) -> Union[Response[None], FaildResponse]:
    file_data = await file.read()
    filename = file.filename or ""

    with tempfile.TemporaryDirectory() as temp_dir:
        if filename.endswith(".zip"):
            zip_file = zipfile.ZipFile(BytesIO(file_data))
            zip_file.extractall(temp_dir)
        elif filename.endswith(".tar.gz"):
            tar_file = tarfile.open(fileobj=BytesIO(file_data), mode="r:gz")
            tar_file.extractall(temp_dir)
        else:
            return FaildResponse(code=400, message="未知文件格式")

        for index_file in Path(temp_dir).rglob("index.html"):
            index_dir = index_file.parent
            if webui_dir.exists():
                shutil.rmtree(webui_dir)
            shutil.move(index_dir, webui_dir)

            break
        else:
            return FaildResponse(code=400, message="压缩文件中不存在 index.html")

    if not any(isinstance(route, Mount) and route.name == "webui" for route in app.routes):
        app.mount("/", StaticFiles(directory=webui_dir, html=True), name="webui")

    logger.success("成功更新 WebUI")
    return Response[None](data=None)


@app.delete("/webui/update")
async def reset_webui() -> Response[None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        tar_file = tarfile.open(fileobj=BytesIO(static_dir.joinpath("webui.tar.gz").read_bytes()), mode="r:gz")
        tar_file.extractall(temp_dir)

        for index_file in Path(temp_dir).rglob("index.html"):
            index_dir = index_file.parent
            if webui_dir.exists():
                shutil.rmtree(webui_dir)
            shutil.move(index_dir, webui_dir)
            break

    if not any(isinstance(route, Mount) and route.name == "webui" for route in app.routes):
        app.mount("/", StaticFiles(directory=webui_dir, html=True), name="webui")

    logger.success("成功重置为默认 WebUI")
    return Response[None](data=None)
