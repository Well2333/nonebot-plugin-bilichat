from importlib.metadata import version
from pathlib import Path
from shutil import copyfile

import yaml
from deepdiff.diff import DeepDiff
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
    logger.info(f"用户未设置配置文件路径, 尝试默认配置文件路径 {config_path}")

if not config_path.exists():
    logger.error(f"默认配置文件路径 {config_path} 不存在, 已在该位置创建默认配置文件, 请修改配置后重新加载插件")
    copyfile(STATIC_DIR.joinpath("config.yaml"), config_path)
    raise SystemExit


class ConfigCTX:
    _config = Config()

    @classmethod
    def get(cls) -> Config:
        return cls._config

    @classmethod
    def set(cls, cfg: Config | None = None, *, diff_msg: bool = True) -> None:
        cls._config = cfg or cls._config
        old_cfg = cls._load_config_file()
        if cfg_diff := DeepDiff(cls._config, old_cfg, ignore_order=True).get("values_changed", {}):
            if diff_msg:
                for k, v in cfg_diff.items():
                    logger.info(f"{k}: " + str(v["new_value"]) + " -> " + str(v["old_value"]))
            logger.info("配置已更新, 保存配置文件")
            config_path.write_text(
                yaml.dump(cls._config.model_dump(mode="json"), indent=4, allow_unicode=True), encoding="utf-8"
            )  # type: ignore
        else:
            logger.info("配置未发生变化")

    @staticmethod
    def _load_config_file() -> Config:
        return Config.model_validate(yaml.safe_load(config_path.read_text(encoding="utf-8")))


ConfigCTX.set(ConfigCTX._load_config_file(), diff_msg=False)
