from asyncio import Lock
from typing import TypedDict

from nonebot.adapters import Event, Message
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER
from nonebot_plugin_waiter import waiter

from ..config import plugin_config
from ..lib.uid_extract import uid_extract
from ..subscribe.manager import SubscriptionSystem, Uploader, User
from .base import bilichat, check_lock, get_user


class Request(TypedDict):
    sub: list[Uploader]
    unsub: list[Uploader]


REQUESTS: dict[User, Request] = {}


bili_add_sub_request = bilichat.command("sub", aliases=set(plugin_config.bilichat_cmd_add_sub), priority=2)
bili_remove_sub_request = bilichat.command("unsub", aliases=set(plugin_config.bilichat_cmd_remove_sub), priority=2)
bili_request_handle = bilichat.command("handle", permission=SUPERUSER)


@bili_add_sub_request.handle()
async def add_sub(uid: Message = CommandArg(), user: User = Depends(get_user)):
    reqs = REQUESTS.get(user, {"sub": [], "unsub": []})
    if not uid:
        await bili_add_sub_request.finish("请输入UP主的昵称呢\n`(*>﹏<*)′")
    msg = await uid_extract(uid.extract_plain_text())
    if isinstance(msg, str):
        await bili_add_sub_request.finish(msg)
    up = SubscriptionSystem.uploaders.get(msg.mid, Uploader(nickname=msg.nickname, uid=msg.mid))

    if len(user.subscriptions) > SubscriptionSystem.config.subs_limit:
        await bili_add_sub_request.finish("本群的订阅已经满啦\n删除无用的订阅再试吧\n`(*>﹏<*)′")
    elif up.uid in user.subscriptions:
        await bili_add_sub_request.finish("本群已经订阅了此UP主呢...\n`(*>﹏<*)′")
    elif up in reqs["sub"]:
        await bili_add_sub_request.finish(f"已经申请过添加 {up} 啦，无需再次申请\n(*^▽^*)")

    reqs["sub"].append(up)
    REQUESTS[user] = reqs

    await bili_add_sub_request.finish("已记录此次添加申请，请联系管理员处理\n(*^▽^*)")


@bili_remove_sub_request.handle()
async def remove_sub(msg: Message = CommandArg(), user: User = Depends(get_user)):
    reqs = REQUESTS.get(user, {"sub": [], "unsub": []})
    if not msg:
        await bili_remove_sub_request.finish("请输入UP主的昵称或 UID 呢\n`(*>﹏<*)′")
    keyword = msg.extract_plain_text().lower()
    for up in SubscriptionSystem.uploaders.values():
        if up.nickname.lower() == keyword or str(up.uid) == keyword:
            if up.uid not in user.subscriptions:
                await bili_remove_sub_request.finish("本群并未订阅此UP主呢...\n`(*>﹏<*)′")
            elif up in reqs["unsub"]:
                await bili_remove_sub_request.finish(f"已经申请过移除 {up} 啦，无需再次申请\n(*^▽^*)")

            reqs["unsub"].append(up)
            REQUESTS[user] = reqs
            await bili_remove_sub_request.finish("已记录此次添加申请，请联系管理员处理\n(*^▽^*)")
    await bili_remove_sub_request.finish("未找到该 UP 主呢\n`(*>﹏<*)′")


@bili_request_handle.handle()
async def handle_request(lock: Lock = Depends(check_lock)):
    async with lock:
        if not REQUESTS or not any(bool(reqs["sub"] or reqs["unsub"]) for reqs in REQUESTS.values()):
            await bili_request_handle.finish("没有任何申请记录")
        for user, reqs in REQUESTS.copy().items():
            REQUESTS.pop(user)
            msg = []
            index = 0
            if not reqs["sub"] and not reqs["unsub"]:
                continue
            msg.append(f"{user.user_id}({user.platform})")
            if reqs["sub"]:
                msg.append("  添加:")
                for up in reqs["sub"]:
                    msg.append(f"    {index}. {up.nickname}({up.uid})")
                    index += 1
            if reqs["unsub"]:
                msg.append("  移除:")
                for up in reqs["unsub"]:
                    msg.append(f"    {index}. {up.nickname}({up.uid})")
                    index += 1
            msg.extend(["请输入：", "`y` 同意全部请求", "`n` 拒绝全部请求", "`e` 逐条审查"])
            await bili_request_handle.send("\n".join(msg))

            @waiter(waits=["message"], keep_session=True)
            async def check(event: Event):
                return event.get_plaintext().lower().strip()

            async for resp in check(timeout=120):
                if resp == "y":
                    store: dict[Uploader, str] = {}
                    for up in reqs["sub"]:
                        store[up] = user.add_subscription(up) or f"已添加 {up.nickname}({up.uid})"
                    for up in reqs["unsub"]:
                        store[up] = await user.remove_subscription(up) or f"已移除 {up.nickname}({up.uid})"
                    await bili_request_handle.send(
                        "已同意该用户的全部请求，具体如下：\n"
                        + "\n".join([f"{up.nickname}({up.uid}): {m}" for up, m in store.items()])
                    )
                    break
                elif resp == "n":
                    await bili_request_handle.send("已拒绝该用户的全部请求")
                    break
                elif resp == "e":
                    for up in reqs["sub"]:
                        await bili_request_handle.send(f"是否同意添加 {up.nickname}({up.uid})")

                        async for resp1 in check(timeout=120):
                            if resp1 == "y":
                                await bili_request_handle.send(
                                    user.add_subscription(up) or f"已添加 {up.nickname}({up.uid})"
                                )
                                break
                            elif resp1 == "n":
                                await bili_request_handle.send(f"已拒绝添加 {up.nickname}({up.uid})")
                                break
                            else:
                                await bili_request_handle.send(f"请输入 y 或 n，而不是 {resp1}")
                    for up in reqs["unsub"]:
                        await bili_request_handle.send(f"是否移除 {up.nickname}({up.uid})")

                        async for resp2 in check(timeout=120):
                            if resp2 == "y":
                                await bili_request_handle.send(
                                    await user.remove_subscription(up) or f"已移除 {up.nickname}({up.uid})"
                                )
                                break
                            elif resp2 == "n":
                                await bili_request_handle.send(f"已拒绝移除 {up.nickname}({up.uid})")
                                break
                            else:
                                await bili_request_handle.send(f"请输入 y 或 n，而不是 {resp2}")
                    break
            else:
                await bili_request_handle.send("输入无效，请输入：\n`y` 同意全部请求\n`n` 拒绝全部请求\n`e` 逐条审查")
