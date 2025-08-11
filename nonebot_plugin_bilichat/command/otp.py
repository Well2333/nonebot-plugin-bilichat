from io import BytesIO

import qrcode
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna.uniseg import Image, MsgTarget, Text, UniMessage
from nonebot_plugin_uninfo import Uninfo
from qrcode.image.pure import PyPNGImage

from nonebot_plugin_bilichat.config import ConfigCTX
from nonebot_plugin_bilichat.lib.auth import BILICHAT_OTP

from .base import bilichat

bili_webui_otp = bilichat.command("otp", permission=SUPERUSER)
bili_webui_otp_qrcode = bilichat.command("otp_qrcode", permission=SUPERUSER)


@bili_webui_otp.handle()
async def handle_webuiotp(
    target: MsgTarget,
    session: Uninfo,
):
    if not target.private:
        await bili_webui_otp.finish("此命令仅限私聊使用")
        return

    otp_code = BILICHAT_OTP.now()
    await UniMessage(Text(f"您的WebUI验证码是: {otp_code}\n有效期: 5分钟")).send(
        target=target, fallback=ConfigCTX.get().nonebot.fallback
    )

    logger.info(f"为用户 {session.id} 发送了当前的OTP验证码: {otp_code}")


@bili_webui_otp_qrcode.handle()
async def handle_webuiotp_qrcode(
    target: MsgTarget,
):
    if not target.private:
        await bili_webui_otp.finish("此命令仅限私聊使用")
        return

    qr = qrcode.QRCode(  # type: ignore
        version=1,
        box_size=10,
        border=4,
        image_factory=PyPNGImage,
    )
    qr.add_data(BILICHAT_OTP.provisioning_uri())
    img = qr.make_image(fill_color="black", back_color="white")
    img_data = BytesIO()
    img.save(img_data)
    await UniMessage(Image(raw=img_data.getvalue())).send(target=target, fallback=ConfigCTX.get().nonebot.fallback)


logger.success("Loaded: nonebot_plugin_bilichat.command.otp")
