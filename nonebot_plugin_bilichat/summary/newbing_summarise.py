import json
import random
import re
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

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
for count in range(5):
    try:
        bot = Chatbot(cookies=cookies, proxy=plugin_config.bilichat_openai_proxy)  # type: ignore
        logger.success("Bing chatbot init success")
        break
    except Exception:
        logger.error(f"Bing chatbot init failed, retrying {count+1}/5")


def get_small_size_transcripts(title: str, text_data: List[str]):
    prompt = f"请为视频“{title}”总结文案,开头用一整段文字简述视频的要点(大于40字符),\
随后总结2-6条视频的Bulletpoint(每条大于15字符),\
然后使用以下格式输出总结内容 ## 总结 \n ## 要点 \n - [Emoji] Bulletpoint\n\n,\
如果你无法找到相关的信息可以尝试自己总结,\
但请一定不要输出任何其他内容。视频文案的内容如下: "
    unique_texts = list(OrderedDict.fromkeys(text_data))
    if plugin_config.bilichat_newbing_token_limit > 0:
        while len(",".join(unique_texts)) + len(prompt) > plugin_config.bilichat_newbing_token_limit:
            unique_texts.pop(random.randint(0, len(unique_texts) - 1))
    return prompt + ",".join(unique_texts)


async def newbing_req(prompt: str) -> Optional[str]:
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

def newbing_summary_preprocess(ai_summary:str) -> str:
    """预处理（清洗）newbing输出的总结内容"""
    searchObj =   re.search(r'##\s+总结\s+(.*)##\s+要点\s+(.*)', ai_summary, re.S)  # 要求必须有“总结”和“要点”两个词，并且去除总结前面BB的内容
    if searchObj:
        summary = searchObj.group(1).strip()
        bulletpoint = searchObj.group(2).strip()
        bulletpoint = re.sub(r'\[\^\d+\^\]\s*', '', bulletpoint)  # 去除引用标记 eg. [^1^]

        """
            要点列表条目之间的换行数量不稳定，可能为 [0-n] 个
            为了避免丢失换行，先强制给它加上一个换行
            然后再合并多余的换行
        """
        bulletpoint = re.sub(r'-\s*\[(.+?)\]\s*', r'\n● \g<1> ', bulletpoint)
        bulletpoint = re.sub(r'\n+', r'\n', bulletpoint).strip()

        return f"## 总结\n{summary}\n\n## 要点\n{bulletpoint}"
    else:
        return ''

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

            ai_summary = newbing_summary_preprocess(ai_summary or '')

            # 如果为空则是拒绝回答
            if not ai_summary:
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
