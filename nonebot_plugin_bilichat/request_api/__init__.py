import random

import httpx
from httpx import AsyncClient
from nonebot.log import logger
from packaging.version import Version
from yarl import URL

from nonebot_plugin_bilichat.config import plugin_config
from nonebot_plugin_bilichat.model.exception import RequestError
from nonebot_plugin_bilichat.model.request_api import Account, Content, Dynamic, LiveRoom, Note, VersionInfo

MINIMUM_API_VERSION = Version("0.1.0")


class RequestAPI:
    def __init__(self, api_base: URL, api_token: str, weight: int) -> None:
        self._api_base = api_base
        self._api_token = api_token
        self._weight = weight
        self._client = AsyncClient(base_url=str(api_base), headers={"Authorization": f"Bearer {api_token}"}, timeout=60)

        # Check API version
        version = httpx.get(
            str(api_base.joinpath("version")),
            headers={"Authorization": f"Bearer {api_token}"},
        ).json()
        if not ((Version(version["version"]) >= MINIMUM_API_VERSION) and (version["package"] == "bilichat-request")):
            raise RuntimeError(f"API 版本不兼容, {version}")

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        req = await self._client.request(method, url, **kwargs)
        if not 199 < req.status_code < 300:
            logger.error(f"Request {method} {url} failed: {req.status_code} {req.json()}")
            raise RequestError(req.status_code, req.json()["detail"])
        return req

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

    async def account_web_creat(self, uid: int, cookies: list[dict], note: Note) -> Account:
        return Account.model_validate(
            (
                await self._post(
                    "/account/web_account/create", json={"uid": uid, "cookies": cookies, "note": note.model_dump()}
                )
            ).json()
        )

    async def account_web_delete(self, uid: int) -> Account:
        return Account.model_validate((await self._post("/account/web_account/delete", json={"uid": uid})).json())

    async def sub_live(self, uid: int) -> LiveRoom:
        return LiveRoom.model_validate((await self._get("/sub/live", params={"uid": uid})).json())

    async def sub_lives(self, uids: list[int]) -> list[LiveRoom]:
        return [LiveRoom.model_validate(live) for live in (await self._post("/sub/lives", json={"uids": uids})).json()]

    async def subs_dynamic(self, uid: int) -> list[Dynamic]:
        return [
            Dynamic.model_validate(dynamic) for dynamic in (await self._get("/sub/dynamic", params={"uid": uid})).json()
        ]

    async def tools_b23_extract(self, b23: str) -> str:
        return (await self._get("/tools/b23_extract", params={"url": b23})).text

    async def tools_b23_generate(self, url: str) -> str:
        return (await self._get("/tools/b23_generate", params={"url": url})).text


request_apis: list[RequestAPI] = []
for api in plugin_config.api.request_api:
    try:
        request_api = RequestAPI(URL(api.api), api.token, api.weight)
        request_apis.append(request_api)
    except Exception as e:  # noqa: PERF203
        logger.exception(f"API {api.api} 初始化失败, 跳过: {e}")


def get_request_api() -> RequestAPI:
    if not request_apis:
        raise RuntimeError("未找到可用的 Bilichat API 服务, 请添加至少一个 API 服务")
    return random.choice(request_apis)
