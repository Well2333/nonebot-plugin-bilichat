from asyncio import Lock

from nonebot.adapters import Message
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER

from ..config import plugin_config
from ..subscribe.manager import SubscriptionSystem, User, UserSubConfig
from .base import bilichat, check_lock, get_user

bili_at_all = bilichat.command("atall", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_at_all))
bili_dynamic = bilichat.command("dynamic", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_dynamic))
bili_live = bilichat.command("live", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_live))


@bili_at_all.handle()
async def at_all(user: User = Depends(get_user), msg: Message = CommandArg(), lock: Lock = Depends(check_lock)):
    async with lock:
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
                if up.nickname.lower() in keyword or str(up.uid) in keyword:
                    cfg = user.subscriptions.get(up.uid, UserSubConfig(uid=up.uid))
                    if "动态" in keyword or "dynamic" in keyword:
                        cfg.dynamic_at_all = not cfg.dynamic_at_all
                        user.subscriptions.update({up.uid: cfg})
                        if cfg.dynamic_at_all:
                            re_msg = f"已开启 {up.nickname}({up.uid}) 的动态@全体成员了~\n(*^▽^*)"
                        else:
                            re_msg = f"已关闭 {up.nickname}({up.uid}) 的动态@全体成员了~\n(*^▽^*)"
                    elif "直播" in keyword or "live" in keyword:
                        cfg.live_at_all = not cfg.live_at_all
                        user.subscriptions.update({up.uid: cfg})
                        if cfg.live_at_all:
                            re_msg = f"已开启 {up.nickname}({up.uid}) 的直播@全体成员了~\n(*^▽^*)"
                        else:
                            re_msg = f"已关闭 {up.nickname}({up.uid}) 的直播@全体成员了~\n(*^▽^*)"
                    else:
                        await bili_at_all.finish("请输入你想开启(关闭)的是 `直播` 或 `动态` 呢\n`(*>﹏<*)′")
        SubscriptionSystem.save_to_file()
        await bili_at_all.finish(re_msg)


@bili_dynamic.handle()
async def dynamic(user: User = Depends(get_user), msg: Message = CommandArg(), lock: Lock = Depends(check_lock)):
    async with lock:
        keyword = msg.extract_plain_text().lower().strip()
        re_msg = "未找到该 UP 主呢\n`(*>﹏<*)′"
        for up in SubscriptionSystem.uploaders.values():
            if up.nickname.lower() == keyword or str(up.uid) == keyword:
                cfg = user.subscriptions.get(up.uid, UserSubConfig(uid=up.uid))
                if cfg.dynamic is True:
                    cfg.dynamic = False
                    user.subscriptions.update(
                        {
                            up.uid: cfg,  # type: ignore
                        }
                    )
                    re_msg = f"已关闭 {up.nickname}({up.uid}) 的动态通知了~\n(*^▽^*)"
                else:
                    cfg.dynamic = True
                    user.subscriptions.update({up.uid: cfg})  # type: ignore
                    re_msg = f"已开启 {up.nickname}({up.uid}) 的动态通知了~\n(*^▽^*)"
        SubscriptionSystem.save_to_file()
        await bili_dynamic.finish(re_msg)


@bili_live.handle()
async def live(user: User = Depends(get_user), msg: Message = CommandArg(), lock: Lock = Depends(check_lock)):
    async with lock:
        keyword = msg.extract_plain_text().lower().strip()
        re_msg = "未找到该 UP 主呢\n`(*>﹏<*)′"
        for up in SubscriptionSystem.uploaders.values():
            if up.nickname.lower() == keyword or str(up.uid) == keyword:
                cfg = user.subscriptions.get(up.uid, UserSubConfig(uid=up.uid))
                if cfg.live is True:
                    cfg.live = False
                    user.subscriptions.update(
                        {
                            up.uid: cfg,  # type: ignore
                        }
                    )
                    re_msg = f"已关闭 {up.nickname}({up.uid}) 的直播通知了~\n(*^▽^*)"
                else:
                    cfg.live = True
                    user.subscriptions.update({up.uid: cfg})  # type: ignore
                    re_msg = f"已开启 {up.nickname}({up.uid}) 的直播通知了~\n(*^▽^*)"
        SubscriptionSystem.save_to_file()
        await bili_live.finish(re_msg)
