import asyncio
import re

from nonebot.log import logger
from playwright.async_api import Page, Response

try:
    from playwright._impl._errors import TimeoutError  # type: ignore
except ImportError:
    from playwright._impl._api_types import TimeoutError  # type: ignore

from ....config import plugin_config
from ....model.exception import AbortError, CaptchaAbortError, NotFindAbortError
from ....optional import capture_exception
from ...browser import get_new_page, mobile_style_js, network_requestfailed, pw_font_injecter


async def get_mobile_screenshot(page: Page, dynid: str):
    captcha = False

    async def detect_captcha(response: Response):
        nonlocal captcha
        logger.debug(f"[Captcha] Get captcha image url: {response.url}")
        if await response.body():
            captcha = True

    page.on(
        "response",
        lambda response: detect_captcha(response)
        if response.url.startswith("https://static.geetest.com/captcha_v3/")
        else None,
    )

    url = f"https://m.bilibili.com/dynamic/{dynid}"
    await page.set_viewport_size({"width": 460, "height": 780})
    await page.route(re.compile("^https://static.graiax/fonts/(.+)$"), pw_font_injecter)
    await page.goto(url, wait_until="networkidle")

    if captcha:
        raise CaptchaAbortError("[Captcha] 需要人机验证，配置 bilichat_bilibili_cookie 可以缓解此问题")

    if page.url == "https://m.bilibili.com/404":
        raise NotFindAbortError(f"{dynid} 动态不存在")

    await page.wait_for_load_state(state="domcontentloaded")
    await page.wait_for_selector(".b-img__inner, .dyn-header__author__face", state="visible")

    await page.add_script_tag(path=mobile_style_js)

    await page.wait_for_function("getMobileStyle('false')")

    await page.wait_for_load_state("networkidle")
    await page.wait_for_load_state("domcontentloaded")

    await page.wait_for_timeout(200)

    # 判断字体是否加载完成
    need_wait = ["imageComplete", "fontsLoaded"]
    await asyncio.gather(*[page.wait_for_function(f"{i}()") for i in need_wait])

    card = await page.query_selector(".opus-modules" if "opus" in page.url else ".dyn-card")
    assert card
    clip = await card.bounding_box()
    assert clip
    return page, clip


async def get_pc_screenshot(page: Page, dynid: str):
    """电脑端动态截图"""
    url = f"https://t.bilibili.com/{dynid}"
    await page.set_viewport_size({"width": 2560, "height": 1080})
    await page.goto(url, wait_until="networkidle")
    # 动态被删除或者进审核了
    if page.url == "https://www.bilibili.com/404":
        raise NotFindAbortError(f"{dynid} 动态不存在")
    card = await page.query_selector(".card")
    assert card
    clip = await card.bounding_box()
    assert clip
    bar = await page.query_selector(".bili-dyn-action__icon")
    assert bar
    bar_bound = await bar.bounding_box()
    assert bar_bound
    clip["height"] = bar_bound["y"] - clip["y"]
    return page, clip


async def screenshot(dynid: str, retry: bool = True, **kwargs):
    logger.info(f"正在截图动态：{dynid}")
    async with get_new_page(mobile_style=(plugin_config.bilichat_dynamic_style == "browser_mobile")) as page:
        await page.route(re.compile("^https://fonts.bbot/(.+)$"), pw_font_injecter)
        try:
            # page.on("requestfinished", network_request)
            page.on("requestfailed", network_requestfailed)
            if plugin_config.bilichat_dynamic_style == "browser_mobile":
                page, clip = await get_mobile_screenshot(page, dynid)
            else:
                page, clip = await get_pc_screenshot(page, dynid)
            clip["height"] = min(clip["height"], 32766)  # 限制高度
            if picture := await page.screenshot(clip=clip, full_page=True, type="jpeg", quality=98):
                return picture
        except CaptchaAbortError:
            raise
        except TimeoutError:
            if retry:
                logger.error(f"Dynamic {dynid} screenshot timed out, retrying...")
                return await screenshot(dynid, retry=False)
            raise AbortError(f"{dynid} 动态截图超时")
        except NotFindAbortError:
            if retry:
                logger.error(f"Dynamic {dynid} screenshot not found, retry in 3 secs...")
                await asyncio.sleep(3)
                return await screenshot(dynid, retry=False)
            raise
        except Exception as e:  # noqa
            if "waiting until" in str(e):
                if retry:
                    logger.error(f"Dynamic {dynid} screenshot timed out, retrying...")
                    await asyncio.sleep(3)
                    return await screenshot(dynid, retry=False)
                raise AbortError(f"{dynid} 动态截图超时")
            else:
                capture_exception()
                if retry:
                    logger.exception(f"Dynamic {dynid} screenshot not found, retrying...")
                    return await screenshot(dynid, retry=False)
                raise AbortError(f"{dynid} 动态截图失败")
