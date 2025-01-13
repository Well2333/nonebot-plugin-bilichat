import httpx
from httpx import AsyncClient
from nonebot.log import logger
from packaging.version import Version
from yarl import URL

from nonebot_plugin_bilichat.config import __version__
from nonebot_plugin_bilichat.lib.tools import shorten_long_items
from nonebot_plugin_bilichat.model.exception import RequestError
from nonebot_plugin_bilichat.model.request_api import Account, Content, Dynamic, LiveRoom, Note, SearchUp, VersionInfo

MINIMUM_API_VERSION = Version("0.2.4")


class RequestAPI:
    def __init__(
        self, api_base: URL, api_token: str, weight: int, note: str = "", *, skip_version_checking: bool = False
    ) -> None:
        if ".example.com" in str(api_base.host_subcomponent):
            raise ValueError(f"无效的 API URL: {api_base}, 请配置一个有效的 API")
        self._api_base = api_base
        self._api_token = api_token
        self._weight = weight
        self._note = note
        headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
        self._client = AsyncClient(base_url=str(api_base), headers=headers, timeout=60)

        if not skip_version_checking:
            # Check API version
            version = httpx.get(
                str(api_base.joinpath("version")),
                headers=headers,
            ).json()
            if not (
                (Version(version["version"]) >= MINIMUM_API_VERSION)  # API version check
                and (version["package"] == "bilichat-request")  # API package check
                and (Version(version["bilichat_min_version"]) <= Version(__version__))  # Bilichat version check
            ):
                raise RuntimeError(f"API 版本不兼容, {version}")

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        logger.debug(f"Request {method} {url} {kwargs}")
        resp = await self._client.request(method, url, **kwargs)
        if not 199 < resp.status_code < 300:
            logger.error(f"Request {method} {url} failed: {resp.status_code} {resp.json()}")
            raise RequestError(resp.status_code, resp.json()["detail"])
        try:
            logger.trace(f"Response {resp.status_code} {shorten_long_items(resp.json().copy())}")
        except AttributeError:
            logger.trace(f"Response {resp.status_code} {resp.text}")
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
        return [Account(cookies={}, **acc) for acc in (await self._get("/account/web_account")).json()]

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
