import time
from json import JSONDecodeError
from typing import Dict

from bilireq.exceptions import ResponseCodeError
from bilireq.live import get_rooms_info_by_uids
from httpx import ConnectError, TransportError
from nonebot.log import logger

from ..lib.bilibili_request import get_b23_url, hc
from ..lib.tools import calc_time_total
from ..model.bilibili.live import LiveRoom
from ..model.exception import AbortError
from ..optional import capture_exception
from .manager import Uploader


async def fetch_live(ups: Dict[int, Uploader]):
    try:
        status_infos = await get_rooms_info_by_uids(list(ups.keys()))
    except (TransportError, ConnectError, JSONDecodeError, ResponseCodeError) as e:
        logger.error(f"[Live] fetch live status failed: {type(e)} {e}")
        raise AbortError("Live Abort")
    except RuntimeError as e:
        logger.error(f"[Live] fetch live status failed: {type(e)} {e}")
        if "The connection pool was closed while" not in str(e):
            capture_exception(e)
        raise AbortError("Live Abort")
    except Exception as e:  # noqa
        capture_exception(e)
        raise e

    if not status_infos:
        return

    for up_id, _data in status_infos.items():
        up = ups.get(int(up_id))
        room = LiveRoom(**_data)
        # 如果没找到该UP，理论上不会发生
        if not up:
            logger.critical("订阅记录中未查询到该 UP 的信息，请联系开发者进行修复" + str(_data))
            continue
        try:
            logger.debug(f"[Live] {up.nickname}({up.uid}) live_status: {room.live_status}")
            # 已开播
            if room.live_status == 1:
                # 如果是 -1 则为第一次刷取，跳过后续推送部分
                if up.living == -1:
                    up.living = room.live_time
                # 如果记录值为 0 则是刚开播，开始开播推送
                elif up.living == 0:
                    up.living = room.live_time
                    live_prompt = (
                        f"UP {room.uname}({room.uid})"
                        f"在 {room.area_v2_name} / {room.area_name} 区开播啦 \n"
                        f"标题：{room.title}"
                    )
                    url = await get_b23_url(f"https://live.bilibili.com/{room.room_id}")
                    live_image = (await hc.get(room.cover_from_user)).content
                    logger.info(f"{live_prompt}")
                    content = [live_prompt, live_image, url]
                    for user in up.subscribed_users:
                        if user.subscriptions[up.uid].get("live", True):
                            await user.push_to_user(
                                content=content, at_all=user.subscriptions[up.uid]["live_at_all"] or user.at_all
                            )
                # 如果记录值大于 0 则是正在直播，不进行开播推送
                else:
                    up.living = room.live_time
            # 未开播或轮播，且记录大于 0，则进行下播推送
            elif up.living > 0:
                livetime = calc_time_total(time.time() - up.living)
                up.living = 0
                live_prompt = f"UP {room.uname}({room.uid}) 已下播啦\n本次直播时长 {livetime}"
                logger.info(f"{live_prompt}")
                content = [live_prompt]
                for user in up.subscribed_users:
                    if user.subscriptions[up.uid].get("live", True):
                        await user.push_to_user(content=content, at_all=False)  # type: ignore
        finally:
            # 如果是 -1 则更新为 0
            if up.living == -1:
                up.living = 0
