from nonebot.adapters import Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER

from ..config import plugin_config
from ..lib.uid_extract import uid_extract
from ..subscribe.manager import SubscriptionSystem, Uploader, User
from .base import bilichat, get_user

bili_add_sub = bilichat.command("sub", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_add_sub))
bili_remove_sub = bilichat.command("unsub", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_remove_sub))
bili_check_sub = bilichat.command("check", aliases=set(plugin_config.bilichat_cmd_check_sub))
bili_at_all = bilichat.command("atall", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_at_all))


@bili_add_sub.handle()
async def add_sub(uid: Message = CommandArg(), user: User = Depends(get_user)):
    # 获取 UP 对象
    if not uid:
        await bili_add_sub.finish("请输入UP主的昵称呢\n`(*>﹏<*)′")
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
    ups_prompt = []
    for index, up in enumerate(ups):
        text = f"{index+1}."
        # at 全体成员
        if user.subscriptions.get(up.uid, {}).get("at_all"):
            text += "📢 "
        text += f"{str(up)}"
        ups_prompt.append(text)

    await bili_check_sub.finish(f"本群共订阅 {len(ups)} 个 UP:\n" + "\n".join(ups_prompt))


@bili_at_all.handle()
async def at_all(
    user: User = Depends(get_user),
    msg: Message = CommandArg(),
):
    keyword = msg.extract_plain_text().lower().strip()
    if keyword in ("全局", "全体", "all"):
        if user.at_all:
            user.at_all = False
            re_msg = "已关闭全局@全体成员了~\n(*^▽^*)"
        else:
            user.at_all = True
            re_msg = "已开启全局@全体成员了~\n(*^▽^*)"
    else:
        for up in SubscriptionSystem.uploaders.values():
            if up.nickname.lower() == keyword or str(up.uid) == keyword:
                cfg = user.subscriptions.get(up.uid, {"at_all": False})
                if cfg["at_all"] is True:
                    cfg["at_all"] = False
                    user.subscriptions.update({up.uid: cfg})
                    re_msg = f"已关闭 {up.nickname}({up.uid}) 的@全体成员了~\n(*^▽^*)"
                else:
                    cfg["at_all"] = True
                    user.subscriptions.update({up.uid: cfg})
                    re_msg = f"已开启 {up.nickname}({up.uid}) 的@全体成员了~\n(*^▽^*)"
        re_msg = "未找到该 UP 主呢\n`(*>﹏<*)′"
    SubscriptionSystem.save_to_file()
    await bili_at_all.finish(re_msg)
