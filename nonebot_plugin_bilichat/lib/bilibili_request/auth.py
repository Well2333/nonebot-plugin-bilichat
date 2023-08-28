import json
from pathlib import Path
from typing import Any, Dict

from bilireq.auth import Auth
from nonebot import get_driver
from nonebot.log import logger

from ...config import plugin_config
from ..store import cache_dir

gRPC_Auth: Auth = Auth()
bili_grpc_auth = cache_dir.joinpath("bili_grpc_auth.json")
bili_grpc_auth.touch(0o700, exist_ok=True)


async def login_from_cache() -> bool:
    global gRPC_Auth
    try:
        data = json.loads(bili_grpc_auth.read_bytes())
        gRPC_Auth.update(data)
        gRPC_Auth = await gRPC_Auth.refresh()
        bili_grpc_auth.write_text(json.dumps(gRPC_Auth.data))
    except Exception as e:
        logger.error(f"缓存登录失败，请使用验证码登录: {e}")
        gRPC_Auth = Auth()
        return False
    else:
        logger.success("缓存登录成功")
        return True


browser_cookies: Dict = {}
if plugin_config.bilichat_bilibili_cookie:
    browser_cookies_file = Path(plugin_config.bilichat_bilibili_cookie)
else:
    browser_cookies_file = cache_dir.joinpath("bilibili_browser_cookies.json")


def load_browser_cookies():
    global browser_cookies
    try:
        browser_cookies = json.loads(browser_cookies_file.read_bytes())
        if isinstance(browser_cookies, list):
            browser_cookies = {cookie["name"]: cookie["value"] for cookie in browser_cookies}
            dump_browser_cookies()
    except Exception:
        browser_cookies = {}


def dump_browser_cookies():
    browser_cookies_file.write_text(json.dumps(browser_cookies, ensure_ascii=False, indent=2))


def get_cookies() -> Dict[str, Any]:
    if gRPC_Auth:
        return gRPC_Auth.cookies
    if browser_cookies:
        return browser_cookies
    return {}


load_browser_cookies()
get_driver().on_startup(login_from_cache)
