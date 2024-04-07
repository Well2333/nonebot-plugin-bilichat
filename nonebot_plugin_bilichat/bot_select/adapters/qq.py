from contextlib import suppress
from typing import List

from nonebot.adapters import Bot as BaseBot

from ..registries import PlatformTarget, register_list_targets
from ..target import TargetQQGuildChannel

with suppress(ImportError):
    from nonebot.adapters.qq import Adapter, Bot

    adapter_name = Adapter.get_name()

    @register_list_targets(adapter_name)
    async def list_targets(bot: BaseBot) -> List[PlatformTarget]:
        assert isinstance(bot, Bot)

        targets = []

        # TODO: 私聊

        guilds = await bot.guilds()
        for guild in guilds:
            channels = await bot.get_channels(guild_id=guild.id)
            for channel in channels:
                targets.append(
                    TargetQQGuildChannel(
                        channel_id=int(channel.id),
                    )
                )

        return targets
