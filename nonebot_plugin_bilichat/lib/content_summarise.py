import re
from typing import List

from loguru import logger

from .openai import get_small_size_transcripts, get_user_prompt, openai_req


async def subtitle_summarise(sub: List[str], title: str):
    """请求字幕总结"""
    small_size_transcripts = get_small_size_transcripts(sub)
    prompt = get_user_prompt(title, small_size_transcripts)
    logger.debug(prompt)
    return await openai_req(prompt)


async def column_summarise(cv_title: str, cv_text: str):
    """请求专栏总结"""
    sentences = re.split(r"[，。；,.;\n]+", cv_text)
    small_size_transcripts = get_small_size_transcripts(sentences)
    prompt = get_user_prompt(cv_title, small_size_transcripts)
    logger.debug(prompt)
    return await openai_req(prompt)
