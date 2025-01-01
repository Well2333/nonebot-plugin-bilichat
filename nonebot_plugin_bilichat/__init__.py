from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_alconna")
require("nonebot_plugin_waiter")

from .config import __version__, config, nonebot_config  # noqa: E402

cmd_perfix = f"{nonebot_config.command_start}{config.nonebot.cmd_start}{nonebot_config.command_sep}"

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-bilichat",
    description="全功能的 bilibili 内容解析器及订阅器",
    usage="视频、专栏、动态解析直接发送链接、小程序、xml卡片即可, 指令请参考 https://github.com/Well2333/nonebot-plugin-bilichat",
    homepage="https://github.com/Well2333/nonebot-plugin-bilichat",
    type="application",
    supported_adapters={"~onebot.v11", "~onebot.v12", "~qq"},
    extra={
        "author": "djkcyl & Well404",
        "version": __version__,
        "priority": 1,
        "menu_data": [
            {
                "func": "添加订阅",
                "trigger_method": "群聊 + 主人",
                "trigger_condition": f"{cmd_perfix}sub",
                "brief_des": "UP 主的昵称或 UID",
                "detail_des": "无",
            },
            {
                "func": "移除订阅",
                "trigger_method": "群聊 + 主人",
                "trigger_condition": f"{cmd_perfix}unsub",
                "brief_des": "UP 主的昵称或 UID",
                "detail_des": "无",
            },
            {
                "func": "查看本群订阅",
                "trigger_method": "群聊 + 无限制",
                "trigger_condition": f"{cmd_perfix}check",
                "brief_des": "无",
                "detail_des": "无",
            },
            {
                "func": "设置是否 at 全体成员, 仅 OB11 有效",
                "trigger_method": "群聊 + 主人",
                "trigger_condition": f"{cmd_perfix}atall",
                "brief_des": "UP 主的昵称或 UID, 或 `全局`",
                "detail_des": "无",
            },
            {
                "func": "验证码登录",
                "trigger_method": "无限制 + 主人",
                "trigger_condition": f"{cmd_perfix}smslogin",
                "brief_des": "无",
                "detail_des": "无",
            },
            {
                "func": "二维码登录",
                "trigger_method": "无限制 + 主人",
                "trigger_condition": f"{cmd_perfix}qrlogin",
                "brief_des": "无",
                "detail_des": "无",
            },
        ],
    },
)

from . import base_content_parsing, command  # noqa: F401, E402
