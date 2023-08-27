import asyncio

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

from ..config import plugin_config
from ..model.exception import AbortError
from ..optional import capture_exception
from .dynamic import fetch_dynamics_grpc, fetch_dynamics_rest
from .manager import SubscriptionSystem


@scheduler.scheduled_job("interval", seconds=plugin_config.bilichat_subs_interval, id="subscribe_update")
async def run_subscribe_update():
    async with asyncio.Lock():
        logger.debug("[Dynamic] Updating start")
        up_groups = SubscriptionSystem.activate_uploaders.values()

        for up in up_groups:
            try:
                logger.debug(f"[Dynamic] fetch {up.nickname}({up.uid}) by gRPC")
                await fetch_dynamics_grpc(up)
                continue
            except AbortError:
                logger.error(f"[Dynamic] fetch dynamic for {up} failed.")
            except Exception:
                capture_exception()
                logger.exception(f"[Dynamic] fetch dynamic for {up} failed.")

            try:
                logger.debug(f"[Dynamic] fetch {up.nickname}({up.uid}) by RestAPI")
                await fetch_dynamics_rest(up)
                continue
            except AbortError:
                logger.error(f"[Dynamic] fetch dynamic for {up} failed, skip...")
            except Exception:
                capture_exception()
                logger.exception(f"[Dynamic] fetch dynamic for {up} failed, skip...")

        logger.debug("[Dynamic] Updating finished")
