import asyncio
from io import BytesIO
from typing import Dict

from jieba.analyse.tfidf import TFIDF
from wordcloud import WordCloud
from nonebot.log import logger

from ..model.cache import Cache
from ..model.exception import AbortError
from ..optional import capture_exception
from .fonts_provider import get_font

tfidf = TFIDF()


async def wordcloud(cache: Cache, cid: str = "0"):
    try:
        logger.info(f"Generation wordcloud of Video(Column) {cache.id}")
        if not cache.episodes[cid] or not cache.episodes[cid].content:
            return None
        elif not cache.episodes[cid].jieba:
            loop = asyncio.get_running_loop()
            cache.episodes[cid].jieba = await loop.run_in_executor(
                None, get_frequencies, cache.episodes[cid].content
            )
            cache.save()
        return await get_worldcloud_image(cache.episodes[cid].jieba)
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
