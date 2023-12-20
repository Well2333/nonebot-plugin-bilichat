import nonebot
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nonebot.drivers import ReverseDriver
from nonebot.drivers.fastapi import Driver as FastAPIDriver

from ..config import plugin_config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount fastapi app
driver: FastAPIDriver = nonebot.get_driver()  # type: ignore

if not isinstance(driver, ReverseDriver) or not isinstance(driver.server_app, FastAPI):
    raise NotImplementedError("Only FastAPI reverse driver is supported.")

driver.server_app.mount(f"/{plugin_config.bilichat_webui_path}", app, name="bilichat")
