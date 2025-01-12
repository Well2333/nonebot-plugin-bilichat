import json
from importlib.metadata import version
from pathlib import Path
from shutil import copyfile

import yaml
from nonebot import get_driver, require
from nonebot.log import logger

from .model.config import Config

__version__ = version("nonebot_plugin_bilichat")


require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store  # noqa: E402

CACHE_DIR = store.get_cache_dir("nonebot_plugin_bilichat")
DATA_DIR = store.get_data_dir("nonebot_plugin_bilichat")
CONFIG_DIR = store.get_config_dir("nonebot_plugin_bilichat")
STATIC_DIR = Path(__file__).parent.joinpath("static")

logger.info(f"nonebot_plugin_bilichat 缓存文件夹 ->  {CACHE_DIR.absolute()}")
logger.info(f"nonebot_plugin_bilichat 数据文件夹 ->  {DATA_DIR.absolute()}")


nonebot_config = get_driver().config
try:
    config_path = Path(nonebot_config.bilichat_config_path)
except Exception as e:
    config_path = CONFIG_DIR.joinpath("config.yaml")
    logger.warning(f"用户未设置配置文件路径, 尝试默认配置文件路径 {config_path}")

if not config_path.exists():
    logger.error(f"默认配置文件路径 {config_path} 不存在, 已在该位置创建默认配置文件, 请修改配置后重新加载插件")
    copyfile(STATIC_DIR.joinpath("config.yaml"), config_path)
    raise SystemExit


def save_config():
    config_path.write_text(yaml.dump(json.loads(config.model_dump_json()), allow_unicode=True), encoding="utf-8")  # type: ignore


config: Config = Config.model_validate(yaml.safe_load(config_path.read_text(encoding="utf-8")))
save_config()
