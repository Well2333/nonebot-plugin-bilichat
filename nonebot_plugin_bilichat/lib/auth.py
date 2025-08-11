import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pyotp import TOTP

from nonebot_plugin_bilichat.config import ConfigCTX

BILICHAT_OTP = TOTP(ConfigCTX.get().webui.otp_secret_key, issuer="BiliChat", name="WebUI")
SECRET_KEY = ConfigCTX.get().webui.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180
security = HTTPBearer()


# JWT相关函数
def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    expire = time.time() + expires_delta if expires_delta else time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    return payload


# FastAPI 依赖函数
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """FastAPI 依赖: 获取当前用户"""
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

