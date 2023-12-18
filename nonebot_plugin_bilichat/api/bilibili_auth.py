from typing import Dict

from bilireq.auth import Auth
from bilireq.login import Login

from ..lib.bilibili_request.auth import AuthManager
from ..model.api import Response
from .base import app


@app.get("/bili_grpc_auth")
async def list_auth() -> Response:
    return Response(
        data=[
            {"id": auth.uid, "token_expired": auth.tokens_expired, "cookie_expired": auth.cookies_expired}
            for auth in AuthManager.grpc_auths
        ]
    )


@app.post("/bili_grpc_auth")
async def add_auth(raw_auth: Dict) -> Response:
    try:
        auth = Auth(raw_auth)
        auth = await auth.refresh()
    except Exception as e:
        return Response(code=400, message=str(e))
    AuthManager.add_auth(auth)
    return Response(
        code=201,
        data={"id": auth.uid, "token_expired": auth.tokens_expired, "cookie_expired": auth.cookies_expired},
    )


@app.delete("/bili_grpc_auth")
async def remove_auth(uid: int) -> Response:
    if msg := AuthManager.remove_auth(uid):
        return Response(code=404, message=msg)
    return Response(code=204, data={})


@app.get("/bili_grpc_login/qrcode")
async def generate_qrcode() -> Response:
    login = Login()
    await login.get_qrcode_url()
    return Response(data={"qrcode_url": login.qrcode_url, "auth_code": login.auth_code})


@app.post("/bili_grpc_login/qrcode")
async def login_by_qrcode(auth_code: str):
    login = Login()
    try:
        if auth := await login.qrcode_login(auth_code=auth_code, retry=3):
            await auth.refresh()
            AuthManager.add_auth(auth)
            return Response(
                code=201,
                data={"id": auth.uid, "token_expired": auth.tokens_expired, "cookie_expired": auth.cookies_expired},
            )
    except Exception as e:
        return Response(code=400, message=str(e))
    return Response(code=400, message="登录失败，用户未扫码或二维码已过期")
