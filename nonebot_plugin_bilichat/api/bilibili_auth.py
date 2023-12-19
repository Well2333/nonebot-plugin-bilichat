from typing import Dict, Union

from bilireq.auth import Auth
from bilireq.login import Login

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
    login = Login()
    await login.get_qrcode_url()
    return GenQrcodeResponse(data=Qrcode(qrcode_url=login.qrcode_url, auth_code=login.auth_code))


@app.post("/bili_grpc_login/qrcode")
async def login_by_qrcode(auth_code: str) -> Union[SingleAuthResponse, FaildResponse]:
    login = Login()
    try:
        if auth := await login.qrcode_login(auth_code=auth_code, retry=3):
            await auth.refresh()
            AuthManager.add_auth(auth)
            return SingleAuthResponse(
                data=AuthInfo(id=auth.uid, token_expired=auth.tokens_expired, cookie_expired=auth.cookies_expired),
            )
    except Exception as e:
        return FaildResponse(code=400, message=str(e))
    return FaildResponse(code=400, message="登录失败，用户未扫码或二维码已过期")
