from typing import Dict, Union

from bilireq.auth import Auth
from bilireq.login import Login, ResponseCodeError
from bilireq.login.qrcode_login import get_qrcode_login_info, get_qrcode_login_result

from ..lib.bilibili_request.auth import AuthManager
from ..model.api import FaildResponse, Response
from ..model.api.bilibili_auth import AuthInfo, GenQrcodeResponse, ListAuthResponse, Qrcode, SingleAuthResponse
from .base import app


@app.get("/bili_grpc_auth")
async def list_auth() -> ListAuthResponse:
    return ListAuthResponse(
        data=[
            AuthInfo(id=auth.uid, token_expired=auth.tokens_expired, cookie_expired=auth.cookies_expired)
            for auth in AuthManager.grpc_auths
        ]
    )


@app.post("/bili_grpc_auth")
async def add_auth(raw_auth: Dict) -> Union[Response, FaildResponse]:
    try:
        auth = Auth(raw_auth)
        auth = await auth.refresh()
    except Exception as e:
        return FaildResponse(code=400, message=str(e))
    AuthManager.add_auth(auth)
    return SingleAuthResponse(
        data=AuthInfo(id=auth.uid, token_expired=auth.tokens_expired, cookie_expired=auth.cookies_expired),
    )


@app.delete("/bili_grpc_auth")
async def remove_auth(uid: int) -> Union[Response, FaildResponse]:
    if msg := AuthManager.remove_auth(uid):
        return FaildResponse(code=404, message=msg)
    return Response(data={})


@app.get("/bili_grpc_login/qrcode")
async def generate_qrcode() -> GenQrcodeResponse:
    r = await get_qrcode_login_info()
    return GenQrcodeResponse(data=Qrcode(qrcode_url=r["url"], auth_code=r["auth_code"]))


@app.post("/bili_grpc_login/qrcode")
async def login_by_qrcode(auth_code: str) -> Union[SingleAuthResponse, FaildResponse]:
    try:
        resp = await get_qrcode_login_result(auth_code)
        auth = Auth()
        auth.data = auth.refresh_handler(resp)
        auth = await auth.refresh()
        AuthManager.add_auth(auth)
        return SingleAuthResponse(
            data=AuthInfo(id=auth.uid, token_expired=auth.tokens_expired, cookie_expired=auth.cookies_expired),
        )
    except ResponseCodeError as e:
        return FaildResponse(code=e.code, message=e.msg)
    except Exception as e:
        return FaildResponse(code=400, message=str(e))
