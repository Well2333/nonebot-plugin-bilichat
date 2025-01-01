import asyncio
import time
from datetime import datetime
from io import BytesIO

import qrcode
from httpx import AsyncClient
from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna.uniseg import Image, MsgTarget, Text, UniMessage
from nonebot_plugin_uninfo.permission import ADMIN
from pytz import timezone
from qrcode.image.pure import PyPNGImage

from nonebot_plugin_bilichat.config import config
from nonebot_plugin_bilichat.model.request_api import Account, Note
from nonebot_plugin_bilichat.request_api import request_apis

from .base import bilichat

bili_check_login = bilichat.command(
    "checklogin",
    aliases=set(config.nonebot.cmd_check_login),
    permission=ADMIN()|SUPERUSER,
)


bili_login_qrcode = bilichat.command(
    "qrlogin",
    aliases=set(config.nonebot.cmd_login_qrcode),
    permission=ADMIN()|SUPERUSER,
)
bili_logout = bilichat.command(
    "logout",
    aliases=set(config.nonebot.cmd_logout),
    permission=SUPERUSER,
)


@bili_check_login.handle()
async def bili_login_handle():
    texts = []
    for api in request_apis:
        auths: list[Account] = await api.account_web_all()
        note = f" ({api._note})" if api._note else ""
        texts.append(f">>> {api._api_base}{note}")
        if not auths:
            texts.append("无已登录账号")
            continue
        for auth in auths:
            note = f" ({auth.note})" if auth.note else ""
            texts.append(f" |-> {auth.uid}{note}")
    await bili_check_login.finish("\n".join(texts) or "无已登录账号")


@bili_login_qrcode.handle()
async def bili_qrcode_login(target: MsgTarget):
    async with AsyncClient(
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
                "Safari/537.36 Edg/114.0.1823.67"
            ),
            "Referer": "https://www.bilibili.com/",
        }
    ) as client:
        # 申请二维码
        resp = await client.get(
            "https://passport.bilibili.com/x/passport-login/web/qrcode/generate",
            params={"source": "main-fe-header", "go_url": "https://www.bilibili.com/", "web_location": 333.1007},
        )
        if resp.status_code != 200:
            logger.error(f"获取二维码失败 code:{resp.status_code} {resp.text}")
            await bili_login_qrcode.finish("获取二维码失败, 请重试。")
        qr_data = resp.json()

        assert qr_data["code"] == 0, f"获取二维码失败 code:{qr_data['code']} {qr_data['message']}"

        qr_url = qr_data["data"]["url"]
        qrcode_key = qr_data["data"]["qrcode_key"]
        logger.debug(f"qrcode login key {qrcode_key}; url {qr_url}")

        # 生成并发送二维码
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4,
            image_factory=PyPNGImage,
        )
        qr.add_data(qr_url)
        img = qr.make_image(fill_color="black", back_color="white")
        img_data = BytesIO()
        img.save(img_data)
        await UniMessage([Text("请在 120s 内使用 bilibili 客户端扫描二维码登录"), Image(raw=img_data.getvalue())]).send(
            target=target
        )

        # 轮询登录状态
        start_time = time.time()
        while True:
            await asyncio.sleep(3)
            # 检查是否超时
            elapsed = time.time() - start_time
            if elapsed > 120:
                logger.info("二维码已超时")
                await bili_login_qrcode.finish("二维码已超时, 请重新操作。")

            # 轮询登录状态
            poll_data = (
                await client.get(
                    "https://passport.bilibili.com/x/passport-login/web/qrcode/poll",
                    params={"qrcode_key": qrcode_key, "source": "main-fe-header", "web_location": 333.1007},
                )
            ).json()
            assert poll_data["code"] == 0, f"轮询登录状态失败 code:{poll_data['code']} {poll_data['message']}"
            data = poll_data.get("data", {})
            code = data.get("code")
            message = data.get("message", "")

            match code:
                case 86101:
                    logger.info("二维码未扫描, 等待扫描...")
                case 86090:
                    logger.info("二维码已扫描, 等待确认...")
                case 0:
                    logger.info("登录成功")
                    # 保存 Cookies
                    cookies = dict(client.cookies)
                    api = request_apis[0]
                    await api.account_web_creat(
                        int(cookies["DedeUserID"]),
                        cookies,
                        Note(
                            source=f"nonebot {target!r}",
                            create_time=datetime.now(tz=timezone("Asia/Shanghai")).isoformat(timespec="seconds"),
                        ),
                    )
                    await bili_login_qrcode.finish("登录成功")

                case 86038:
                    logger.info("二维码已失效")
                    await bili_login_qrcode.finish("二维码已失效, 请重新操作。")
                    break
                case _:
                    logger.info(f"未知状态: {code}, 信息: {message}")


@bili_logout.handle()
async def bili_logout_handle(uid: Message = CommandArg()):
    api = request_apis[0]
    auths: list[Account] = await api.account_web_all()
    for auth in auths:
        if str(auth.uid) == uid.extract_plain_text():
            await api.account_web_delete(auth.uid)
            await bili_logout.finish(f"已登出账号 {auth.uid}")


logger.success("Loaded: nonebot_plugin_bilichat.command.login")
