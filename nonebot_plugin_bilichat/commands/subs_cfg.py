from nonebot.adapters import Message
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER

from ..config import plugin_config
from ..subscribe.manager import DEFUALT_SUB_CONFIG, SubscriptionSystem, User
from .base import bilichat, get_user

bili_at_all = bilichat.command("atall", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_at_all))
bili_dynamic = bilichat.command("dynamic", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_dynamic))
bili_live = bilichat.command("live", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_live))


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
        re_msg = "未找到该 UP 主呢\n`(*>﹏<*)′"
        for up in SubscriptionSystem.uploaders.values():
            if up.nickname.lower() == keyword or str(up.uid) == keyword:
                cfg = user.subscriptions.get(up.uid, DEFUALT_SUB_CONFIG.copy())
                if cfg.get("at_all") is True:
                    cfg["at_all"] = False
                    user.subscriptions.update(
                        {
                            up.uid: cfg,  # type: ignore
                        }
                    )
                    re_msg = f"已关闭 {up.nickname}({up.uid}) 的@全体成员了~\n(*^▽^*)"
                else:
                    cfg["at_all"] = True
                    user.subscriptions.update({up.uid: cfg})  # type: ignore
                    re_msg = f"已开启 {up.nickname}({up.uid}) 的@全体成员了~\n(*^▽^*)"
    SubscriptionSystem.save_to_file()
    await bili_at_all.finish(re_msg)


@bili_dynamic.handle()
async def dynamic(
    user: User = Depends(get_user),
    msg: Message = CommandArg(),
):
    keyword = msg.extract_plain_text().lower().strip()
    re_msg = "未找到该 UP 主呢\n`(*>﹏<*)′"
    for up in SubscriptionSystem.uploaders.values():
        if up.nickname.lower() == keyword or str(up.uid) == keyword:
            cfg = user.subscriptions.get(up.uid, DEFUALT_SUB_CONFIG.copy())
            if cfg.get("dynamic", True) is True:
                cfg["dynamic"] = False
                user.subscriptions.update(
                    {
                        up.uid: cfg,  # type: ignore
                    }
                )
                re_msg = f"已关闭 {up.nickname}({up.uid}) 的动态通知了~\n(*^▽^*)"
            else:
                cfg["dynamic"] = True
                user.subscriptions.update({up.uid: cfg})  # type: ignore
                re_msg = f"已开启 {up.nickname}({up.uid}) 的动态通知了~\n(*^▽^*)"
    SubscriptionSystem.save_to_file()
    await bili_dynamic.finish(re_msg)


@bili_live.handle()
async def live(
    user: User = Depends(get_user),
    msg: Message = CommandArg(),
):
    keyword = msg.extract_plain_text().lower().strip()
    re_msg = "未找到该 UP 主呢\n`(*>﹏<*)′"
    for up in SubscriptionSystem.uploaders.values():
        if up.nickname.lower() == keyword or str(up.uid) == keyword:
            cfg = user.subscriptions.get(up.uid, DEFUALT_SUB_CONFIG.copy())
            if cfg.get("live", True) is True:
                cfg["live"] = False
                user.subscriptions.update(
                    {
                        up.uid: cfg,  # type: ignore
                    }
                )
                re_msg = f"已关闭 {up.nickname}({up.uid}) 的直播通知了~\n(*^▽^*)"
            else:
                cfg["live"] = True
                user.subscriptions.update({up.uid: cfg})  # type: ignore
                re_msg = f"已开启 {up.nickname}({up.uid}) 的直播通知了~\n(*^▽^*)"
    SubscriptionSystem.save_to_file()
    await bili_live.finish(re_msg)
