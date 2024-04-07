from contextlib import suppress
from functools import partial
from typing import (
    Awaitable,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
)

from nonebot import logger
from nonebot.adapters import Bot
from nonebot.compat import PYDANTIC_V2, ConfigDict
from nonebot.exception import ActionFailed
from pydantic import BaseModel

from ..registries import register_list_targets
from ..target import (
    PlatformTarget,
    TargetQQGroup,
    TargetQQPrivate,
    TargetSatoriUnknown,
)

with suppress(ImportError):
    from nonebot.adapters.satori import Adapter
    from nonebot.adapters.satori import Bot as BotSatori

    adapter_name = Adapter.get_name()

    T = TypeVar("T")

    if PYDANTIC_V2:

        class PageResult(BaseModel, Generic[T]):  # type: ignore
            data: List[T]
            next: Optional[str] = None

            model_config: ConfigDict = ConfigDict(extra="allow")  # type: ignore

    else:

        from pydantic.generics import GenericModel

        class PageResult(GenericModel, Generic[T]):
            data: List[T]
            next: Optional[str] = None

            class Config:
                extra = "allow"

    class PagedAPI(Generic[T], Protocol):
        def __call__(self, *, next_token: Optional[str] = None) -> Awaitable[PageResult[T]]: ...

    async def _fetch_all(paged_api: PagedAPI[T]) -> List[T]:
        results = []
        # nonebor-adapter-satori < 0.10.2 的 `channel_list` API 会因为 next_token 为 None 而报错
        token = None
        while True:
            resp = await paged_api(next_token=token)
            results.extend(resp.data)
            if resp.next is None:
                logger.debug("No more pages to fetch")
                break
            token = resp.next
            logger.debug(f"Fetching next page with token: {token}")
        return results

    @register_list_targets(adapter_name)
    async def list_targets(bot: Bot) -> List[PlatformTarget]:
        assert isinstance(bot, BotSatori)

        targets = []
        # 获取群组列表
        try:
            guilds = await _fetch_all(bot.guild_list)
            logger.debug(f"Found {len(guilds)} guilds(groups)")
            for guild in guilds:
                logger.debug(f"featching -> {guild}")
                channels = await _fetch_all(partial(bot.channel_list, guild_id=guild.id))
                for channel in channels:
                    if bot.platform in ["qq", "red", "chronocat"]:
                        target = TargetQQGroup(group_id=int(channel.id))
                    else:
                        target = TargetSatoriUnknown(platform=bot.platform, channel_id=channel.id)
                    targets.append(target)
        except ActionFailed as e:  # pragma: no cover
            logger.warning(f"Satori({bot.platform}) does not support fetching channel list: {e}")

        # 获取好友列表
        try:
            users = await _fetch_all(bot.friend_list)
            for user in users:
                if bot.platform in ["qq", "red", "chronocat"]:
                    target = TargetQQPrivate(user_id=int(user.id))
                else:
                    target = TargetSatoriUnknown(platform=bot.platform, user_id=user.id)
                targets.append(target)
        except ActionFailed as e:  # pragma: no cover
            logger.warning(f"Satori({bot.platform}) does not support fetching friend list: {e}")

        return targets
