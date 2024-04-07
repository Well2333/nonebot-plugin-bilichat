import asyncio
from io import BytesIO
from typing import Dict, Optional

from jieba.analyse.tfidf import TFIDF
from nonebot.log import logger
from wordcloud import WordCloud

from .config import plugin_config
from .lib.cache import BaseCache
from .lib.fonts_provider import get_font_async
from .optional import capture_exception  # type: ignore

tfidf = TFIDF()


async def wordcloud(cache: BaseCache) -> Optional[bytes]:
    try:
        logger.info(f"生成 {cache.id} 的词云")
        if not cache.content:
            return None
        elif not cache.jieba:
            loop = asyncio.get_running_loop()
            cache.jieba = await loop.run_in_executor(None, get_frequencies, cache.content)
            await cache.save()
        return await get_worldcloud_image(cache.jieba)
    except Exception as e:
        capture_exception()
        logger.exception(f"内容 {cache.id} 的词云生成失败: {e}")
        return None


def get_frequencies(msg_list) -> Dict[str, float]:
    text = "\n".join(msg_list)
    return dict(tfidf.extract_tags(text, topK=200, withWeight=True))


async def get_worldcloud_image(frequencies):
    wc = WordCloud(
        font_path=str(await get_font_async()),
        background_color="white",
        width=plugin_config.bilichat_word_cloud_size[0],
        height=plugin_config.bilichat_word_cloud_size[1],
        repeat=False,
        random_state=42,
    )
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, wc.generate_from_frequencies, frequencies)
    bio = BytesIO()
    wc.to_image().save(bio, format="JPEG")
    return bio.getvalue()
