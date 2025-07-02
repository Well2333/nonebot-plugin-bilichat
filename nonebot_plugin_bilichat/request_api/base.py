import httpx
from httpx import AsyncClient
from nonebot.log import logger
from packaging.version import Version
from yarl import URL

from nonebot_plugin_bilichat.config import __version__
from nonebot_plugin_bilichat.lib.tools import shorten_long_items
from nonebot_plugin_bilichat.model.exception import APIError, RequestError
from nonebot_plugin_bilichat.model.request_api import Account, Content, Dynamic, LiveRoom, Note, SearchUp, VersionInfo

MINIMUM_API_VERSION = Version("0.4.0")
MAX_CONSECUTIVE_ERRORS = 10  # 连续错误阈值


class RequestAPI:
    def __init__(self, api_base: URL, api_token: str, weight: int, note: str = "", *, local_api: bool = False) -> None:
        if ".example.com" in str(api_base.host_subcomponent):
            raise ValueError(f"无效的 API URL: {api_base}, 请配置一个有效的 API")
        self._api_base = api_base
        self._api_token = api_token
        self._weight = weight
        self._note = note
        self._local_api = local_api
        self._error_count = 0  # 连续错误计数
        self._available = False  # API可用状态
        self._headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
        self._client = AsyncClient(base_url=str(api_base), headers=self._headers, timeout=60)

    @property
    def is_available(self) -> bool:
        """API是否可用"""
        return self._available

    @property
    def base_url(self) -> URL:
        """API基础URL"""
        return self._api_base

    async def mark_error(self, error: Exception | str | None = None) -> None:
        """标记API的错误"""
        if isinstance(error, Exception):
            logger.exception(error)
        logger.error(f"请求错误: [{error}], 错误计数: {self._error_count}/{MAX_CONSECUTIVE_ERRORS}")

        self._error_count += 1
        if self._error_count >= MAX_CONSECUTIVE_ERRORS:
            self._available = False
            logger.error(f"API可用性检查失败, 已被标记为不可用 : {self._api_base}")

    async def check_api_availability(self) -> None:
        """检查API可用性和版本兼容性

        Raises:
            APIError: API版本不兼容或API无法访问时抛出 (仅在初始化时)
        """

        try:
            # 检查API版本
            logger.debug(f"正在检查API可用性: {self._api_base}")
            if not self._local_api:
                async with httpx.AsyncClient() as client:
                    req = await client.get(
                        str(self._api_base.joinpath("version")),
                        headers=self._headers,
                        timeout=10.0,
                    )
                    req.raise_for_status()
                    version = req.json()

                if not (
                    (Version(version["version"]) >= MINIMUM_API_VERSION)  # API version check
                    and (version["package"] == "bilichat-request")  # API package check
                    and (Version(version["bilichat_min_version"]) <= Version(__version__))  # Bilichat version check
                ):
                    raise APIError(f"API 版本不兼容, {version}")

            # 所有检查通过, 标记API为可用
            logger.debug(f"API检查通过: {self._api_base}")
            self._error_count = 0
            self._available = True

        except Exception as e:
            self._available = False
            if isinstance(e, APIError):
                raise
            raise APIError(f"API可用性检查失败: {self._api_base}, {e}") from e

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """发送HTTP请求并处理结果

        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            httpx.Response: HTTP响应

        Raises:
            RequestError: 请求错误
        """
        logger.debug(f"Request {method} {url} {kwargs}")
        try:
            resp = await self._client.request(method, url, **kwargs)
            if not 200 <= resp.status_code < 300:
                await self.mark_error(f"Request {method} {url} failed: {resp.status_code} {resp.text}")
                raise RequestError(resp.status_code, resp.json()["detail"])
            try:
                logger.trace(f"Response {resp.status_code} {shorten_long_items(resp.json().copy())}")
            except AttributeError:
                logger.trace(f"Response {resp.status_code} {resp.text}")
            # 请求成功, 重置错误计数
            self._error_count = 0
        except Exception as e:
            await self.mark_error(e)
            raise
        return resp

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("GET", url, **kwargs)

    async def _post(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("POST", url, **kwargs)

    async def version(self):
        return VersionInfo.model_validate((await self._get("/version")).json())

    async def content_all(self, bililink: str | int):
        return Content.model_validate((await self._get("/content/", params={"bililink": bililink})).json())

    async def content_video(self, video_id: str | int, quality: int):
        return Content.model_validate(
            (await self._get("/content/video", params={"video_id": video_id, "quality": quality})).json()
        )

    async def content_dynamic(self, dynamic_id: str | int, quality: int):
        return Content.model_validate(
            (await self._get("/content/dynamic", params={"dynamic_id": dynamic_id, "quality": quality})).json()
        )

    async def content_column(self, cvid: str | int, quality: int):
        return Content.model_validate(
            (await self._get("/content/column", params={"cvid": cvid, "quality": quality})).json()
        )

    async def account_web_all(self) -> list[Account]:
        return [Account(**acc) for acc in (await self._get("/account/web_account")).json()]

    async def account_web_creat(self, cookies: list[dict] | dict, note: Note) -> Account:
        return Account.model_validate(
            (
                await self._post(
                    "/account/web_account/create",
                    json={"cookies": cookies, "note": note.model_dump()},
                )
            ).json()
        )

    async def account_web_delete(self, uid: int) -> Account:
        return Account.model_validate((await self._get("/account/web_account/delete", params={"uid": uid})).json())

    async def sub_live(self, uid: int) -> LiveRoom:
        return LiveRoom.model_validate((await self._get("/subs/live", params={"uid": uid})).json())

    async def sub_lives(self, uids: list[int]) -> list[LiveRoom]:
        return [LiveRoom.model_validate(live) for live in (await self._post("/subs/lives", json=uids)).json()]

    async def subs_dynamic(self, uid: int, offset: int = 0) -> list[Dynamic]:
        return [
            Dynamic.model_validate(dynamic)
            for dynamic in (await self._get("/subs/dynamic", params={"uid": uid, "offset": offset})).json()
        ]

    async def tools_b23_extract(self, b23: str) -> str:
        return (await self._get("/tools/b23_extract", params={"url": b23})).text

    async def tools_b23_generate(self, url: str) -> str:
        return (await self._get("/tools/b23_generate", params={"url": url})).text

    async def tools_search_up(self, keyword: str, ps: int = 5) -> list[SearchUp] | SearchUp:
        resq = (await self._get("/tools/search_up", params={"keyword": keyword, "ps": ps})).json()
        if isinstance(resq, list):
            return [SearchUp.model_validate(up) for up in resq]
        return SearchUp.model_validate(resq)
