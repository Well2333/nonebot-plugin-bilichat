import random
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from nonebot.log import logger

from nonebot_plugin_bilichat.config import ConfigCTX

# ==================== 测试用固定OTP配置 ====================
# 警告：仅用于测试！生产环境请保持 FIXED_OTP_CODE = None
# 要启用固定OTP，将 FIXED_OTP_CODE 设置为6位数字字符串，如 "123456"
FIXED_OTP_CODE = "123456"  # 设置为 "123456" 等固定验证码启用测试模式
logger.warning("⚠️  请不要在生产环境中使用固定OTP验证码!")
logger.warning(f"⚠️  测试模式: 使用固定OTP验证码: {FIXED_OTP_CODE}")
logger.warning("⚠️  请不要在生产环境中使用固定OTP验证码!")
# ===========================================================

# JWT配置
SECRET_KEY = ConfigCTX.get().webui.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 安全认证
security = HTTPBearer()


class AuthManager:
    """认证管理器 - 全局单例"""

    _instance = None
    _otp_code: str | None = None
    _expire_time: float = 0

    def __new__(cls) -> "AuthManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def generate_otp(self) -> str:
        """生成6位数字OTP验证码"""
        if FIXED_OTP_CODE is not None:
            # 测试模式：使用固定OTP
            self._otp_code = FIXED_OTP_CODE
            self._expire_time = 4102415999  # 2099年12月31日
            logger.warning(f"⚠️  测试模式：使用固定OTP验证码: {FIXED_OTP_CODE}")
            return FIXED_OTP_CODE
        else:
            # 正常模式：生成随机6位数字验证码
            otp_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
            self._otp_code = otp_code
            self._expire_time = time.time() + 300  # 5分钟 = 300秒
            logger.info(f"生成了新的OTP验证码: {otp_code}")
            return otp_code

    def verify_otp(self, code: str) -> bool:
        """验证OTP验证码"""
        if not self._otp_code:
            return False

        current_time = time.time()

        # 检查是否过期
        if self._expire_time < current_time:
            self._clear_otp()
            return False

        # 检查验证码是否匹配
        if self._otp_code == code:
            # 验证成功后清除验证码
            self._clear_otp()
            return True

        return False

    def _clear_otp(self) -> None:
        """清除OTP验证码"""
        self._otp_code = None
        self._expire_time = 0


# 全局认证管理器实例
auth_manager = AuthManager()
if FIXED_OTP_CODE is not None:
    auth_manager.generate_otp()


# 便捷函数
def generate_otp() -> str:
    """生成OTP验证码"""
    return auth_manager.generate_otp()


def verify_otp(code: str) -> bool:
    """验证OTP验证码"""
    return auth_manager.verify_otp(code)


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
