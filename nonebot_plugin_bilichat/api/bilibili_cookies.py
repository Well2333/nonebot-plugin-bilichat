from typing import Dict

from bilireq.auth import Auth
from bilireq.login import Login
from fastapi import HTTPException
from fastapi.responses import JSONResponse, Response

from ..lib.bilibili_request.auth import AuthManager
from .base import app


@app.get("/bili_grpc_auth")
async def list_auth():
    return JSONResponse(
        content=[
            {"id": auth.uid, "token_expired": auth.tokens_expired, "cookie_expired": auth.cookies_expired}
            for auth in AuthManager.grpc_auths
        ]
    )


@app.post("/bili_grpc_auth")
async def add_auth(raw_auth: Dict):
    try:
        auth = Auth(raw_auth)
        auth = await auth.refresh()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    AuthManager.add_auth(auth)
    return JSONResponse(
        status_code=201,
        content={"id": auth.uid, "token_expired": auth.tokens_expired, "cookie_expired": auth.cookies_expired},
    )


@app.delete("/bili_grpc_auth")
async def remove_auth(uid: int):
    if msg := AuthManager.remove_auth(uid):
        raise HTTPException(status_code=404, detail=msg)
    return Response(status_code=204)


@app.get("/bili_grpc_login/qrcode")
async def generate_qrcode():
    login = Login()
    await login.get_qrcode_url()
    return JSONResponse(content={"qrcode_url": login.qrcode_url, "auth_code": login.auth_code})


@app.post("/bili_grpc_login/qrcode")
async def login_by_qrcode(auth_code: str):
    login = Login()
    if auth := await login.qrcode_login(auth_code=auth_code, retry=3):
        await auth.refresh()
        AuthManager.add_auth(auth)
        return JSONResponse(
            status_code=201,
            content={"id": auth.uid, "token_expired": auth.tokens_expired, "cookie_expired": auth.cookies_expired},
        )
    raise HTTPException(status_code=400, detail="登录失败，用户未扫码或二维码已过期")
