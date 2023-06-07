from pathlib import Path

from nonebot import require
from nonebot.log import logger

require("nonebot_plugin_localstore")


import nonebot_plugin_localstore as store

cache_dir = store.get_cache_dir("nonebot_plugin_bilichat")
data_dir = store.get_data_dir("nonebot_plugin_bilichat")

logger.info(f"Cache folder for nonebot_plugin_bilichat is located at {cache_dir.absolute()}")
logger.info(f"Data folder for nonebot_plugin_bilichat is located at {data_dir.absolute()}")

BING_APOLOGY = Path(__file__).parent.parent.joinpath("static", "bing_apology.jpg")
