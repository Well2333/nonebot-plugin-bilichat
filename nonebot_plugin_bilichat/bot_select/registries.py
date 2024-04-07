import asyncio
import json
from typing import Awaitable, Callable, Dict, List, Set

from nonebot import logger
from nonebot.adapters import Bot
from nonebot.compat import model_dump

from .target import PlatformTarget

BOT_CACHE: Dict[Bot, Set[PlatformTarget]] = dict()
BOT_CACHE_LOCK = asyncio.Lock()

ListTargetsFunc = Callable[[Bot], Awaitable[List[PlatformTarget]]]

list_targets_map: Dict[str, ListTargetsFunc] = {}


def register_list_targets(adapter: str):
    def wrapper(func: ListTargetsFunc):
        list_targets_map[adapter] = func
        return func

    return wrapper


async def add_cache(bot: Bot, target: PlatformTarget):
    async with BOT_CACHE_LOCK:
        BOT_CACHE[bot].add(target)
    info_current()


async def remove_cache(bot: Bot, target: PlatformTarget):
    async with BOT_CACHE_LOCK:
        BOT_CACHE[bot].remove(target)
    info_current()


async def refresh_bot(bot: Bot):
    BOT_CACHE.pop(bot, None)
    adapter_name = bot.adapter.get_name()
    print(adapter_name)
    print(list_targets_map)
    if list_targets := list_targets_map.get(adapter_name):
        try:
            logger.debug(f"executing list targets {list_targets} of adapter {adapter_name}")
            targets = await list_targets(bot)
            BOT_CACHE[bot] = set(targets)
        except Exception:
            logger.exception(f"{bot} get list targets failed")
    else:
        logger.warning(f"no available list targets function for adapter {adapter_name}")
    info_current()


def info_current():
    log_info = {}
    for bot, platform_target_set in BOT_CACHE.items():
        log_info[str(bot)] = [model_dump(target) for target in platform_target_set]
    logger.trace(f"current bot-platform_target: {json.dumps(log_info)}")
