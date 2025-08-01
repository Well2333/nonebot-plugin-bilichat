from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from nonebot_plugin_bilichat.lib.auth import create_access_token, get_current_user, verify_otp

router = APIRouter()


class OTPLoginRequest(BaseModel):
    """OTP登录请求"""
    code: str


class OTPLoginResponse(BaseModel):
    """OTP登录响应"""
    success: bool
    access_token: str | None = None
    token_type: str = "bearer"
    message: str


@router.post("/auth/login")
async def login_with_otp(request: OTPLoginRequest) -> OTPLoginResponse:
    """使用OTP验证码登录并获取JWT令牌"""
    try:
        # 验证OTP验证码
        if verify_otp(request.code):
            # 创建JWT令牌
            access_token = create_access_token(data={"sub": "nonebot_superuser"})
            
            return OTPLoginResponse(
                success=True,
                access_token=access_token,
                message="登录成功"
            )
        else:
            return OTPLoginResponse(
                success=False,
                message="验证码无效或已过期"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录过程中发生错误: {e!s}"
        ) from e


@router.get("/auth/me")
async def get_current_user_info(current_user: Annotated[dict, Depends(get_current_user)]):
    """获取当前用户信息"""
    return {
        "user_id": current_user.get("sub"),
        "authenticated": True
    } 