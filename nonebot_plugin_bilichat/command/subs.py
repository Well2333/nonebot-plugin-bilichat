from asyncio import Lock

from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER
from nonebot_plugin_uninfo.permission import ADMIN

from nonebot_plugin_bilichat.model.subscribe import UserInfo
from nonebot_plugin_bilichat.request_api import RequestAPI
from nonebot_plugin_bilichat.subscribe.status import SubsStatus, UPStatus

from ..config import ConfigCTX
from .base import bilichat, check_lock, get_api, get_user

bili_add_sub = bilichat.command("sub", permission=ADMIN() | SUPERUSER, aliases=set(ConfigCTX.get().nonebot.cmd_add_sub))
bili_remove_sub = bilichat.command(
    "unsub", permission=ADMIN() | SUPERUSER, aliases=set(ConfigCTX.get().nonebot.cmd_remove_sub)
)
bili_check_sub = bilichat.command("check", aliases=set(ConfigCTX.get().nonebot.cmd_check_sub))


@bili_add_sub.handle()
async def add_sub(
    user: UserInfo = Depends(get_user),
    msg: Message = CommandArg(),
    lock: Lock = Depends(check_lock),
    api: RequestAPI = Depends(get_api),
):
    async with lock:
        # 获取 UP 对象
        if not msg:
            await bili_add_sub.finish("请输入UP主的昵称")
        up = await api.tools_search_up(msg.extract_plain_text())
        if not up:
            await bili_add_sub.finish(f"未找到 UP {msg.extract_plain_text()}")
        elif isinstance(up, list):
            upstr = "\n".join([str(u) for u in up])
            await bili_add_sub.finish(f"未找到 UP {msg.extract_plain_text()}, 猜你想找: \n{upstr}")
        # 添加订阅
        user.add_subscription(uid=up.uid, uname=up.nickname)
        config = ConfigCTX.get()
        config.subs.users_dict[user.id] = user
        ConfigCTX.set()
        if up.uid not in SubsStatus.online_ups_cache:
            SubsStatus.online_ups_cache[up.uid] = UPStatus(uid=up.uid, name=up.nickname)
    await bili_add_sub.finish(f"已经成功订阅 UP {up.nickname}({up.uid})")


@bili_remove_sub.handle()
async def remove_sub(user: UserInfo = Depends(get_user), msg: Message = CommandArg(), lock: Lock = Depends(check_lock)):
    async with lock:
        # 获取 UP 对象
        if not msg:
            await bili_add_sub.finish("请输入 UP 主的昵称或 UID")
        config = ConfigCTX.get()
        keyword = msg.extract_plain_text().strip()
        logger.info(f"keyword: {keyword}")
        if keyword in ["all", "全部"]:
            user.subscribes_dict.clear()
            config.subs.users_dict[user.id] = user
            ConfigCTX.set()
            await bili_add_sub.finish("已经成功取关本会话订阅的全部 UP 主")
        for up in user.subscribes_dict.values():
            if keyword in (up.uname, up.nickname) or str(up.uid) == keyword.lower().replace("uid:", "").strip():
                user.subscribes_dict.pop(up.uid)
                config.subs.users_dict[user.id] = user
                ConfigCTX.set()
                await bili_add_sub.finish(f"已经成功取关 UP {up.nickname or up.uname}({up.uid})")
        await bili_add_sub.finish("未找到该 UP 主")


@bili_check_sub.handle()
async def check_sub(user: UserInfo = Depends(get_user), lock: Lock = Depends(check_lock)):
    async with lock:
        if not user.subscribes_dict:
            await bili_check_sub.finish("本会话并未订阅任何UP主")
        # 查看本会话的订阅
        ups = user.subscribes_dict.values()
        ups_prompt = []
        for index, up in enumerate(ups):
            text = f"{index+1}."
            text += f" {up.nickname or up.uname}({up.uid})"
            ups_prompt.append(text)
        re_msg = f"ID:{user.id}\n共订阅 {len(ups)} 个 UP:\n" + "\n".join(ups_prompt)
        await bili_check_sub.finish(re_msg)
