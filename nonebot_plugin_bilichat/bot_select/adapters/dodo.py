from contextlib import suppress
from typing import List

from nonebot.adapters import Bot as BaseBot

from ..registries import register_list_targets
from ..target import (
    PlatformTarget,
    TargetDoDoChannel,
)

with suppress(ImportError):
    from nonebot.adapters.dodo import Adapter  # type: ignore
    from nonebot.adapters.dodo import Bot as BotDodo  # type: ignore

    adapter_name = Adapter.get_name()

    @register_list_targets(adapter_name)
    async def list_targets(bot: BaseBot) -> List[PlatformTarget]:
        assert isinstance(bot, BotDodo)
        targets = []
        for island in await bot.get_island_list():
            for channel in await bot.get_channel_list(island_source_id=island.island_source_id):
                targets.append(TargetDoDoChannel(channel_id=channel.channel_id))

        # TODO: 私聊

        return targets
