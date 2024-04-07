from contextlib import suppress
from typing import List

from nonebot.adapters import Bot as BaseBot

from ..registries import PlatformTarget, add_cache, register_list_targets, remove_cache
from ..target import TargetOB12Unknow, TargetQQGroup, TargetQQGuildChannel, TargetQQPrivate, target_changed

with suppress(ImportError):
    from nonebot.adapters.onebot.v12 import (
        Adapter,
        Bot,
        FriendDecreaseEvent,
        FriendIncreaseEvent,
        GroupMemberDecreaseEvent,
        GroupMemberIncreaseEvent,
    )
    from nonebot.adapters.onebot.v12.exception import UnsupportedAction

    adapter_name = Adapter.get_name()

    @register_list_targets(adapter_name)
    async def list_targets(bot: BaseBot) -> List[PlatformTarget]:
        assert isinstance(bot, Bot)

        targets = []
        try:
            friends = await bot.get_friend_list()
            for friend in friends:
                platform = bot.platform
                if platform == "qq":
                    targets.append(TargetQQPrivate(user_id=int(friend["user_id"])))
                elif platform == "qqguild":
                    # FIXME: 怎么获取 src_guild_id 捏？
                    pass
                else:
                    targets.append(
                        TargetOB12Unknow(
                            platform=platform,
                            detail_type="private",
                            user_id=friend["user_id"],
                        )
                    )

        except UnsupportedAction:  # pragma: no cover
            pass

        try:
            groups = await bot.get_group_list()
            for group in groups:
                platform = bot.platform
                if platform == "qq":
                    targets.append(TargetQQGroup(group_id=int(group["group_id"])))
                else:
                    targets.append(
                        TargetOB12Unknow(
                            platform=platform,
                            detail_type="group",
                            group_id=group["group_id"],
                        )
                    )

        except UnsupportedAction:  # pragma: no cover
            pass

        try:
            guilds = await bot.get_guild_list()
            for guild in guilds:
                channels = await bot.get_channel_list(guild_id=guild["guild_id"])
                for channel in channels:
                    platform = bot.platform
                    if platform == "qqguild":
                        targets.append(TargetQQGuildChannel(channel_id=int(channel["channel_id"])))
                    else:
                        targets.append(
                            TargetOB12Unknow(
                                platform=platform,
                                detail_type="channel",
                                channel_id=channel["channel_id"],
                                guild_id=guild["guild_id"],
                            )
                        )

        except UnsupportedAction:  # pragma: no cover
            pass

        return targets

    @target_changed.handle()
    async def _(bot: BaseBot, event: GroupMemberIncreaseEvent):
        if event.user_id == bot.self_id:
            await add_cache(bot, TargetQQGroup(group_id=int(event.group_id)))

    @target_changed.handle()
    async def _(bot: BaseBot, event: GroupMemberDecreaseEvent):
        if event.user_id == bot.self_id:
            await remove_cache(bot, TargetQQGroup(group_id=int(event.group_id)))

    @target_changed.handle()
    async def _(bot: BaseBot, event: FriendIncreaseEvent):
        await add_cache(bot, TargetQQPrivate(user_id=int(event.user_id)))

    @target_changed.handle()
    async def _(bot: BaseBot, event: FriendDecreaseEvent):
        await remove_cache(bot, TargetQQPrivate(user_id=int(event.user_id)))

