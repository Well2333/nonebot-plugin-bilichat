import contextlib
import importlib
import pkgutil

from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from . import adatpters
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

modules = []
for _, module_name, _ in pkgutil.iter_modules(adatpters.__path__):
    full_module_name = f"{adatpters.__name__}.{module_name}"
    with contextlib.suppress(ImportError):
        importlib.import_module(full_module_name)
        logger.success(f"{module_name} adapter was loaded successfully")
