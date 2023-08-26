import asyncio

from nonebot_plugin_apscheduler import scheduler

from ..config import plugin_config
from .dynamic import main as dynamic_main


@scheduler.scheduled_job("interval", seconds=plugin_config.bilichat_subs_interval, id="subscribe_update")
async def run_subscribe_update():
    async with asyncio.Lock():
        await dynamic_main()
