import json
import random
from typing import Any, Dict, List, Union

from bilireq.auth import Auth
from nonebot import get_driver
from nonebot.log import logger

from ..store import cache_dir

bili_grpc_auth_file = cache_dir.joinpath("bili_grpc_auth.json")
bili_grpc_auth_file.touch(0o700, exist_ok=True)


class AuthManager:
    grpc_auths: List[Auth] = []

    @classmethod
    async def load_grpc_auths(cls) -> None:
        data: Union[List[Dict], Dict] = json.loads(bili_grpc_auth_file.read_bytes() or "[]")
        data = data if isinstance(data, list) else [data]
        cls.grpc_auths.clear()
        for raw_auth in data:
            auth = Auth(raw_auth)
            try:
                auth = await auth.refresh()
                cls.grpc_auths.append(auth)
                logger.success(f"{auth.uid} 缓存登录成功")
            except Exception as e:
                logger.error(f"{auth.uid} 缓存登录失败，请使用验证码登录: {e}")
        cls.dump_grpc_auths()

    @classmethod
    def dump_grpc_auths(cls):
        bili_grpc_auth_file.write_text(
            json.dumps([auth.data for auth in cls.grpc_auths], indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @classmethod
    def get_cookies(cls) -> Dict[str, str]:
        if auths := cls.grpc_auths.copy():
            random.shuffle(auths)
            for auth in auths:
                if auth.cookies:
                    return auth.cookies.copy()
        logger.warning("没有可用的 bilibili cookies，请求可能风控")
        return {}

    @classmethod
    def get_auth(cls) -> Union[Auth, None]:
        return random.choice(cls.grpc_auths).copy() if cls.grpc_auths else None

    @classmethod
    def add_auth(cls, auth: Auth) -> None:
        for old_auth in cls.grpc_auths:
            if old_auth.uid == auth.uid:
                cls.grpc_auths.remove(old_auth)
                break
        cls.grpc_auths.append(auth)
        cls.dump_grpc_auths()

    @classmethod
    def remove_auth(cls, uid: int) -> Union[str, None]:
        for old_auth in cls.grpc_auths:
            if old_auth.uid == uid:
                cls.grpc_auths.remove(old_auth)
                cls.dump_grpc_auths()
                return
        logger.warning(f"没有找到 uid 为 {uid} 的账号")
        return f"没有找到 uid 为 {uid} 的账号"


get_driver().on_startup(AuthManager.load_grpc_auths)
