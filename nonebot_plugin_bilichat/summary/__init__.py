from nonebot.log import logger

from ..config import plugin_config
from ..lib.cache import BaseCache
from ..model.exception import AbortError
from .openai_summarise import openai_summarization


async def summarization(cache: BaseCache):
    # summarization will be returned in the following priority
    # openai cache -> newbing cache -> newbing new sum -> openai new sum
    logger.info(f"Generation summary of Video(Column) {cache.id}")
    if not cache.content:
        raise AbortError("视频无有效字幕")

    # try openai cache
    if plugin_config.bilichat_openai_token:
        return await openai_summarization(cache)  # type: ignore
