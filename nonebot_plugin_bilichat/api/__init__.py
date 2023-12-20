import gzip
import shutil
import tarfile
from io import BytesIO

from fastapi.staticfiles import StaticFiles
from httpx import AsyncClient
from nonebot.log import logger
from packaging.version import Version

from ..config import plugin_config, raw_config
from ..lib.store import cache_dir, static_dir
from ..lib.strings import generate_framed_text

if plugin_config.bilichat_webui_path:
    from nonebot import get_driver

    from . import bilibili_auth, subs_config  # noqa: F401
    from .base import app

    webui_dir = cache_dir.joinpath("webui")
    webui_dir.mkdir(parents=True, exist_ok=True)
    version_file = webui_dir.joinpath("version.txt")
    version_file.touch(exist_ok=True)
    driver = get_driver()
    app.mount("/", StaticFiles(directory=webui_dir, html=True), name="static")
    propmt = [
        "SETTING UP BILICHAT WebUI AT",
        f"http://{raw_config.host}:{raw_config.port}/{plugin_config.bilichat_webui_path}/",
    ]
    if plugin_config.bilichat_webui_path == "bilichat":
        propmt.extend(
            [
                "WARNING: Bilichat WebUI is currently running on default path. "
                "Please consider to use different path via adding config `bilichat_webui_path` in .env file.",
            ]
        )
    logger.success("\n" + generate_framed_text(propmt))

    @driver.on_startup
    async def init_webui():
        def version_check(version: str):
            version_file.touch(exist_ok=True)
            if Version(version) <= Version(version_file.read_text() or "0.0.1"):
                logger.info(f"webui is up to date. version:{version}")
                return True
            logger.info(f"webui is outdated. version:{version} > {version_file.read_text()}")
            shutil.rmtree(webui_dir)
            webui_dir.mkdir(parents=True, exist_ok=True)
            return False

        try:
            async with AsyncClient(follow_redirects=True) as client:
                resp = await client.get(
                    "https://api.github.com/repos/wosiwq/nonebot-plugin-bilichat-webui/releases/latest"
                )
                data = resp.json()
                version = data["name"]

                if version_check(version):
                    return

                for assets in data["assets"]:
                    if assets["name"] == "dist.tar.gz":
                        logger.info(f"downloading latest webui from {assets['browser_download_url']}")
                        webui_file: bytes = (await client.get(assets["browser_download_url"])).content
                        assert webui_file
                        break
                else:
                    raise ValueError(
                        "dist.tar.gz not found at https://github.com/wosiwq/nonebot-plugin-bilichat-webui/releases/latest/"
                    )
        except Exception as e:
            if e == ValueError:
                raise
            logger.error(f"faild to connect to github -> {type(e)}: {e}")
            for file in static_dir.glob("webui-*.tar.gz"):
                parts = file.name.split("-")
                if len(parts) > 1 and parts[1].endswith(".tar.gz"):
                    version = parts[1].replace(".tar.gz", "")
                    if version_check(version):
                        return
                    webui_file = file.read_bytes()
                    break
            else:
                raise FileNotFoundError("webui.tar.gz not found in static dir, please check package integrity")
            logger.info("webui download failed, use default webui")

        with gzip.GzipFile(fileobj=BytesIO(webui_file)) as gz:
            with tarfile.open(fileobj=BytesIO(gz.read()), mode="r:") as tar:
                tar.extractall(path=webui_dir)

        for item in webui_dir.joinpath("dist").iterdir():
            new_path = webui_dir / item.name
            shutil.move(str(item), str(new_path))
        webui_dir.joinpath("dist").rmdir()

        version_file.write_text(version)
