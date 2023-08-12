import asyncio
from io import BytesIO
from typing import Dict

from jieba.analyse.tfidf import TFIDF
from nonebot.log import logger
from wordcloud import WordCloud

from ..lib.fonts_provider import get_font
from ..lib.cache import BaseCache
from ..model.exception import AbortError
from ..optional import capture_exception  # type: ignore

tfidf = TFIDF()


async def wordcloud(cache: BaseCache):
    try:
        logger.info(f"Generation wordcloud of Video(Column) {cache.id}")
        if not cache.content:
            return None
        elif not cache.jieba:
            loop = asyncio.get_running_loop()
            cache.jieba = await loop.run_in_executor(None, get_frequencies, cache.content)
            await cache.save()
        return await get_worldcloud_image(cache.jieba)
    except AbortError as e:
        logger.exception(f"Video(Column) {cache.id} wordcloud generation aborted: {e}")
        return None
    except Exception as e:
        capture_exception()
        logger.exception(f"Video(Column) {cache.id} wordcloud generation failed: {e}")
        return None


def get_frequencies(msg_list) -> Dict[str, float]:
    text = "\n".join(msg_list)
    return dict(tfidf.extract_tags(text, topK=200, withWeight=True))


async def get_worldcloud_image(frequencies):
    wc = WordCloud(
        font_path=str(await get_font()),
        background_color="white",
        width=1000,
        height=800,
        repeat=False,
        random_state=42,
    )
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, wc.generate_from_frequencies, frequencies)
    bio = BytesIO()
    wc.to_image().save(bio, format="JPEG")
    return bio.getvalue()
