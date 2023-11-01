from typing import Optional

from httpx._exceptions import TimeoutException
from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult
from nonebot.log import logger
from pydantic import BaseModel

from ..lib.bilibili_request import get_b23_url, hc
from ..lib.bilibili_request.auth import get_cookies
from ..lib.cache import BaseCache, Cache
from ..lib.draw.column import draw_column
from ..model.arguments import Options
from ..model.exception import AbortError

XPATH = "//p//text() | //h1/text() | //h2/text() | //h3/text() | //h4/text() | //h5/text() | //h6/text()"


class Column(BaseModel):
    id: int
    """专栏cv号"""
    title: str
    """专栏标题"""
    url: str
    """b23 链接"""
    cache: BaseCache
    
    @property
    def bili_id(self) -> str:
        return f"cv{self.id}"

    @classmethod
    async def from_id(cls, bili_number: str, options: Optional[Options] = None):
        try:
            cvid = bili_number[2:]
            cv = await hc.get(f"https://www.bilibili.com/read/cv{cvid}", cookies=get_cookies())
            if cv.status_code != 200:
                logger.debug(f"cv{cvid} status code: {cv.status_code} content: \n{cv.content}")
                raise AbortError("未找到此专栏，可能已被 UP 主删除。")
            cv.encoding = "utf-8"
            cv = cv.text
            http_parser: _Element = etree.fromstring(cv, etree.HTMLParser(encoding="utf-8"))
            cv_title: str = http_parser.xpath('//h1[@class="title"]/text()')[0]
            main_article: _Element = http_parser.xpath('//div[@id="read-article-holder"]')[0]
            plist: _ElementUnicodeResult = main_article.xpath(XPATH)
            cv_text = [text.strip() for text in plist if text.strip()]
            b23_url = await get_b23_url(f"https://www.bilibili.com/read/cv{cvid}")
        except AbortError:
            raise
        except TimeoutException:
            logger.warning("Column parsing API call timeout")
            raise AbortError(f"{bili_number} 专栏信息生成超时，请稍后再试。")
        except Exception as e:  # noqa
            logger.exception(f"Column parsing API call error: {e}")
            raise AbortError(f"专栏解析 API 调用出错：{e}") from e

        if options:
            if options.no_cache:
                logger.debug(f"parameter --no-cache of cv{cvid} detected, using temporary cache")
                cache = BaseCache(id=f"cv{cvid}", title=cv_title, content=cv_text)
            elif options.refresh:
                logger.debug(f"parameter --refresh of cv{cvid} detected, remove cache")
                cache = Cache(id=f"cv{cvid}", title=cv_title, content=cv_text)
                await cache.save()
            else:
                cache = await Cache.load(f"cv{cvid}", title=cv_title, content=cv_text)
        else:
            cache = await Cache.load(f"cv{cvid}", title=cv_title, content=cv_text)

        content = cls(id=int(cvid), title=cv_title, url=b23_url, cache=cache)
        return content

    async def get_subtitle(self):
        return self.cache.content

    async def get_image(self, style: str):
        return await draw_column(cvid=self.id)
