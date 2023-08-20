import json
from datetime import timedelta

from bilireq.auth import Auth
from bilireq.login import Login
from nonebot import get_driver
from nonebot.log import logger
from nonebot.params import ArgPlainText
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State

from .lib.store import cache_dir

gRPC_Auth: Auth = Auth()


bili_grpc_auth = cache_dir.joinpath("bili_grpc_auth.json")
bili_grpc_auth.touch(0o700, exist_ok=True)


async def login_from_cache() -> bool:
    global gRPC_Auth
    try:
        data = json.loads(bili_grpc_auth.read_bytes())
        gRPC_Auth.update(data)
        await gRPC_Auth.refresh()
        logger.debug(gRPC_Auth.data)
    except Exception as e:
        logger.error(f"缓存登录失败，请使用验证码登录: {e}")
        return False
    else:
        logger.success("缓存登录成功")
        return True


get_driver().on_startup(login_from_cache)
bili_login = on_command("bilichat_login", permission=SUPERUSER, rule=to_me(), expire_time=timedelta(seconds=120))


@bili_login.handle()
async def bili_login_from_cache():
    if await login_from_cache():
        await bili_login.finish("使用缓存登录成功")


@bili_login.got("username", prompt="请输入B站账号(电话号码)")
async def bili_send_sms(state: T_State, username: str = ArgPlainText()):
    login = Login()
    state["_username_"] = username
    try:
        state["_captcha_key_"] = await login.send_sms(username)
    except Exception as e:
        await bili_login.finish(f"无法发送验证码: {e}")


@bili_login.got("sms", prompt="验证码已发送，请在120秒内输入验证码")
async def bili_handle_login(state: T_State, sms: str = ArgPlainText()):
    global gRPC_Auth
    login = Login()
    try:
        gRPC_Auth = await login.sms_login(code=sms, tel=state["_username_"], cid=86, captcha_key=state["_captcha_key_"])
        logger.debug(gRPC_Auth.data)
        bili_grpc_auth.write_text(json.dumps(gRPC_Auth.data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        await bili_login.finish(f"登录失败: {e}")
    await bili_login.finish("登录成功，已将验证信息缓存至文件")
