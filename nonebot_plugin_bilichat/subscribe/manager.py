import asyncio
import json
import time
from typing import Any, Dict, List, Optional, TypedDict, Union

from nonebot import get_bots, get_driver
from nonebot.log import logger

from ..commands.adapters import PUSH_HANDLER
from ..config import plugin_config
from ..lib.store import data_dir
from ..lib.tools import calc_time_total

subscribe_file = data_dir.joinpath("subscribe.json")
subscribe_file.touch(0o755, True)

driver = get_driver()


class Uploader:
    """Represents an Uploader"""

    def __init__(self, nickname: str, uid: int):
        self.nickname: str = nickname
        self.uid: int = uid
        self.living: int = -1
        self.dyn_offset: int = 0

    @property
    def subscribed_users(self) -> List["User"]:
        """Get a list of user IDs subscribed to this uploader."""
        return [user for user in SubscriptionSystem.users.values() if self.uid in user.subscriptions]

    def dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the User."""
        return {"nickname": self.nickname, "uid": self.uid}

    def __str__(self) -> str:
        if self.living > 100000:
            live = f" 🔴直播中: {calc_time_total(time.time() - self.living)}"
        elif self.living > 0:
            live = " 🔴直播中"
        else:
            live = ""
        return f"{self.nickname}({self.uid}){live}"


class UserSubConfig(TypedDict):
    at_all: bool
    dynamic: bool
    live: bool


DEFUALT_SUB_CONFIG = {
    "at_all": False,
    "dynamic": True,
    "live": True,
}


class User:
    """Represents a user in the system."""

    def __init__(self, user_id: str, platfrom: str, at_all: bool = False, subscriptions: Dict[str, UserSubConfig] = {}):
        self.user_id: str = str(user_id)
        self.platfrom: str = platfrom
        self.at_all: bool = at_all
        self.subscriptions: Dict[int, UserSubConfig] = {int(k): v for k, v in subscriptions.items()}

    def dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the User."""
        return {
            "user_id": self.user_id,
            "platfrom": self.platfrom,
            "at_all": self.at_all,
            "subscriptions": self.subscriptions,
        }

    @property
    def subscribe_ups(self) -> List[Uploader]:
        uplist = []
        for uid in self.subscriptions.keys():
            if up := SubscriptionSystem.uploaders.get(uid):
                uplist.append(up)
            else:
                del self.subscriptions[uid]
        return uplist

    async def push_to_user(self, content: List[Union[str, bytes]], at_all: Optional[bool] = None):
        handler = PUSH_HANDLER.get(self.platfrom)
        if handler:
            await handler(self.user_id, content, at_all=self.at_all if at_all is None else at_all)
            await asyncio.sleep(plugin_config.bilichat_push_delay)

    def add_subscription(self, uploader: Uploader) -> Union[None, str]:
        """Add a subscription for a user to an uploader."""

        if len(self.subscriptions) > plugin_config.bilichat_subs_limit:
            return "本群的订阅已经满啦\n删除无用的订阅再试吧\n`(*>﹏<*)′"

        if uploader.uid in self.subscriptions:
            return "本群已经订阅了此UP主呢...\n`(*>﹏<*)′"

        self.subscriptions[uploader.uid] = DEFUALT_SUB_CONFIG.copy()  # type: ignore

        SubscriptionSystem.uploaders[uploader.uid] = uploader
        SubscriptionSystem.activate_uploaders[uploader.uid] = uploader
        SubscriptionSystem.users[self.user_id] = self

        SubscriptionSystem.get_activate_uploaders()
        SubscriptionSystem.save_to_file()

    def remove_subscription(self, uploader: Uploader) -> Union[None, str]:
        """Remove a subscription for a user from an uploader."""
        if uploader.uid not in self.subscriptions:
            return "本群并未订阅此UP主呢...\n`(*>﹏<*)′"

        del self.subscriptions[uploader.uid]
        SubscriptionSystem.users[self.user_id] = self
        if not self.subscriptions:
            del SubscriptionSystem.users[self.user_id]

        if not uploader.subscribed_users:
            del SubscriptionSystem.uploaders[uploader.uid]

        SubscriptionSystem.refresh_activate_uploaders()
        SubscriptionSystem.save_to_file()


class SubscriptionSystem:
    """Manages the subscription system."""

    uploaders: Dict[int, Uploader] = {}
    activate_uploaders: Dict[int, Uploader] = {}
    users: Dict[str, User] = {}

    @classmethod
    def dict(cls):
        return {
            "uploaders": {up.uid: up.dict() for up in cls.uploaders.values()},
            "users": {u.user_id: u.dict() for u in cls.users.values()},
        }

    @classmethod
    def load_from_file(cls):
        """Load data from the JSON file."""
        data = json.loads(subscribe_file.read_text() or '{"uploaders":{},"users":{}}')
        cls.uploaders = {int(k): Uploader(**v) for k, v in data["uploaders"].items()}
        cls.users = {k: User(**v) for k, v in data["users"].items()}

    @classmethod
    def save_to_file(cls):
        """Save data to the JSON file."""
        subscribe_file.write_text(
            json.dumps(
                cls.dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )

    @classmethod
    def get_activate_uploaders(cls):
        at_ups = "\n".join([str(up) for up in cls.activate_uploaders.values()])
        logger.debug("activate uploaders:\n" + (at_ups or "None activate uploaders"))
        return at_ups

    @classmethod
    def refresh_activate_uploaders(cls):
        """通过当前 Bot 覆盖的平台，激活需要推送的UP"""
        logger.debug("refreshing activate uploaders")
        cls.activate_uploaders = {}
        for bot in get_bots().values():
            platform = bot.adapter.get_name()
            for user in cls.users.values():
                if user.platfrom == platform:
                    for up in user.subscribe_ups:
                        cls.activate_uploaders[up.uid] = up
        cls.get_activate_uploaders()

    @classmethod
    async def async_refresh_activate_uploaders(cls):
        return cls.refresh_activate_uploaders()


SubscriptionSystem.load_from_file()

driver.on_bot_connect(SubscriptionSystem.async_refresh_activate_uploaders)
driver.on_bot_disconnect(SubscriptionSystem.async_refresh_activate_uploaders)
