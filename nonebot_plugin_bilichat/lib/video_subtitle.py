import httpx
import asyncio

from loguru import logger
from typing import Optional
from sentry_sdk import capture_exception

from ..core.bot_config import BotConfig
from ..model.exception import AbortError
from ..model.bcut_asr import ResultStateEnum

from .bcut_asr import BcutASR
from .bilibili_request import get_player, hc
from .bilibili_request import grpc_get_playview


async def get_subtitle_url(aid: int, cid: int) -> Optional[str]:
    video_player = await get_player(aid, cid)
    subtitles_raw: list[dict] = video_player["subtitle"]["subtitles"]
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


async def get_subtitle(aid: int, cid: int) -> list[str]:
    subtitle_url = await get_subtitle_url(aid, cid)
    if subtitle_url:
        logger.debug(subtitle_url)
        subtitle = await hc.get(f"https:{subtitle_url}")
        if subtitle.status_code != 200:
            logger.warning(f"字幕获取失败：{aid} {cid}，状态码：{subtitle.status_code}，内容：{subtitle.text}")
            raise AbortError("字幕下载失败")
        logger.info(f"字幕获取成功：{aid} {cid}")
    elif BotConfig.Bilibili.use_bcut_asr:
        logger.info(f"字幕获取失败，尝试使用 BCut-ASR：{aid} {cid}")
        playview = await grpc_get_playview(aid, cid)
        if not playview.video_info.dash_audio:
            raise AbortError("视频无音频流")
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
        try:
            asr = await get_bcut_asr(audio)
        except Exception as e:
            logger.exception("BCut-ASR 识别失败")
            capture_exception()
            raise AbortError("BCut-ASR 识别失败") from e
        return [x.transcript for x in asr]
    else:
        raise AbortError("未找到字幕且未开启 AI 语音识别")
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
            logger.info(f"[BCut-ASR] 任务 {result.task_id} 正在进行中 - {result.state}...")
            await asyncio.sleep(2)
        elif result.state == ResultStateEnum.ERROR:
            logger.error(f"[BCut-ASR] 任务 {result.task_id} 发生错误！")
            raise AbortError("语音识别出错")
