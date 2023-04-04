import asyncio

from io import BytesIO
from wordcloud import WordCloud
from jieba.analyse.tfidf import TFIDF


from .fonts_provider import get_font

tfidf = TFIDF()


def get_frequencies(msg_list) -> dict[str, float]:
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
    await asyncio.to_thread(wc.generate_from_frequencies, frequencies)
    bio = BytesIO()
    wc.to_image().save(bio, format="JPEG")
    return bio.getvalue()
