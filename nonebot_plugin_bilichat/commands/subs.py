from typing import Optional

from nonebot.adapters import Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER

from ..config import plugin_config
from ..lib.uid_extract import uid_extract
from ..subscribe import LOCK
from ..subscribe.manager import DEFUALT_SUB_CONFIG, SubscriptionSystem, Uploader, User
from .base import bilichat, get_user

bili_add_sub = bilichat.command("sub", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_add_sub))
bili_remove_sub = bilichat.command("unsub", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_remove_sub))
bili_check_sub = bilichat.command("check", aliases=set(plugin_config.bilichat_cmd_check_sub))
bili_reset_sub = bilichat.command("reset", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_reset_sub))


@bili_add_sub.handle()
async def add_sub(uid: Message = CommandArg(), user: User = Depends(get_user)):
    async with LOCK:
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
    async with LOCK:
        # 获取 UP 对象
        if not msg:
            await bili_add_sub.finish("请输入UP主的昵称或 UID 呢\n`(*>﹏<*)′")
        keyword = msg.extract_plain_text().lower()
        if keyword in ["all", "全部"]:
            for up in SubscriptionSystem.uploaders.copy().values():
                await user.remove_subscription(up)
            await bili_add_sub.finish("已经成功取关本群订阅的全部UP主啦\n(*^▽^*)")
        for up in SubscriptionSystem.uploaders.values():
            if up.nickname.lower() == keyword or str(up.uid) == keyword:
                re_msg = await user.remove_subscription(up) or f"已经成功取关 {up} 啦\n(*^▽^*)"
                await bili_add_sub.finish(re_msg)
        await bili_add_sub.finish("未找到该 UP 主呢\n`(*>﹏<*)′")


@bili_check_sub.handle()
async def check_sub(
    user: User = Depends(get_user),
    msg: Optional[Message] = CommandArg(),
):
    async with LOCK:
        if not user.subscriptions:
            await bili_check_sub.finish("本群并未订阅任何UP主呢...\n`(*>﹏<*)′")
        # 查看本群的订阅
        if not msg:
            ups = user.subscribe_ups
            ups_prompt = []
            for index, up in enumerate(ups):
                text = f"{index+1}."
                cfg = DEFUALT_SUB_CONFIG.copy()
                cfg.update(user.subscriptions.get(up.uid, {}))  # type: ignore
                if cfg != DEFUALT_SUB_CONFIG:
                    text += "⚙️"
                text += f" {str(up)}"
                ups_prompt.append(text)
            re_msg = f"本群ID:{user.user_id}\n共订阅 {len(ups)} 个 UP:\n" + "\n".join(ups_prompt)
        # 查看指定 UP 主的配置
        else:
            re_msg = "未找到该 UP 主呢\n`(*>﹏<*)′"
            keyword = msg.extract_plain_text().lower().strip()
            for up in user.subscribe_ups:
                if up.nickname.lower() == keyword or str(up.uid) == keyword:
                    prompt = [str(up)]
                    cfg = user.subscriptions.get(up.uid, {})
                    prompt.append(f"📢 @ 全员(动态) - {cfg.get('dynamic_at_all',False)}")
                    prompt.append(f"📢 @ 全员(直播) - {cfg.get('live_at_all',False)}")
                    prompt.append(f"💬 动态推送 - {cfg.get('dynamic',True)}")
                    prompt.append(f"📺 直播推送 - {cfg.get('live',True)}")
                    re_msg = "\n".join(prompt)
                    break
        await bili_check_sub.finish(re_msg)


@bili_reset_sub.handle()
async def reset_sub(
    user: User = Depends(get_user),
    msg: Optional[Message] = CommandArg(),
):
    async with LOCK:
        if not msg:
            await bili_reset_sub.finish("请输入UP主的昵称或 UID 呢\n`(*>﹏<*)′")
        keyword = msg.extract_plain_text().lower()
        if keyword in ["all", "全部"]:
            for sub in user.subscriptions:
                user.subscriptions[sub] = DEFUALT_SUB_CONFIG.copy()
            SubscriptionSystem.save_to_file()
            await bili_reset_sub.finish("已经成功重置本群订阅的全部UP主的推送配置啦\n(*^▽^*)")
        for up in SubscriptionSystem.uploaders.values():
            if up.nickname.lower() == keyword or str(up.uid) == keyword:
                user.subscriptions[up.uid] = DEFUALT_SUB_CONFIG.copy()
                SubscriptionSystem.save_to_file()
                await bili_reset_sub.finish(f"已经成功重置 {up} 的推送配置啦\n(*^▽^*)")
        await bili_reset_sub.finish("未找到该 UP 主呢\n`(*>﹏<*)′")
