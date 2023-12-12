from pathlib import Path

import nonebot
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ..config import plugin_config

app: FastAPI = nonebot.get_app()

app.mount(
    f"/{plugin_config.bilichat_webui_url}/web/",
    StaticFiles(directory=Path(__file__).parent.parent.joinpath("static").joinpath("web"), html=True),
)
