import nonebot
from nonebot.adapters.mirai2 import Adapter as MIRAI_Adapter
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.adapters.onebot.v12 import Adapter as ONEBOT_V12Adapter
from nonebot.adapters.qqguild import Adapter as QQGUILD_Adapter

# from nonebot_adapter_walleq import Adapter as Walleq_Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(MIRAI_Adapter)
driver.register_adapter(ONEBOT_V11Adapter)
driver.register_adapter(ONEBOT_V12Adapter)
driver.register_adapter(QQGUILD_Adapter)
# driver.register_adapter(Walleq_Adapter)

# nonebot.load_plugin("nonebot_plugin_sentry")
# nonebot.load_plugin("nonebot_plugin_all4one")
nonebot.load_plugin("nonebot_plugin_bilichat")

if __name__ == "__main__":
    nonebot.run()
