import base64
import json
from typing import Union

from bilireq.login import Login
from nonebot.adapters.mirai2 import Bot
from nonebot.adapters.mirai2.event import BotLeaveEventActive, BotLeaveEventDisband, BotLeaveEventKick, MessageEvent
from nonebot.adapters.mirai2.message import MessageChain, MessageSegment
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.params import CommandArg

from ...commands.base import bili_check_dyn, leave_group
from ...commands.login import bili_login_qrcode
from ...config import plugin_config
from ...lib.bilibili_request.auth import bili_grpc_auth, gRPC_Auth
from ...lib.fetch_dynamic import fetch_last_dynamic
from ...lib.uid_extract import uid_extract
from ...subscribe import LOCK
from ...subscribe.manager import SubscriptionSystem


@bili_check_dyn.handle()
async def check_dynamic_mirai(bot: Bot, uid: MessageChain = CommandArg()):
    # 获取 UP 对象
    if not uid:
        await bili_check_dyn.finish("请输入UP主的昵称呢\n`(*>﹏<*)′")
    up = await uid_extract(uid.extract_plain_text())
    if isinstance(up, str):
        await bili_check_dyn.finish(up)
        raise FinishedException
    if dyn := await fetch_last_dynamic(up):
        if image := await dyn.get_image(plugin_config.bilichat_dynamic_style):
            await bili_check_dyn.finish(MessageSegment.image(base64=base64.b64encode(image).decode("utf-8")))


@leave_group.handle()
async def remove_sub_mirai2(event: Union[BotLeaveEventKick, BotLeaveEventDisband, BotLeaveEventActive]):
    logger.info(f"remove subs from {event.group.id}")
    async with LOCK:
        if user := SubscriptionSystem.users.get("mirai2-_-" + str(event.group.id)):
            for up in user.subscribe_ups:
                await user.remove_subscription(up)
        SubscriptionSystem.save_to_file()


@bili_login_qrcode.handle()
async def bili_qrcode_login_mirai2(event: MessageEvent):
    login = Login()
    qr_url = await login.get_qrcode_url()
    logger.debug(f"qrcode login url: {qr_url}")
    data = "base64://" + await login.get_qrcode(qr_url, base64=True)  # type: ignore
    await bili_login_qrcode.send(MessageSegment.image(base64=data))
    try:
        gRPC_Auth.update(await login.qrcode_login(interval=5))  # type: ignore
        logger.debug(gRPC_Auth.data)
        bili_grpc_auth.write_text(json.dumps(gRPC_Auth.data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        await bili_login_qrcode.finish(f"登录失败: {e}")
    await bili_login_qrcode.finish("登录成功，已将验证信息缓存至文件")
