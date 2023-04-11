from nonebot.log import logger

from ..config import plugin_config
from ..model.cache import Cache

if plugin_config.bilichat_newbing_cookie:
    logger.info("Using newbing as summarization tool")
    from .newbing_summarise import newbing_summarization

if plugin_config.bilichat_openai_token:
    logger.info("Using openai as summarization tool")
    from .openai_summarise import openai_summarization


async def summarization(cache: Cache, cid: str = "0"):
    logger.info(f"Generation summary of Video(Column) {cache.id}")
    if not cache.episodes[cid] or not cache.episodes[cid].content:
        return "视频无有效字幕"

    if plugin_config.bilichat_newbing_cookie:
        summary, newbing_meaning = await newbing_summarization(cache, cid)
        if newbing_meaning or not plugin_config.bilichat_openai_token:
            return summary
        logger.error("newbing summary failed, retry with openai")

    if plugin_config.bilichat_openai_token:
        summary = await openai_summarization(cache, cid)
        return summary
