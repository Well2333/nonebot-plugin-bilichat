
from nonebot.adapters.qq import (
    Bot,
    ChannelDeleteEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.params import CommandArg

from ...commands.base import bili_check_dyn, leave_group
from ...config import plugin_config
from ...lib.fetch_dynamic import fetch_last_dynamic
from ...lib.uid_extract import uid_extract
from ...subscribe.manager import SubscriptionSystem


@bili_check_dyn.handle()
async def check_dynamic_v11(bot: Bot, event: MessageEvent, uid: Message = CommandArg()):
    # 获取 UP 对象
    if not uid:
        await bili_check_dyn.finish("请输入UP主的昵称呢\n`(*>﹏<*)′")
    up = await uid_extract(uid.extract_plain_text())
    if isinstance(up, str):
        await bili_check_dyn.finish(up)
        raise FinishedException
    if dyn := await fetch_last_dynamic(up):
        if image := await dyn.get_image(plugin_config.bilichat_dynamic_style):
            await bili_check_dyn.finish(MessageSegment.file_image(image))


@leave_group.handle()
async def remove_sub_qqguild(event: ChannelDeleteEvent):
    if not event.is_tome():
        return
    logger.info(f"remove subs from {event.id}")
    if user := SubscriptionSystem.users.get("QQGuildOfficial-_-" + str(event.id)):
        for up in user.subscribe_ups:
            await user.remove_subscription(up)
    SubscriptionSystem.save_to_file()
