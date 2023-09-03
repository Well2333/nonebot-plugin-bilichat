from ....config import plugin_config

if plugin_config.bilichat_use_browser:
    from .browser_shot import screenshot as draw_column  # type: ignore


else:

    async def draw_column(*args, **kwargs):
        return
