from contextlib import suppress
from typing import List

from nonebot.adapters import Bot

from ..registries import PlatformTarget, add_cache, register_list_targets, remove_cache
from ..target import TargetQQGroup, TargetQQPrivate, target_changed

with suppress(ImportError):
    from nonebot.adapters.onebot.v11 import (
        Adapter,
        FriendAddNoticeEvent,
        GroupDecreaseNoticeEvent,
        GroupIncreaseNoticeEvent,
    )
    from nonebot.adapters.onebot.v11 import Bot as BotOB11

    adapter_name = Adapter.get_name()

    @register_list_targets(adapter_name)
    async def list_targets(bot: Bot) -> List[PlatformTarget]:
        assert isinstance(bot, BotOB11)

        targets = []
        try:
            groups = await bot.get_group_list()
        except Exception:
            groups = []

        for group in groups:
            group_id = group["group_id"]
            target = TargetQQGroup(group_id=group_id)
            targets.append(target)

        # 获取好友列表
        try:
            users = await bot.get_friend_list()
        except Exception:
            users = []

        for user in users:
            user_id = user["user_id"]
            target = TargetQQPrivate(user_id=user_id)
            targets.append(target)

        return targets

    @target_changed.handle()
    async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
        if event.is_tome():
            await remove_cache(bot, TargetQQGroup(group_id=event.group_id))

    @target_changed.handle()
    async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
        if event.is_tome():
            await add_cache(bot, TargetQQGroup(group_id=event.group_id))

    @target_changed.handle()
    async def _(bot: Bot, event: FriendAddNoticeEvent):
        await add_cache(bot, TargetQQPrivate(user_id=event.user_id))
