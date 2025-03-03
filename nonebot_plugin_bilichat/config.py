from importlib.metadata import version
from pathlib import Path
from shutil import copyfile

import yaml
from deepdiff.diff import DeepDiff
from nonebot import get_driver, require
from nonebot.log import logger

from .migrate import migrate
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
    logger.error(f"默认配置文件路径 {config_path} 不存在, 已在该位置创建默认配置文件")
    for _ in range(5):
        logger.warning("Bilichat 将会以默认配置启动, 如需修改可通过 webui 修改或修改配置文件后重新启动")
    copyfile(STATIC_DIR.joinpath("config.yaml"), config_path)


class ConfigCTX:
    _config = Config()

    @classmethod
    def get(cls) -> Config:
        return cls._config

    @classmethod
    def set(cls, cfg: Config | None = None, *, diff_msg: bool = True) -> None:
        cls._config = cfg or cls._config
        old_cfg = cls._load_config_file()

        if diff_msg and (cfg_diff := DeepDiff(old_cfg, cls._config, ignore_order=True, threshold_to_diff_deeper=0)):
            if "values_changed" in cfg_diff:
                for diff_path, diff_info in cfg_diff["values_changed"].items():
                    logger.info(f"[⚙️] 修改配置项 {diff_path}: {diff_info['old_value']} --> {diff_info['new_value']}")
            if "dictionary_item_added" in cfg_diff:
                for diff_path in cfg_diff["dictionary_item_added"]:
                    logger.info(f"[🎉] 新增配置项: {diff_path}")
            if "dictionary_item_removed" in cfg_diff:
                for diff_path in cfg_diff["dictionary_item_removed"]:
                    logger.info(f"[♻️] 移除配置项: {diff_path}")
            logger.info("配置已更新, 保存配置文件")
            config_path.write_text(
                yaml.dump(cls._config.model_dump(mode="json"), indent=4, allow_unicode=True), encoding="utf-8"
            )
        else:
            logger.info("配置未发生变化")

    @staticmethod
    def _load_config_file() -> Config:
        return Config.model_validate(migrate(yaml.safe_load(config_path.read_text(encoding="utf-8"))))


ConfigCTX.set(ConfigCTX._load_config_file(), diff_msg=False)
