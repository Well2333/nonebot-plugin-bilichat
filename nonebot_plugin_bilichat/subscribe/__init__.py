import asyncio

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

from ..config import plugin_config
from ..model.exception import AbortError
from ..optional import capture_exception
from .dynamic import fetch_dynamics_grpc, fetch_dynamics_rest
from .live import fetch_live
from .manager import SubscriptionSystem

LOCK = asyncio.Lock()


@scheduler.scheduled_job(
    "interval",
    seconds=plugin_config.bilichat_dynamic_interval,
    id="dynamic_update",
    jitter=plugin_config.bilichat_dynamic_interval // 5,
)
async def run_dynamic_update():
    async with LOCK:
        if not SubscriptionSystem.activate_uploaders:
            logger.debug("no activate uploaders to check, skip...")
            return
        # 动态
        logger.debug("[Dynamic] Updating start")
        up_groups = SubscriptionSystem.activate_uploaders.values()
        for up in up_groups:
            if plugin_config.bilichat_dynamic_grpc:
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


@scheduler.scheduled_job(
    "interval",
    seconds=plugin_config.bilichat_live_interval,
    id="live_update",
    jitter=plugin_config.bilichat_live_interval // 5,
)
async def run_live_update():
    async with LOCK:
        if not SubscriptionSystem.activate_uploaders:
            logger.debug("no activate uploaders to check, skip...")
            return
        try:
            logger.debug("[Live] Updating start")
            await fetch_live(SubscriptionSystem.activate_uploaders)
        except AbortError:
            logger.error("[Live] fetch live failed.")
        except Exception:
            capture_exception()
            logger.exception("[Live] fetch live failed.")
        logger.debug("[Live] Updating finished")
