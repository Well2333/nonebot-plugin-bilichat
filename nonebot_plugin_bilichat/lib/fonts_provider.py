import asyncio
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import httpx
from loguru import logger
from yarl import URL

from ..config import plugin_config
from .store import data_dir

DEFUALT_DYNAMIC_FONT = "HarmonyOS_Sans_SC_Medium.ttf"


font_path = data_dir.joinpath("font")

font_path.mkdir(parents=True, exist_ok=True)


async def get_font(font: str = DEFUALT_DYNAMIC_FONT):
    logger.debug(f"Loading font: {font}")
    url = URL(font)
    if url.is_absolute():
        if font_path.joinpath(url.name).exists():
            logger.debug(f"Font {url.name} found in local")
            return font_path.joinpath(url.name)
        else:
            logger.warning(
                f"font {font} does not exist, this will take several seconds to minutes to download fonts depend on your network."
            )
            async with httpx.AsyncClient() as client:
                resp = await client.get(font)
                if resp.status_code != 200:
                    raise ConnectionError(f"Font {font} failed to download")
                font_path.joinpath(url.name).write_bytes(resp.content)
                return font_path.joinpath(url.name)
    else:
        if not font_path.joinpath(font).exists():
            raise FileNotFoundError(f"Font {font} does not exist")
        logger.debug(f"Font {font} found in local")
        return font_path.joinpath(font)


def get_font_sync(font: str = DEFUALT_DYNAMIC_FONT):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_font(font))


def font_init():
    font_url = (
        "https://mirrors.bfsu.edu.cn/pypi/web/packages/ad/97/"
        "03cd0a15291c6c193260d97586c4adf37a7277d8ae4507d68566c5757a6a/"
        "bbot_fonts-0.1.1-py3-none-any.whl"
    )
    lock_file = font_path.joinpath(".lock")
    lock_file.touch(exist_ok=True)
    if lock_file.read_text() != font_url:
        logger.warning("font file does not exist. Trying to download")
        font_file = BytesIO()
        with httpx.stream("GET", font_url) as r:
            for chunk in r.iter_bytes():
                font_file.write(chunk)
        with ZipFile(font_file) as z:
            fonts = [i for i in z.filelist if str(i.filename).startswith("bbot_fonts/font/")]
            for font in fonts:
                file_name = Path(font.filename).name
                local_file = font_path.joinpath(file_name)
                if not local_file.exists():
                    logger.debug(local_file)
                    local_file.write_bytes(z.read(font))

        lock_file.write_text(font_url)


font_init()
