import asyncio
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from loguru import logger
from nonebot_plugin_htmlrender.browser import get_browser
from playwright._impl._api_types import TimeoutError
from playwright.async_api import Page, Request, Response

from ....config import plugin_config
from ....model.exception import AbortError, CaptchaAbortError, NotFindAbortError
from ....optional import capture_exception
from ...browser import pw_font_injecter
from ...store import static_dir

browser_cookies_file = Path(plugin_config.bilichat_bilibili_cookie or "")
mobile_style_js = static_dir.joinpath("browser", "mobile_style.js")


@asynccontextmanager
async def get_new_page(device_scale_factor: float = 2, **kwargs) -> AsyncIterator[Page]:
    browser = await get_browser()
    if plugin_config.bilichat_dynamic_style == "browser_mobile":
        kwargs["user_agent"] = (
            "5.0 (Linux; Android 13; SM-A037U) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36  uacq"
        )
    page = await browser.new_page(device_scale_factor=device_scale_factor, **kwargs)
    if browser_cookies_file.exists() and browser_cookies_file.is_file():
        if browser_cookies := json.loads(browser_cookies_file.read_bytes()):
            logger.debug("正在为浏览器添加cookies")
            await page.context.add_cookies(
                [
                    {
                        "domain": cookie["domain"],
                        "name": cookie["name"],
                        "path": cookie["path"],
                        "value": cookie["value"],
                    }
                    for cookie in browser_cookies
                ]
            )
    try:
        yield page
    finally:
        await page.close()


async def refresh_cookies(page: Page):
    storage_state = await page.context.storage_state()
    if cookies := storage_state.get("cookies"):
        browser_cookies_file.write_text(json.dumps(cookies))


async def network_request(request: Request):
    url = request.url
    method = request.method
    response = await request.response()
    if response:
        status = response.status
        timing = "%.2f" % response.request.timing["responseEnd"]
    else:
        status = "/"
        timing = "/"
    logger.debug(f"[Response] [{method} {status}] {timing}ms <<  {url}")


def network_requestfailed(request: Request):
    url = request.url
    fail = request.failure
    method = request.method
    logger.warning(f"[RequestFailed] [{method} {fail}] << {url}")


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


async def screenshot(dynid: str, retry: bool = True):
    logger.info(f"正在截图动态：{dynid}")
    async with get_new_page() as page:
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
                await refresh_cookies(page)
                return picture
        except CaptchaAbortError:
            raise
        except TimeoutError:
            if retry:
                logger.error(f"Dynamic {dynid} screenshot timed out, retrying...")
                return await screenshot(dynid, False)
            raise AbortError(f"{dynid} 动态截图超时")
        except NotFindAbortError:
            if retry:
                logger.error(f"Dynamic {dynid} screenshot not found, retry in 3 secs...")
                await asyncio.sleep(3)
                return await screenshot(dynid, False)
            raise
        except Exception as e:  # noqa
            if "waiting until" in str(e):
                if retry:
                    logger.error(f"Dynamic {dynid} screenshot timed out, retrying...")
                    await asyncio.sleep(3)
                    return await screenshot(dynid, False)
                raise AbortError(f"{dynid} 动态截图超时")
            else:
                capture_exception()
                if retry:
                    logger.exception(f"Dynamic {dynid} screenshot not found, retrying...")
                    return await screenshot(dynid, False)
                raise AbortError(f"{dynid} 动态截图失败")
