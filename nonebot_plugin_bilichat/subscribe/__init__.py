import asyncio

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

from ..model.exception import AbortError
from ..optional import capture_exception
from .dynamic import fetch_dynamics_grpc, fetch_dynamics_rest
from .live import fetch_live
from .manager import CONFIG_LOCK, SubscriptionSystem

NO_ACTIVE_UP = 0


async def _check_activate_uploaders(func:str = "Scheduler") -> bool:
    global NO_ACTIVE_UP
    if SubscriptionSystem.activate_uploaders:
        NO_ACTIVE_UP = 0
        return True
    if NO_ACTIVE_UP >= 10:
        NO_ACTIVE_UP = 0
        logger.debug(f"[{func}]-(0/10) 无活跃的UP, 尝试刷新列表...")
        await SubscriptionSystem.refresh_activate_uploaders(refresh=True)
        if SubscriptionSystem.activate_uploaders:
            return True
    NO_ACTIVE_UP += 1
    logger.debug(f"[{func}]-({NO_ACTIVE_UP}/10) 无活跃的UP, 跳过...")
    return False


@scheduler.scheduled_job(
    "interval",
    seconds=90,
    id="dynamic_update",
    jitter=5,
    max_instances=1,
)
async def run_dynamic_update():
    if not await _check_activate_uploaders("Dynamic"):
        return
    # 动态
    logger.debug("[Dynamic] 开始获取动态...")
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
                    logger.debug(f"[Dynamic] 使用gRPC获取 {up.nickname}({up.uid}) | offset={up.dyn_offset}")
                    await fetch_dynamics_grpc(up)
                    continue
                except AbortError:
                    logger.error(f"[Dynamic] 获取 {up} 失败.")
                except Exception:
                    capture_exception()
                    logger.exception(f"[Dynamic] 获取 {up} 失败.")

            try:
                logger.debug(f"[Dynamic] 使用 RestAPI 获取 {up.nickname}({up.uid}) | offset={up.dyn_offset}")
                await fetch_dynamics_rest(up)
                continue
            except AbortError:
                logger.error(f"[Dynamic] 获取 {up} 失败, skip...")
            except Exception:
                capture_exception()
                logger.exception(f"[Dynamic] 获取 {up} 失败, skip...")
    logger.debug("[Dynamic] 获取完成")


@scheduler.scheduled_job(
    "interval",
    seconds=60,
    id="live_update",
    jitter=5,
    max_instances=1,
)
async def run_live_update():
    if not await _check_activate_uploaders("Live"):
        return
    try:
        logger.debug("[Live] 获取开始")
        await fetch_live(list(SubscriptionSystem.activate_uploaders.keys()).copy())
    except AbortError:
        logger.error("[Live] 获取中断.")
    except Exception:
        capture_exception()
        logger.exception("[Live] 获取失败.")
    logger.debug("[Live] 获取完成")
