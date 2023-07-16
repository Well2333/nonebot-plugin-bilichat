import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.adapters.qqguild import Adapter as QQGUILD_Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
# driver.register_adapter(QQGUILD_Adapter)

# nonebot.load_plugin("nonebot_plugin_sentry")
# nonebot.load_plugin("nonebot_plugin_all4one")
nonebot.load_plugin("nonebot_plugin_bilichat")
nonebot.load_builtin_plugin("echo")

if __name__ == "__main__":
    nonebot.run()
