from nonebot.plugin import PluginMetadata

from .config import __version__

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-bilichat",
    description="一个通过 OpenAI 来对b站视频进行总结插件",
    usage="直接发送视频链接即可",
    homepage="https://github.com/Aunly/nonebot-plugin-bilichat",
    type="application",
    supported_adapters={"~onebot.v11", "~onebot.v12", "~qqguild", "~mirai2"},
    extra={
        "author": "djkcyl & Well404",
        "version": __version__,
        "priority": 1,
    },
)

from . import adapters, commands
