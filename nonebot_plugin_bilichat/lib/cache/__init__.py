from nonebot.log import logger

from ...config import plugin_config
from .cache import BaseCache  # noqa: F401

if plugin_config.bilichat_cache_serive == "mongodb":
    from .mongo_cache import MongoCache as Cache  # noqa: F401

    logger.info("Use MongoDB as cache service")
elif plugin_config.bilichat_cache_serive == "json":
    from .json_cache import JSONFileCache as Cache  # noqa: F401

    logger.info("Use JsonFile as cache service")
