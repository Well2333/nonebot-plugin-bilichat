import asyncio
import re

from nonebot.log import logger

try:
    from playwright._impl._errors import TimeoutError  # type: ignore
except ImportError:
    from playwright._impl._api_types import TimeoutError  # type: ignore

from ....model.exception import AbortError, CaptchaAbortError, NotFindAbortError
from ....optional import capture_exception
from ...browser import get_new_page, network_requestfailed, pw_font_injecter


async def screenshot(cvid: str, retry: bool = True, **kwargs):
    logger.info(f"正在截图专栏：{cvid}")
    async with get_new_page() as page:
        await page.route(re.compile("^https://fonts.bbot/(.+)$"), pw_font_injecter)
        try:
            page.on("requestfailed", network_requestfailed)
            url = f"https://www.bilibili.com/read/cv{cvid}"
            await page.set_viewport_size({"width": 1080, "height": 1080})
            await page.goto(url, wait_until="networkidle")
            # 专栏被删除或者进审核了
            if page.url == "https://www.bilibili.com/404":
                raise NotFindAbortError(f"cv{cvid} 专栏不存在")
            content = await page.query_selector("#app > div > div.article-container > div.article-container__content")
            assert content
            clip = await content.bounding_box()
            assert clip
            clip["y"] = clip["y"] - 30  # 增加顶部白边
            clip["height"] = min(clip["height"] + 30, 32766)  # 增加顶部白边，限制高度
            clip["x"] = clip["x"] + 40  # 移除左右一半的白边
            clip["width"] = clip["width"] - 80  # 移除左右一半的白边
            await page.set_viewport_size({"width": 1080, "height": int(clip["height"] + 720)})
            await asyncio.sleep(1)
            await page.wait_for_load_state(state="networkidle")
            if picture := await page.screenshot(clip=clip, full_page=True, type="jpeg", quality=98):
                return picture
        except CaptchaAbortError:
            raise
        except TimeoutError:
            if retry:
                logger.error(f"Column cv{cvid} screenshot timed out, retrying...")
                return await screenshot(cvid, retry=False)
            raise AbortError(f"cv{cvid} 专栏截图超时")
        except NotFindAbortError:
            if retry:
                logger.error(f"Column cv{cvid} screenshot not found, retry in 3 secs...")
                await asyncio.sleep(3)
                return await screenshot(cvid, retry=False)
            raise
        except Exception as e:  # noqa
            if "waiting until" in str(e):
                if retry:
                    logger.error(f"Column cv{cvid} screenshot timed out, retrying...")
                    await asyncio.sleep(3)
                    return await screenshot(cvid, retry=False)
                raise AbortError(f"cv{cvid} 专栏截图超时")
            else:
                capture_exception()
                if retry:
                    logger.exception(f"Column cv{cvid} screenshot not found, retrying...")
                    return await screenshot(cvid, retry=False)
                raise AbortError(f"cv{cvid} 专栏截图失败")
