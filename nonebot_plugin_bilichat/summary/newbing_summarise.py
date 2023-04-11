import json
import random
import re
from collections import OrderedDict
from pathlib import Path
from typing import List

from EdgeGPT import Chatbot, ConversationStyle
from nonebot.log import logger

from ..config import plugin_config
from ..model.cache import Cache
from ..model.exception import AbortError
from ..optional import capture_exception  # type: ignore
from .text_to_image import rich_text2image
from ..lib.store import BING_APOLOGY

cookies = json.loads(Path(plugin_config.bilichat_newbing_cookie).read_text("utf-8"))  # type: ignore
logger.info("Try init bing chatbot")
for count in range(5):
    try:
        bot = Chatbot(cookies=cookies, proxy=plugin_config.bilichat_openai_proxy)  # type: ignore
        logger.success("Bing chatbot init success")
        break
    except Exception:
        logger.error(f"Bing chatbot init failed, retrying {count+1}/5")



def get_small_size_transcripts(title: str, text_data: List[str]):
    prompt = f"请为视频“{title}”总结文案,开头简述要点(大于40字符),\
随后总结2-6条视频的Bulletpoint(每条大于15字符),\
然后使用以下格式输出总结内容 ## 总结 \n ## 要点 \n - [Emoji] Bulletpoint\n\n,\
如果你无法找到相关的信息可以尝试自己总结,\
但请一定不要输出任何其他内容。视频文案的内容如下: "
    unique_texts = list(OrderedDict.fromkeys(text_data))
    if plugin_config.bilichat_newbing_token_limit > 0:
        while len(",".join(unique_texts)) + len(prompt) > plugin_config.bilichat_newbing_token_limit:
            unique_texts.pop(random.randint(0, len(unique_texts) - 1))
    return prompt + ",".join(unique_texts)


async def newbing_req(prompt: str):
    logger.debug(f"prompt have {len(prompt)} chars")
    ans = await bot.ask(
        prompt=prompt,
        conversation_style=ConversationStyle.creative,
        wss_link="wss://sydney.bing.com/sydney/ChatHub",
    )
    await bot.reset()
    logger.debug(ans)
    bing_resp = ans["item"]["messages"][1]
    return None if bing_resp["contentOrigin"] == "Apology" else bing_resp["text"]



async def newbing_summarization(cache: Cache, cid: str = "0"):
    try:
        logger.info(f"Generation summary of Video(Column) {cache.id}")
        if not cache.episodes[cid] or not cache.episodes[cid].content:
            return "视频无有效字幕"
        elif not cache.episodes[cid].newbing:
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
                return BING_APOLOGY.read_bytes()
            # 大于 100 认为有意义
            elif len(ai_summary) > 100:
                cache.episodes[cid].newbing = ai_summary
                cache.save()
            # 小于 100 认为无意义
            else:
                logger.warning(f"Video(Column) {cache.id} summary failure")
                cache.episodes[cid].newbing = f"视频(专栏) {cache.id} 总结失败: {ai_summary}"

        if img := await rich_text2image(cache.episodes[cid].newbing or "视频无法总结"):
            return img
        else:
            return f"总结图片生成失败, 直接发送原文:\n{cache.episodes[cid].newbing}"
    except AbortError as e:
        logger.exception(f"Video(Column) {cache.id} summary aborted: {e}")
        return f"视频(专栏) {cache.id} 总结中止: {e}"
    except Exception as e:
        capture_exception()
        logger.exception(f"Video(Column) {cache.id} summary failed: {e}")
        return f"视频(专栏) {cache.id} 总结失败: {e}"
