import asyncio
import concurrent.futures
import json
import random
import re
from collections import OrderedDict
from pathlib import Path
from typing import List, Literal

from EdgeGPT import Chatbot, ConversationStyle
from nonebot.log import logger

from ..config import plugin_config
from ..lib.store import BING_APOLOGY
from ..model.cache import Cache
from ..model.exception import AbortError, BingChatResponseException
from ..model.newbing import BingChatResponse
from ..optional import capture_exception  # type: ignore
from .text_to_image import t2i

cookies = (
    {}
    if plugin_config.bilichat_newbing_cookie == "no_login"
    else json.loads(Path(plugin_config.bilichat_newbing_cookie).read_text("utf-8"))  # type: ignore
)

bot = None


def init_chatbot(total_count: int = 5):
    global bot
    for count in range(total_count):
        try:
            bot = Chatbot(cookies=cookies, proxy=plugin_config.bilichat_openai_proxy)  # type: ignore
            logger.success("Bing chatbot init success")
            return
        except Exception as e:
            logger.error(f"Bing chatbot init failed, retrying {count+1}/5: {e}")
    raise RuntimeError("Bing chatbot init failed")


logger.info("Try init bing chatbot")
init_chatbot()
assert bot, "Bing chatbot init failed"


def get_small_size_transcripts(title: str, text_data: List[str], type_: Literal["视频字幕", "专栏文章"] = "视频字幕"):
    prompt = (
        f"使用以下Markdown模板为我总结{type_}数据，除非{type_[2:]}中的内容无意义，或者内容较少无法总结，或者未提供{type_[2:]}数据，或者无有效内容，你就不使用模板回复，只回复“无意义”："
        + "## 概述\
        {内容，尽可能精简总结内容不要太详细}\
        ## 要点\
        - {使用不重复并合适的emoji，仅限一个，禁止重复} {内容不换行大于15字，可多项，条数与有效内容数量呈正比}\
        不要随意翻译任何内容。仅使用中文总结。\
        不说与总结无关的其他内容，你的回复仅限固定格式提供的“概述”和“要点”两项。"
        + f"{type_[:2]}标题为“{title}”，{type_}数据如下，立刻开始总结："
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
        # reset line breaks
        bulletpoint = re.sub(r"-\s*\[(.+?)\]\s*", r"\n● \g<1> ", bulletpoint)
        bulletpoint = re.sub(r"\n+", r"\n", bulletpoint).strip()
        # final output
        bing_summary = f"## 总结\n{summary}\n\n## 要点\n{bulletpoint}"
        logger.info(f"Newbing summary: \n{bing_summary}")
        return bing_summary
    else:
        logger.debug(f"Newbing output is meaningless: \n{ai_summary}")
        return ""


async def newbing_req(prompt: str, _is_retry: bool = False):
    logger.debug(f"prompt have {len(prompt)} chars")
    try:
        if not isinstance(bot, Chatbot):
            raise TypeError
        raw = await bot.ask(
            prompt=prompt,
            conversation_style=ConversationStyle.creative,
            wss_link="wss://sydney.bing.com/sydney/ChatHub",
        )
        await bot.reset()
        res = BingChatResponse(raw=raw)
        return (
            newbing_summary_preprocess(res.content_answer)
            if plugin_config.bilichat_newbing_preprocess
            else res.content_answer
        )
    except BingChatResponseException as e:
        raise e
    except Exception as e:
        if _is_retry:
            raise e
        # 如果没有重试，则刷新 bot 后重试
        logger.warning(f"newbing summary failed (Retrying): {e}")
        try:
            logger.info("Try init bing chatbot")
            loop = asyncio.get_running_loop()
            executor = concurrent.futures.ThreadPoolExecutor()
            await loop.run_in_executor(executor, init_chatbot)
            assert bot, "Bing chatbot init failed"
        except Exception:
            return "newbing chatbot 失效，请检查 cookie 文件是否过期"
        return await newbing_req(prompt, _is_retry=True)


async def newbing_summarization(cache: Cache, cid: str = "0"):
    meaning = False
    try:
        if not cache.episodes[cid].newbing:
            if cache.id[:2].lower() in ["bv", "av"]:
                ai_summary = await newbing_req(get_small_size_transcripts(cache.title, cache.episodes[cid].content))
            elif cache.id[:2].lower() == "cv":
                ai_summary = await newbing_req(
                    get_small_size_transcripts(cache.title, cache.episodes[cid].content, type_="专栏文章")
                )
            else:
                raise ValueError(f"Illegal Video(Column) types {cache.id}")

            # 大于 50 认为有意义
            if len(ai_summary) > 50:
                cache.episodes[cid].newbing = ai_summary
                cache.save()
                meaning = True
            # 小于 50 认为无意义
            else:
                logger.warning(f"Video(Column) {cache.id} summary failure")
                return f"视频(专栏) {cache.id} 总结失败: {ai_summary}", False

        elif cache.episodes[cid].newbing == "Refusal to answer":
            return BING_APOLOGY.read_bytes(), False
        else:
            meaning = True
            logger.info("Using cached newbing summarization")

        return await t2i(cache.episodes[cid].newbing or "视频无法总结", "new Bing"), meaning
    except BingChatResponseException as e:
        logger.error(f"Video(Column) {cache.id} summary failed: {e}")
        cache.episodes[cid].newbing = "Refusal to answer"
        cache.save()
        return BING_APOLOGY.read_bytes(), False
    except AbortError as e:
        logger.exception(f"Video(Column) {cache.id} summary aborted: {e}")
        return f"视频(专栏) {cache.id} 总结中止: {e}", False
    except Exception as e:
        capture_exception()
        logger.exception(f"Video(Column) {cache.id} summary failed: {e}")
        return f"视频(专栏) {cache.id} 总结失败: {e}", False
