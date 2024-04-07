from contextlib import suppress
from typing import List

from nonebot.adapters import Bot

from ..registries import PlatformTarget, register_list_targets
from ..target import TargetQQGroup, TargetQQPrivate

with suppress(ImportError):
    from nonebot.adapters.red import (  # type: ignore
        Adapter,
    )
    from nonebot.adapters.red import Bot as BotRed  # type: ignore

    adapter_name = Adapter.get_name()

    @register_list_targets(adapter_name)
    async def list_targets(bot: Bot) -> List[PlatformTarget]:
        assert isinstance(bot, BotRed)

        targets = []
        try:
            groups = await bot.get_groups()
        except Exception:
            groups = []
        for group in groups:
            group_id = int(group.groupCode)
            target = TargetQQGroup(group_id=group_id)
            targets.append(target)

        # 获取好友列表
        try:
            users = await bot.get_friends()
        except Exception:
            users = []
        for user in users:
            user_id = int(user.uin)
            target = TargetQQPrivate(user_id=user_id)
            targets.append(target)

        return targets
