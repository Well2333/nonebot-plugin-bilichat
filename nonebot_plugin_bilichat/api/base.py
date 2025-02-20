import nonebot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nonebot.drivers import ReverseDriver
from nonebot.drivers.fastapi import Driver as FastAPIDriver

driver: FastAPIDriver = nonebot.get_driver()  # type: ignore

if not isinstance(driver, ReverseDriver) or not isinstance(driver.server_app, FastAPI):
    raise NotImplementedError("Only FastAPI reverse driver is supported.")

app = driver.server_app

app.separate_input_output_schemas = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
