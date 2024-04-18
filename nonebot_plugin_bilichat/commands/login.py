import time
from asyncio import Lock

from bilireq.login import Login
from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna.uniseg import Image, MsgTarget, UniMessage

from ..config import plugin_config
from ..lib.bilibili_request.auth import AuthManager
from ..lib.tools import calc_time_total
from .base import bilichat, check_lock

# bili_login_sms = bilichat.command(
#     "smslogin",
#     aliases={
#         "验证码登录",
#     },
#     permission=SUPERUSER,
# )


# @bili_login_sms.got("username", prompt="请输入B站账号(电话号码)")
# async def bili_send_sms(state: T_State, username: str = ArgPlainText()):
#     login = Login()
#     state["_username_"] = username
#     state["_login_"] = login
#     try:
#         state["_captcha_key_"] = await login.send_sms(username)
#     except Exception as e:
#         await bili_login_sms.finish(f"无法发送验证码: {e}")
#
#
# @bili_login_sms.got("sms", prompt="验证码已发送，请在120秒内输入验证码")
# async def bili_handle_login(state: T_State, sms: str = ArgPlainText()):
#     login: Login = state["_login_"]
#     try:
#         auth = await login.sms_login(code=sms, tel=state["_username_"], cid=86, captcha_key=state["_captcha_key_"])
#         assert auth, "登录失败，返回数据为空"
#         logger.debug(auth.data)
#         AuthManager.grpc_auths.append(auth)
#         AuthManager.dump_grpc_auths()
#     except Exception as e:
#         await bili_login_sms.finish(f"登录失败: {e}")
#     await bili_login_sms.finish("登录成功，已将验证信息缓存至文件")

bili_check_login = bilichat.command(
    "checklogin",
    aliases=set(plugin_config.bilichat_cmd_check_login),
    permission=SUPERUSER,
)


bili_login_qrcode = bilichat.command(
    "qrlogin",
    aliases=set(plugin_config.bilichat_cmd_login_qrcode),
    permission=SUPERUSER,
)
bili_logout = bilichat.command(
    "logout",
    aliases=set(plugin_config.bilichat_cmd_logout),
    permission=SUPERUSER,
)


@bili_check_login.handle()
async def bili_login_handle():
    await bili_check_login.finish(
        "\n----------\n".join(
            [
                (
                    f"账号uid: {auth.uid}\n"
                    f"token有效期: {calc_time_total(auth.tokens_expired-int(time.time()))}\n"
                    f"cookie有效期: {calc_time_total(auth.cookies_expired-int(time.time()))}"
                )
                for auth in AuthManager.grpc_auths
            ]
        )
    )


@bili_login_qrcode.handle()
async def bili_qrcode_login(target: MsgTarget, lock: Lock = Depends(check_lock)):
    async with lock:
        login = Login()
        qr_url = await login.get_qrcode_url()
        logger.debug(f"qrcode login url: {qr_url}")
        await UniMessage(Image(raw=await login.get_qrcode(qr_url))).send(target=target)  # type: ignore
        try:
            auth = await login.qrcode_login(interval=5)
            assert auth, "登录失败，返回数据为空"
            logger.debug(auth.data)
            AuthManager.add_auth(auth)
            AuthManager.dump_grpc_auths()
        except Exception as e:
            await bili_login_qrcode.finish(f"登录失败: {e}")
        await bili_login_qrcode.finish("登录成功，已将验证信息缓存至文件")


@bili_logout.handle()
async def bili_logout_handle(lock: Lock = Depends(check_lock), uid: Message = CommandArg()):
    async with lock:
        if not uid.extract_plain_text().isdigit():
            await bili_logout.finish("请输入正确的uid")
        if msg := AuthManager.remove_auth(int(uid.extract_plain_text())):
            await bili_logout.finish(msg)
        await bili_logout.finish(f"账号 {uid} 已退出登录")
