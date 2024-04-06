from pathlib import Path

from nonebot import require
from nonebot.log import logger

require("nonebot_plugin_localstore")


import nonebot_plugin_localstore as store  # noqa: E402

cache_dir = store.get_cache_dir("nonebot_plugin_bilichat")
data_dir = store.get_data_dir("nonebot_plugin_bilichat")
static_dir = Path(__file__).parent.parent.joinpath("static")

logger.info(f"nonebot_plugin_bilichat 缓存文件夹 ->  {cache_dir.absolute()}")
logger.info(f"nonebot_plugin_bilichat 数据文件夹 ->  {data_dir.absolute()}")
