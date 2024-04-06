from typing import List

from nonebot.log import logger

from ..config import plugin_config
from ..lib.cache import BaseCache
from ..lib.text_to_image import t2i
from ..model.exception import ProssesError
from ..optional import capture_exception  # type: ignore
from .openai import get_small_size_transcripts, get_summarise_prompt, openai_req


async def subtitle_summarise(title: str, sub: List[str]):
    small_size_transcripts = get_small_size_transcripts(title, sub)
    prompt = get_summarise_prompt(title, small_size_transcripts)
    logger.debug(prompt)
    return await openai_req(prompt)


async def column_summarise(cv_title: str, cv_text: List[str]):
    small_size_transcripts = get_small_size_transcripts(cv_title, cv_text)
    prompt = get_summarise_prompt(cv_title, small_size_transcripts, type_="专栏文章")
    logger.debug(prompt)
    return await openai_req(prompt)


async def openai_summarization(cache: BaseCache):
    try:
        if not cache.openai:
            if cache.id[:2].lower() in ["bv", "av"]:
                ai_summary = await subtitle_summarise(cache.title, cache.content)  # type: ignore
            elif cache.id[:2].lower() == "cv":
                ai_summary = await column_summarise(cache.title, cache.content)  # type: ignore
            else:
                raise ValueError(f"未知内容类型 {cache.id}")

            if ai_summary.response:
                cache.openai = ai_summary.response
                summary = ai_summary.response
                await cache.save()
            else:
                logger.warning(f"视频(专栏) {cache.id} 总结失败: {ai_summary.raw}")
                if plugin_config.bilichat_summary_ignore_null:
                    return
                else:
                    summary = f"视频(专栏) {cache.id} 总结失败: 响应内容异常\n{ai_summary.raw}"
        else:
            summary = cache.openai
        return await t2i(summary or "视频无法总结", plugin_config.bilichat_openai_model)
    except Exception as e:
        capture_exception()
        logger.exception(f"视频(专栏) {cache.id} 总结失败: {e}")
        if not plugin_config.bilichat_summary_ignore_null:
            raise ProssesError(f"视频(专栏) {cache.id} 总结失败: {e}")
