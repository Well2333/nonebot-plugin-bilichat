from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna.uniseg import MsgTarget, Text, UniMessage
from nonebot_plugin_uninfo import Uninfo

from nonebot_plugin_bilichat.config import ConfigCTX
from nonebot_plugin_bilichat.lib.auth import generate_otp

from .base import bilichat

bili_webui_otp = bilichat.command("webuiotp", permission=SUPERUSER)


@bili_webui_otp.handle()
async def handle_webuiotp(
    target: MsgTarget,
    session: Uninfo,
):
    """生成WebUI OTP验证码"""
    # 检查是否为私聊
    if not target.private:
        await bili_webui_otp.finish("此命令仅限私聊使用")
        return

    # 生成6位数字验证码
    otp_code = generate_otp()
    
    # 发送验证码给用户
    await UniMessage(Text(f"您的WebUI验证码是: {otp_code}\n有效期: 5分钟")).send(
        target=target, 
        fallback=ConfigCTX.get().nonebot.fallback
    )
    
    logger.info(f"为用户 {session.id} 生成了OTP验证码: {otp_code}")


logger.success("Loaded: nonebot_plugin_bilichat.command.otp") 