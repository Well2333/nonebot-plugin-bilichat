from ....config import plugin_config

if plugin_config.bilichat_dynamic_style == "dynamicrender":
    from .dynamicrender import skia_dynamic as draw_dynamic
else:
    from .browser_shot import screenshot as draw_dynamic

if plugin_config.bilichat_bilibili_cookie_api and plugin_config.bilichat_bilibili_cookie:
    from ....api import bilibili_cookies  # noqa: F401