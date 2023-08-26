from nonebot.adapters import Bot, Event, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.typing import T_State

from ..adapters import ID_HANDLER
from ..lib.uid_extract import uid_extract
from ..subscribe.manager import SubscriptionSystem, Uploader, User
from .base import bilichat

bili_add_sub = bilichat.command("sub", aliases={"订阅", "关注"})


@bili_add_sub.handle()
async def add_sub(bot: Bot, event: Event, state: T_State, uid: Message = CommandArg()):
    handler = ID_HANDLER.get(bot.adapter.get_name())
    # 获取用户对象
    if not handler:
        await bili_add_sub.finish("暂时还不支持当前平台呢\n`(*>﹏<*)′")
        raise FinishedException
    user_id = await handler(event)
    if not user_id:
        await bili_add_sub.finish("暂时还不支持当前会话呢\n`(*>﹏<*)′")
        raise FinishedException
    user = SubscriptionSystem.users.get(user_id, User(user_id=user_id, platfrom=bot.adapter.get_name()))

    # 获取 UP 对象
    if not uid:
        await bili_add_sub.finish("请输入UP主的昵称或 UID 呢\n`(*>﹏<*)′")
    msg = await uid_extract(uid.extract_plain_text())
    if isinstance(msg, str):
        await bili_add_sub.finish(msg)
        raise FinishedException
    up = SubscriptionSystem.uploaders.get(msg.mid, Uploader(nickname=msg.nickname, uid=msg.mid))

    msg = user.add_subscription(up) or f"已经成功关注 {up} 啦\n(*^▽^*)"
    await bili_add_sub.finish(msg)


bili_remove_sub = bilichat.command("unsub", aliases={"退订", "取关"})


@bili_remove_sub.handle()
async def remove_sub(bot: Bot, event: Event, state: T_State, uid: Message = CommandArg()):
    handler = ID_HANDLER.get(bot.adapter.get_name())
    # 获取用户对象
    if not handler:
        await bili_add_sub.finish("暂时还不支持当前平台呢\n`(*>﹏<*)′")
        raise FinishedException
    user_id = await handler(event)
    if not user_id:
        await bili_add_sub.finish("暂时还不支持当前会话呢\n`(*>﹏<*)′")
        raise FinishedException
    user = SubscriptionSystem.users.get(user_id, User(user_id=user_id, platfrom=bot.adapter.get_name()))

    # 获取 UP 对象
    if not uid:
        await bili_add_sub.finish("请输入UP主的昵称或 UID 呢\n`(*>﹏<*)′")
    msg = await uid_extract(uid.extract_plain_text())
    if isinstance(msg, str):
        await bili_add_sub.finish(msg)
        raise FinishedException
    up = SubscriptionSystem.uploaders.get(msg.mid, Uploader(nickname=msg.nickname, uid=msg.mid))

    msg = user.remove_subscription(up) or f"已经成功取关 {up} 啦\n(*^▽^*)"
    await bili_add_sub.finish(msg)
