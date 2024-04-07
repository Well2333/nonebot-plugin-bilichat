from contextlib import suppress
from typing import List

from nonebot.adapters import Bot as BaseBot

from ..registries import register_list_targets
from ..target import (
    PlatformTarget,
    TargetKaiheilaChannel,
    TargetKaiheilaPrivate,
)

with suppress(ImportError):
    from nonebot.adapters.kaiheila import Adapter, Bot  # type: ignore
    from nonebot.adapters.kaiheila.api import (  # type: ignore
        Channel,
        Guild,
        UserChat,
    )

    adapter_name = Adapter.get_name()

    def _unwrap_paging_api(field: str):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                while True:
                    for x in getattr(result, field):
                        yield x

                    if result.meta.page != result.meta.page_total:
                        result = await func(*args, **kwargs, page=result.meta.page + 1)
                    else:
                        break

            return wrapper

        return decorator

    @register_list_targets(adapter_name)
    async def list_targets(bot: BaseBot) -> List[PlatformTarget]:
        assert isinstance(bot, Bot)

        targets = []

        async for guild in _unwrap_paging_api("guilds")(bot.guild_list)():
            guild: Guild
            async for channel in _unwrap_paging_api("channels")(bot.channel_list)(guild_id=guild.id_):
                assert isinstance(channel, Channel)
                assert channel.id_
                target = TargetKaiheilaChannel(channel_id=channel.id_)
                targets.append(target)

        async for user_chat in _unwrap_paging_api("user_chats")(bot.userChat_list)():
            user_chat: UserChat
            assert user_chat.target_info and user_chat.target_info.id_
            target = TargetKaiheilaPrivate(user_id=user_chat.target_info.id_)
            targets.append(target)

        return targets
