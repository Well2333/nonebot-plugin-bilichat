import asyncio
from typing import Dict, List, Optional

import httpx
from loguru import logger

from ..config import plugin_config
from ..model.bcut_asr import ResultStateEnum
from ..model.exception import AbortError
from .bcut_asr import BcutASR
from .bilibili_request import get_player, grpc_get_playview, hc
from ..optional import capture_exception  # type: ignore


async def get_subtitle_url(aid: int, cid: int) -> Optional[str]:
    video_player = await get_player(aid, cid)
    subtitles_raw: List[Dict] = video_player["subtitle"]["subtitles"]
    logger.debug(subtitles_raw)

    if not subtitles_raw:
        return

    logger.debug(subtitles_raw)
    ai_subtitles = {}
    manual_subtitles = {}
    preferred_subs = ["zh-Hans", "en-US"]

    for subtitle in subtitles_raw:
        if "自动生成" in subtitle["lan_doc"]:
            ai_subtitles[subtitle["lan"]] = subtitle["subtitle_url"]
        else:
            manual_subtitles[subtitle["lan"]] = subtitle["subtitle_url"]

    if not manual_subtitles:
        return next(iter(ai_subtitles.values()))

    for sub in preferred_subs:
        if sub in manual_subtitles:
            return manual_subtitles[sub]

    return next(iter(manual_subtitles.values()))


async def get_subtitle(aid: int, cid: int) -> List[str]:
    subtitle_url = await get_subtitle_url(aid, cid)
    if subtitle_url:
        logger.debug(subtitle_url)
        subtitle = await hc.get(f"https:{subtitle_url}")
        if subtitle.status_code != 200:
            logger.warning(
                f"Subtitle fetch failed: {aid} {cid}, status code: {subtitle.status_code}, content: {subtitle.text}"
            )
            raise AbortError("Subtitle fetch failed")
        logger.debug(f"Subtitle fetched: {aid} {cid}")
    elif plugin_config.bilichat_use_bcut_asr:
        logger.info(f"Subtitle not found, try using BCut-ASR: {aid} {cid}")
        playview = await grpc_get_playview(aid, cid)
        if not playview.video_info.dash_audio:
            raise AbortError("Video has no audio streaming")
        async with httpx.AsyncClient(
            headers={
                "user-agent": "Bilibili Freedoooooom/MarkII",
            },
        ) as client:
            audio_resp = await client.get(
                playview.video_info.dash_audio[-1].backup_url[0]
                if playview.video_info.dash_audio[-1].backup_url
                else playview.video_info.dash_audio[-1].baseUrl,
            )
        audio_resp.raise_for_status()
        audio = audio_resp.content
        for count in range(plugin_config.bilichat_neterror_retry):
            try:
                asr = await get_bcut_asr(audio)
                return [x.transcript for x in asr]
            except httpx.ReadTimeout as e:
                logger.error(
                    f"except httpx.ReadTimeout, retry count remaining {plugin_config.bilichat_neterror_retry-count-1}"
                )
                await asyncio.sleep(5)
            except Exception as e:
                logger.exception(f"BCut-ASR conversion failed: {e}")
                capture_exception()
                raise AbortError("BCut-ASR conversion failed") from e
        raise AbortError("BCut-ASR conversion failed due to network error")
    else:
        raise AbortError("Subtitles not found and BCut-ASR is disabled in env")
    return [x["content"] for x in subtitle.json()["body"]]


async def get_bcut_asr(file_bytes: bytes):
    bcut = BcutASR()
    bcut.set_data(raw_data=file_bytes, data_fmt="m4a")
    await bcut.upload()
    await bcut.create_task()
    while True:
        result = await bcut.result()
        if result.state == ResultStateEnum.COMPLETE:
            return result.parse()
        elif result.state in [ResultStateEnum.RUNING, ResultStateEnum.STOP]:
            logger.info(f"[BCut-ASR] task {result.task_id} in progress - {result.state}...")
            await asyncio.sleep(2)
        elif result.state == ResultStateEnum.ERROR:
            logger.error(f"[BCut-ASR] task {result.task_id} has an error occurred!")
            raise AbortError("BCut-ASR task failed")
