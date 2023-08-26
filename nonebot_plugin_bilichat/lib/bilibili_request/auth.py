import json

from bilireq.auth import Auth
from nonebot import get_driver
from nonebot.log import logger

from ..store import cache_dir

gRPC_Auth: Auth = Auth()
bili_grpc_auth = cache_dir.joinpath("bili_grpc_auth.json")
bili_grpc_auth.touch(0o700, exist_ok=True)

async def login_from_cache() -> bool:
    global gRPC_Auth
    try:
        data = json.loads(bili_grpc_auth.read_bytes())
        gRPC_Auth.update(data)
        await gRPC_Auth.refresh()
        logger.debug(gRPC_Auth.data)
    except Exception as e:
        logger.error(f"缓存登录失败，请使用验证码登录: {e}")
        gRPC_Auth = Auth()
        return False
    else:
        logger.success("缓存登录成功")
        return True


get_driver().on_startup(login_from_cache)

# browser_cookies: Dict = {}
# browser_cookies_file = Path(plugin_config.bilichat_bilibili_cookie or "")
#
#
# def load_browser_cookies():
#     global browser_cookies
#     browser_cookies = json.loads(browser_cookies_file.read_bytes())
#
#
# def dump_browser_cookies():
#     browser_cookies_file.write_text(json.dumps(browser_cookies, ensure_ascii=False, indent=4))
