from nonebot import require

require("nonebot_plugin_localstore")


import nonebot_plugin_localstore as store


cache_dir = store.get_cache_dir("nonebot_plugin_bilichat")
data_dir = store.get_data_dir("nonebot_plugin_bilichat")
config_dir = store.get_config_dir("nonebot_plugin_bilichat")