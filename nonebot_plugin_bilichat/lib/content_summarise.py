import re
from typing import List

from loguru import logger

from .openai import get_small_size_transcripts, get_user_prompt, openai_req
from ..model.cache import Cache
from ..model.exception import AbortError
from ..optional import capture_exception


async def subtitle_summarise(title: str, sub: List[str]):
    small_size_transcripts = get_small_size_transcripts(sub)
    prompt = get_user_prompt(title, small_size_transcripts)
    logger.debug(prompt)
    return await openai_req(prompt)


async def column_summarise(cv_title: str, cv_text: str):
    sentences = re.split(r"[，。；,.;\n]+", cv_text)
    small_size_transcripts = get_small_size_transcripts(sentences)
    prompt = get_user_prompt(cv_title, small_size_transcripts)
    logger.debug(prompt)
    return await openai_req(prompt)


async def openai_summarization(cache: Cache, cid: str = "0"):
    try:
        logger.info(f"Generation summary of Video(Column) {cache.id}")
        if not cache.episodes[cid] or not cache.episodes[cid].content:
            return None
        elif not cache.episodes[cid].openai:
            if cache.id[:2].lower() in ["bv", "av"]:
                ai_summary = await subtitle_summarise(
                    cache.title, cache.episodes[cid].content
                )
            elif cache.id[:2].lower() == "cv":
                ai_summary = await column_summarise(
                    cache.title, cache.episodes[cid].content[0]
                )
            else:
                raise ValueError(f"Illegal Video(Column) types {cache.id}")

            if ai_summary.summary:
                cache.episodes[cid].openai = ai_summary.summary
                cache.save()
            else:
                logger.warning(
                    f"Video(Column) {cache.id} summary failure: {ai_summary.raw}"
                )
                return None
        return cache.episodes[cid].openai  # TODO: add image type output
    except AbortError as e:
        logger.exception(f"Video(Column) {cache.id} summary aborted: {e}")
        return None
    except Exception as e:
        capture_exception()
        logger.exception(f"Video(Column) {cache.id} summary failed: {e}")
        return None
