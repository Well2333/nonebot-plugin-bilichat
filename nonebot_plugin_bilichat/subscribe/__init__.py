import asyncio

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

from ..model.exception import AbortError
from ..optional import capture_exception
from .dynamic import fetch_dynamics_grpc, fetch_dynamics_rest
from .live import fetch_live
from .manager import CONFIG_LOCK, SubscriptionSystem


@scheduler.scheduled_job(
    "interval",
    seconds=90,
    id="dynamic_update",
    jitter=5,
    max_instances=1,
)
async def run_dynamic_update():
    if not SubscriptionSystem.activate_uploaders:
        logger.debug("no activate uploaders to check, skip...")
        return
    # 动态
    logger.debug("[Dynamic] Updating start")
    up_groups = list(SubscriptionSystem.activate_uploaders.keys()).copy()
    for up_id in up_groups:
        await asyncio.sleep(0)
        up = SubscriptionSystem.activate_uploaders.get(up_id)
        if not up:
            continue
        while CONFIG_LOCK.locked():
            await asyncio.sleep(0)
        async with CONFIG_LOCK:
            if SubscriptionSystem.config.dynamic_grpc:
                try:
                    logger.debug(f"[Dynamic] fetch {up.nickname}({up.uid}) by gRPC | offset={up.dyn_offset}")
                    await fetch_dynamics_grpc(up)
                    continue
                except AbortError:
                    logger.error(f"[Dynamic] fetch dynamic for {up} failed.")
                except Exception:
                    capture_exception()
                    logger.exception(f"[Dynamic] fetch dynamic for {up} failed.")

            try:
                logger.debug(f"[Dynamic] fetch {up.nickname}({up.uid}) by RestAPI | offset={up.dyn_offset}")
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
    seconds=60,
    id="live_update",
    jitter=5,
    max_instances=1,
)
async def run_live_update():
    if not SubscriptionSystem.activate_uploaders:
        logger.debug("no activate uploaders to check, skip...")
        return
    try:
        logger.debug("[Live] Updating start")
        await fetch_live(list(SubscriptionSystem.activate_uploaders.keys()).copy())
    except AbortError:
        logger.error("[Live] fetch live failed.")
    except Exception:
        capture_exception()
        logger.exception("[Live] fetch live failed.")
    logger.debug("[Live] Updating finished")
