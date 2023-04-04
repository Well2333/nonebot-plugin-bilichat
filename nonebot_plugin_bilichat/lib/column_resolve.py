from typing import Tuple

from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult

from ..model.exception import AbortError
from .bilibili_request import hc

XPATH = "//p//text() | //h1/text() | //h2/text() | //h3/text() | //h4/text() | //h5/text() | //h6/text()"


async def get_cv(cvid: str) -> Tuple[str, str]:
    cv = await hc.get(f"https://www.bilibili.com/read/cv{cvid}")
    if cv.status_code != 200:
        raise AbortError("专栏获取失败")
    cv.encoding = "utf-8"
    cv = cv.text

    http_parser: _Element = etree.fromstring(cv, etree.HTMLParser(encoding="utf-8"))
    title: str = http_parser.xpath('//h1[@class="title"]/text()')[0]
    main_article: _Element = http_parser.xpath('//div[@id="read-article-holder"]')[0]
    plist: _ElementUnicodeResult = main_article.xpath(XPATH)
    text_list = [text.strip() for text in plist if text.strip()]
    return title, "\n".join(text_list)
