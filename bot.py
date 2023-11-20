import nonebot

# from nonebot.adapters.mirai2 import Adapter as Mirai_Adapter
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

# from nonebot.adapters.qq import Adapter as QQ_Adapter
from nonebot.log import logger

nonebot.init()

logger.add(
    "logs/{time:YYYY-MM-DD}.log",
    level="INFO",
    rotation="00:00",
    retention="720 days",
)
logger.add(
    "logs/debug/{time:YYYY-MM-DD}.log",
    level="DEBUG",
    rotation="00:00",
    compression="tar.xz",
    retention="7 days",
)
logger.info("========= 重新启动 =========")

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
# driver.register_adapter(Mirai_Adapter)
# driver.register_adapter(QQ_Adapter)


nonebot.load_plugin("nonebot_plugin_bilichat")
nonebot.load_builtin_plugin("echo")
nonebot.load_plugin("v11_selfmsg_hook")

if __name__ == "__main__":
    nonebot.run()
