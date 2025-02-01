import time
from contextlib import suppress

from httpx import AsyncClient
from nonebot.log import logger
from nonebot_plugin_alconna import AtAll, Image, Text, UniMessage
from nonebot_plugin_apscheduler import scheduler
from sentry_sdk import capture_exception

from nonebot_plugin_bilichat.config import ConfigCTX
from nonebot_plugin_bilichat.lib.tools import calc_time_total
from nonebot_plugin_bilichat.model.exception import AbortError
from nonebot_plugin_bilichat.request_api import get_request_api
from nonebot_plugin_bilichat.subscribe.status import PushType, UPStatus

from .status import SubsStatus


async def dynamic():
    logger.debug("[Dynamic] 检查新动态")
    try:
        ups = await SubsStatus.get_online_ups("dynamic")
    except AbortError:
        logger.debug("[Dynamic] 没有需要推送的用户, 跳过")
        return
    for up in ups:
        try:
            logger.debug(f"[Dynamic] 获取 UP {up.name}({up.uid}) 动态")
            api = get_request_api()
            try:
                all_dyns = await api.subs_dynamic(up.uid)
                if not all_dyns:
                    logger.info(f"[Dynamic] UP {up.name}({up.uid}) 未发布动态")
                    continue
            except Exception as e:
                logger.error(f"[Dynamic] 获取 UP {up.name}({up.uid}) 动态失败: {e}")
                continue
            # 第一次获取, 仅更新offset
            if up.dyn_offset == -1:
                with suppress(Exception):
                    up.dyn_offset = max([dyn.dyn_id for dyn in all_dyns])
                continue
            # 新动态
            new_dyns = sorted([dyn for dyn in all_dyns if dyn.dyn_id > up.dyn_offset], key=lambda x: x.dyn_id)
            for dyn in new_dyns:
                logger.info(f"[Dynamic] UP {up.name}({up.uid}) 发布了新动态: {dyn.dyn_id}")
                up.dyn_offset = dyn.dyn_id
                content = await api.content_dynamic(dyn.dyn_id, ConfigCTX.get().api.browser_shot_quality)
                dyn_img = Image(raw=content.img_bytes)
                for user in up.users:
                    if user.subscribes[str(up.uid)].dynamic[dyn.dyn_type] == PushType.IGNORE:
                        continue
                    logger.info(f"[Dynamic] 推送 UP {up.name}({up.uid}) 动态给用户 {user.id}")
                    up_info = user.subscribes[str(up.uid)]
                    up_info.uname = up.name  # 更新up名字
                    up_name = up_info.nickname or up_info.uname
                    at_all = (
                        AtAll()
                        if user.subscribes[str(up.uid)].dynamic.get(dyn.dyn_type) == PushType.AT_ALL
                        else Text("")
                    )
                    msg = UniMessage([at_all, Text(f"{up_name} 发布了新动态\n"), dyn_img, Text(f"\n{content.b23}")])
                    target = user.target
                    logger.debug(f"target: {target}")
                    await user.target.send(msg)
        except Exception as e:
            capture_exception(e)
            logger.exception(e)
            continue


async def live():
    logger.debug("[Live] 检查直播状态")
    try:
        ups: list[UPStatus] = await SubsStatus.get_online_ups("live")
    except AbortError:
        logger.debug("[Live] 没有需要推送的用户, 跳过")
        return
    api = get_request_api()
    try:
        lives = {lv.uid: lv for lv in await api.sub_lives([up.uid for up in ups])}
    except Exception as e:
        logger.error(f"[Live] 获取直播信息失败: {e}")
        return
    for up in ups:
        live = lives[up.uid]
        logger.debug(f"[Live] UP {up.name}({up.uid}) 直播状态: {live.live_status}")
        # 第一次获取, 仅更新状态
        if up.live_status == -1:
            up.live_status = live.live_status
            continue
        # 正在直播, live.live_status == 1
        if live.live_status == 1:
            # 开播通知, up.live_status != 1
            if up.live_status != 0:
                cover = (await AsyncClient().get(live.cover_from_user)).content
                live_cover = Image(raw=cover)
                for user in up.users:
                    if user.subscribes[str(up.uid)].live == PushType.IGNORE:
                        continue
                    logger.info(f"[Live] 推送 UP {up.name}({up.uid}) 开播给用户 {user.id}")
                    up_info = user.subscribes[str(up.uid)]
                    up_info.uname = up.name  # 更新up名字
                    up_name = up_info.nickname or up_info.uname
                    at_all = AtAll() if user.subscribes[str(up.uid)].live == PushType.AT_ALL else Text("")
                    msg = UniMessage(
                        [
                            at_all,
                            Text(f"{up_name} 开播了: {live.title}\n"),
                            live_cover,
                            Text(f"\nhttps://live.bilibili.com/{live.room_id}"),
                        ]
                    )
                    await user.target.send(msg)
        # 下播通知, up.live_status == 1 且 live.live_status != 1
        elif up.live_status == 1:
            for user in up.users:
                if user.subscribes[str(up.uid)].live == PushType.IGNORE:
                    continue
                logger.info(f"[Live] 推送 UP {up.name}({up.uid}) 下播给用户 {user.id}")
                up_info = user.subscribes[str(up.uid)]
                up_info.uname = up.name  # 更新up名字
                up_name = up_info.nickname or up_info.uname
                live_time = (
                    Text(f"\n本次直播时长 {calc_time_total(time.time() - live.live_time)}")
                    if live.live_time > 1500000000
                    else Text("")
                )
                msg = UniMessage([Text(f"{up_name} 下播了"), live_time])
                await user.target.send(msg)
        up.live_status = live.live_status


def set_subs_job():
    if dynamic_interval := ConfigCTX.get().subs.dynamic_interval:
        logger.info(f"启动动态检查定时任务, 间隔 {dynamic_interval} 秒")
        scheduler.add_job(
            dynamic,
            "interval",
            id="bilichat_dynamic",
            seconds=ConfigCTX.get().subs.dynamic_interval,
            jitter=ConfigCTX.get().subs.dynamic_interval // 2,
            max_instances=1,
        )
    if live_interval := ConfigCTX.get().subs.live_interval:
        logger.info(f"启动直播检查定时任务, 间隔 {live_interval} 秒")
        scheduler.add_job(
            live,
            "interval",
            id="bilichat_live",
            seconds=ConfigCTX.get().subs.live_interval,
            jitter=ConfigCTX.get().subs.live_interval // 2,
            max_instances=1,
        )


def reset_subs_job():
    scheduler.remove_job("bilichat_dynamic")
    scheduler.remove_job("bilichat_live")
    set_subs_job()
    logger.info("已重置订阅定时任务")
    return True


set_subs_job()
