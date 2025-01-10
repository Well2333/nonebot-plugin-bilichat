import time

from httpx import AsyncClient
from nonebot.log import logger
from nonebot_plugin_alconna import AtAll, Image, Text, UniMessage
from nonebot_plugin_apscheduler import scheduler

from nonebot_plugin_bilichat.config import config
from nonebot_plugin_bilichat.lib.tools import calc_time_total
from nonebot_plugin_bilichat.model.exception import AbortError
from nonebot_plugin_bilichat.request_api import get_request_api

from .status import SubsStatus


@scheduler.scheduled_job(
    "interval", id="dynamic", seconds=config.subs.dynamic_interval, jitter=config.subs.dynamic_interval // 2
)
async def dynamic():
    logger.debug("[Dynamic] 检查新动态")
    try:
        ups = await SubsStatus.get_online_ups()
    except AbortError:
        return
    for up in ups:
        logger.debug(f"[Dynamic] 获取 UP {up.name}({up.uid}) 动态")
        api = get_request_api()
        try:
            all_dyns = await api.subs_dynamic(up.uid)
        except Exception as e:
            logger.error(f"[Dynamic] 获取 UP {up.name}({up.uid}) 动态失败: {e}")
            continue
        # 第一次获取, 仅更新offset
        if up.dyn_offset == -1:
            up.dyn_offset = max([dyn.dyn_id for dyn in all_dyns])
            return
        # 新动态
        new_dyns = sorted([dyn for dyn in all_dyns if dyn.dyn_id > up.dyn_offset], key=lambda x: x.dyn_id)
        for dyn in new_dyns:
            logger.info(f"[Dynamic] UP {up.name}({up.uid}) 发布了新动态: {dyn.dyn_id}")
            up.dyn_offset = dyn.dyn_id
            content = await api.content_dynamic(dyn.dyn_id, config.api.browser_shot_quality)
            dyn_img = Image(raw=content.img_bytes)
            for user in up.users:
                logger.info(f"[Dynamic] 推送 UP {up.name}({up.uid}) 动态给用户 {user.id}")
                up_info = user.subscribes[str(up.uid)]
                up_info.uname = up.name  # 更新up名字
                up_name = up_info.nickname or up_info.uname
                at_all = AtAll() if user.subscribes[str(up.uid)].dynamic.get(dyn.dyn_type) == "AT_ALL" else Text("")
                msg = UniMessage([at_all, Text(f"{up_name} 发布了新动态\n"), dyn_img, Text(f"\n{content.b23}")])
                target = user.target
                logger.debug(f"target: {target}")
                await user.target.send(msg)


@scheduler.scheduled_job(
    "interval", id="live", seconds=config.subs.live_interval, jitter=config.subs.live_interval // 2
)
async def live():
    logger.debug("[Live] 检查直播状态")
    try:
        ups = await SubsStatus.get_online_ups()
    except AbortError:
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
            return
        # 正在直播
        if live.live_status == 1:
            # 开播通知
            if up.live_status == 0:
                cover = (await AsyncClient().get(live.cover_from_user)).content
                live_cover = Image(raw=cover)
                for user in up.users:
                    logger.info(f"[Live] 推送 UP {up.name}({up.uid}) 开播给用户 {user.id}")
                    up_info = user.subscribes[str(up.uid)]
                    up_info.uname = up.name  # 更新up名字
                    up_name = up_info.nickname or up_info.uname
                    at_all = AtAll() if user.subscribes[str(up.uid)].live == "AT_ALL" else Text("")
                    msg = UniMessage(
                        [
                            at_all,
                            Text(f"{up_name} 开播了: {live.title}\n"),
                            live_cover,
                            Text(f"\nhttps://live.bilibili.com/{live.room_id}"),
                        ]
                    )
                    await user.target.send(msg)
        # 下播通知
        elif up.live_status == 1:
            for user in up.users:
                logger.info(f"[Live] 推送 UP {up.name}({up.uid}) 下播给用户 {user.id}")
                up_info = user.subscribes[str(up.uid)]
                up_info.uname = up.name  # 更新up名字
                up_name = up_info.nickname or up_info.uname
                msg = UniMessage(
                    Text(f"{up_name} 下播了\n本次直播时长 {calc_time_total(time.time() - live.live_time)}")
                )
                await user.target.send(msg)
        up.live_status = live.live_status
