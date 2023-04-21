import json
import random
import re
from collections import OrderedDict
from pathlib import Path
from typing import List, Dict

from EdgeGPT import Chatbot, ConversationStyle
from nonebot.log import logger

from ..config import plugin_config
from ..lib.store import BING_APOLOGY
from ..model.cache import Cache
from ..model.exception import AbortError
from ..optional import capture_exception  # type: ignore
from .text_to_image import rich_text2image

cookies = json.loads(Path(plugin_config.bilichat_newbing_cookie).read_text("utf-8"))  # type: ignore
logger.info("Try init bing chatbot")
init = False
for count in range(5):
    try:
        bot = Chatbot(cookies=cookies, proxy=plugin_config.bilichat_openai_proxy)  # type: ignore
        logger.success("Bing chatbot init success")
        init = True
        break
    except Exception as e:
        logger.error(f"Bing chatbot init failed, retrying {count+1}/5: {e}")

if not init:
    raise RuntimeError("Bing chatbot init failed")


def get_small_size_transcripts(title: str, text_data: List[str]):
    prompt = (
        "使用以下Markdown模板为我总结视频字幕数据，除非字幕中的内容无意义，或者内容较少无法总结，或者未提供字幕数据，或者无有效内容，你就不使用模板回复，只回复“无意义”：\
        ## 概述\
        {内容，尽可能精简总结内容不要太详细}\
        ## 要点\
        - {使用不重复并合适的emoji，仅限一个，禁止重复} {内容不换行大于15字，可多项，条数与有效内容数量呈正比}\
        不要随意翻译任何内容。仅使用中文总结。\
        不说与总结无关的其他内容，你的回复仅限固定格式提供的“概述”和“要点”两项。"
        + f"视频标题为“{title}”，视频字幕数据如下，立刻开始总结："
    )
    unique_texts = list(OrderedDict.fromkeys(text_data))
    if plugin_config.bilichat_newbing_token_limit > 0:
        while len(",".join(unique_texts)) + len(prompt) > plugin_config.bilichat_newbing_token_limit:
            unique_texts.pop(random.randint(0, len(unique_texts) - 1))
    return prompt + ",".join(unique_texts)


def newbing_summary_preprocess(ai_summary: str):
    # https://github.com/djkcyl/nonebot-plugin-bilichat/pull/18
    """Pre-process (clean) the summary content of newbing output"""
    if search_obj := re.search(r"##\s+概述\s+(.*)##\s+要点\s+(.*)", ai_summary, re.S):
        # content separation
        summary = search_obj[1].strip()
        bulletpoint = search_obj[2].strip()
        # remove reference like [^1^]
        summary = re.sub(r"\[\^\d+\^\]\s*", "", summary)
        bulletpoint = re.sub(r"\[\^\d+\^\]\s*", "", bulletpoint)
        # reset line breaks
        bulletpoint = re.sub(r"-\s*\[(.+?)\]\s*", r"\n● \g<1> ", bulletpoint)
        bulletpoint = re.sub(r"\n+", r"\n", bulletpoint).strip()
        # final output
        bing_summary = f"## 总结\n{summary}\n\n## 要点\n{bulletpoint}"
        logger.info(f"Newbing summary: \n{bing_summary}")
        return bing_summary
    else:
        logger.debug(f"Newbing output is meaningless: \n{ai_summary}")
        return None


async def newbing_req(prompt: str):
    logger.debug(f"prompt have {len(prompt)} chars")
    ans = await bot.ask(
        prompt=prompt,
        conversation_style=ConversationStyle.creative,
        wss_link="wss://sydney.bing.com/sydney/ChatHub",
    )
    await bot.reset()
    logger.debug(ans)
    bing_resp: Dict = ans["item"]["messages"][1]
    return (
        newbing_summary_preprocess(bing_resp.get("text", ""))
        if plugin_config.bilichat_newbing_preprocess
        else bing_resp.get("text", None)
    )


async def newbing_summarization(cache: Cache, cid: str = "0"):
    meaning = False
    try:
        if not cache.episodes[cid].newbing:
            if cache.id[:2].lower() in ["bv", "av"]:
                ai_summary = await newbing_req(get_small_size_transcripts(cache.title, cache.episodes[cid].content))
            elif cache.id[:2].lower() == "cv":
                ai_summary = await newbing_req(
                    get_small_size_transcripts(cache.title, re.split(r"[，。；,.;\n]+", cache.episodes[cid].content[0]))
                )
            else:
                raise ValueError(f"Illegal Video(Column) types {cache.id}")

            # 如果为空则是拒绝回答
            if ai_summary is None:
                return BING_APOLOGY.read_bytes(), False
            # 大于 100 认为有意义
            elif len(ai_summary) > 100:
                cache.episodes[cid].newbing = ai_summary
                cache.save()
                meaning = True
            # 小于 100 认为无意义
            else:
                logger.warning(f"Video(Column) {cache.id} summary failure")
                cache.episodes[cid].newbing = f"视频(专栏) {cache.id} 总结失败: {ai_summary}"
        else:
            meaning = True
            logger.info("Using cached newbing summarization")

        if img := await rich_text2image(cache.episodes[cid].newbing or "视频无法总结", "new Bing(testing)"):
            return img, meaning
        else:
            return f"总结图片生成失败, 直接发送原文:\n{cache.episodes[cid].newbing}", meaning
    except AbortError as e:
        logger.exception(f"Video(Column) {cache.id} summary aborted: {e}")
        return f"视频(专栏) {cache.id} 总结中止: {e}", False
    except Exception as e:
        capture_exception()
        logger.exception(f"Video(Column) {cache.id} summary failed: {e}")
        return f"视频(专栏) {cache.id} 总结失败: {e}", False
