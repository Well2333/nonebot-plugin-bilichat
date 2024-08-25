from bilireq.utils import DEFAULT_HEADERS
from bilireq.utils import get as _get
from bilireq.utils import post as _post
from httpx import TimeoutException
from nonebot.log import logger

from ...config import plugin_config
from .auth import AuthManager


async def get(url: str, **kwargs):
    """
    发送 GET 请求

    Args:
        url: 请求链接
        **kwargs: 其他参数
    """
    e = None
    for i in range(plugin_config.bilichat_neterror_retry):
        try:
            return await _get(url, **kwargs)
        except TimeoutException as e:
            logger.error(f"请求 {url} 超时: {e}, 重试第 {i + 1}/{plugin_config.bilichat_neterror_retry} 次")
    raise e or TimeoutException(f"请求 {url} 超时")


async def post(url: str, **kwargs):
    """
    发送 POST 请求

    Args:
        url: 请求链接
        **kwargs: 其他参数
    """
    e = None
    for i in range(plugin_config.bilichat_neterror_retry):
        try:
            return await _post(url, **kwargs)
        except TimeoutException as e:
            logger.error(f"请求 {url} 超时: {e}, 重试第 {i + 1}/{plugin_config.bilichat_neterror_retry} 次")
    raise e or TimeoutException(f"请求 {url} 超时")


async def get_b23_url(burl: str) -> str:
    """
    b23 链接转换

    Args:
        burl: 需要转换的 BiliBili 链接
    """
    url = "https://api.bilibili.com/x/share/click"
    data = {
        "build": 6700300,
        "buvid": 0,
        "oid": burl,
        "platform": "android",
        "share_channel": "COPY",
        "share_id": "public.webview.0.0.pv",
        "share_mode": 3,
    }
    resp = await post(url, data=data)
    logger.debug(resp)
    return resp["content"]


async def get_user_space_info(uid: int):
    """
    获取用户空间信息
    """
    url = "https://app.bilibili.com/x/v2/space"
    params = {
        "vmid": uid,
        "build": 6840300,
        "ps": 1,
    }
    return await get(url, params=params, cookies=AuthManager.get_cookies())


async def get_player(aid: int, cid: int):
    """
    获取视频播放器信息
    """
    url = "https://api.bilibili.com/x/player/v2"
    params = {
        "aid": aid,
        "cid": cid,
    }
    return await get(url, params=params, cookies=AuthManager.get_cookies())


async def get_dynamic(dyn_id: str):
    """
    获取动态信息
    """
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?timezone_offset=-480&id={dyn_id}"
    headers = {
        "Referer": f"https://t.bilibili.com/{dyn_id}",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq"
        ),
    }
    return await get(url=url, headers=headers, cookies=AuthManager.get_cookies())


async def search_user(keyword: str):
    """
    搜索用户
    """
    url = "https://app.bilibili.com/x/v2/search/type"
    data = {"build": "6840300", "keyword": keyword, "type": "2", "ps": 5}

    return await get(url, params=data, cookies=AuthManager.get_cookies())


async def get_user_dynamics(uid: int):
    """根据 UID 批量获取直播间信息"""
    url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space"
    data = {"host_mid": uid}
    headers = {
        **DEFAULT_HEADERS,
        **{
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 uacq"
            ),
            "Origin": "https://space.bilibili.com",
            "Referer": f"https://space.bilibili.com/{uid}/dynamic",
        },
    }
    return await get(url, params=data, headers=headers, cookies=AuthManager.get_cookies())
