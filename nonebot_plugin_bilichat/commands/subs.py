from nonebot.adapters import Bot, Event, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg, Depends
from nonebot.typing import T_State

from ..lib.uid_extract import uid_extract
from ..subscribe.manager import SubscriptionSystem, Uploader, User
from .base import bilichat, get_user

bili_add_sub = bilichat.command("sub", aliases={"订阅", "关注"})
bili_remove_sub = bilichat.command("unsub", aliases={"退订", "取关"})
bili_check_sub = bilichat.command("check", aliases={"查看", "查看订阅"})


@bili_add_sub.handle()
async def add_sub(uid: Message = CommandArg(), user: User = Depends(get_user)):
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


@bili_remove_sub.handle()
async def remove_sub(msg: Message = CommandArg(), user: User = Depends(get_user)):
    # 获取 UP 对象
    if not msg:
        await bili_add_sub.finish("请输入UP主的昵称或 UID 呢\n`(*>﹏<*)′")
    keyword = msg.extract_plain_text().lower()
    for up in SubscriptionSystem.uploaders.values():
        if up.nickname.lower() == keyword or str(up.uid) == keyword:
            re_msg = user.remove_subscription(up) or f"已经成功取关 {up} 啦\n(*^▽^*)"
            await bili_add_sub.finish(re_msg)
    await bili_add_sub.finish("未找到该 UP 主呢\n`(*>﹏<*)′")


@bili_check_sub.handle()
async def check_sub(user: User = Depends(get_user)):
    if not user.subscriptions:
        await bili_check_sub.finish("本群并未订阅任何UP主呢...\n`(*>﹏<*)′")
    ups = user.subscribe_ups
    await bili_check_sub.finish(
        f"本群共订阅 {len(ups)} 个 UP:\n" + "\n".join([f"{index+1}. {str(up)}" for index, up in enumerate(ups)])
    )
