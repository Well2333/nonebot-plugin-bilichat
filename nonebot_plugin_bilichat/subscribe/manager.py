import json
from datetime import datetime
from typing import Any, Dict, List, Union

from nonebot import get_bots, get_driver
from nonebot.log import logger

from ..adapters import PUSH_HANDLER
from ..config import plugin_config
from ..lib.store import data_dir

subscribe_file = data_dir.joinpath("subscribe.json")
subscribe_file.touch(0o755, True)

driver = get_driver()


class Uploader:
    """Represents an Uploader"""

    def __init__(self, nickname: str, uid: int):
        self.nickname: str = nickname
        self.uid: int = uid
        self.living: Union[datetime, None] = None
        self.dyn_offset: int = 0

    @property
    def subscribed_users(self) -> List["User"]:
        """Get a list of user IDs subscribed to this uploader."""
        return [user for user in SubscriptionSystem.users.values() if self.uid in user.subscriptions]

    def dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the User."""
        return {"nickname": self.nickname, "uid": self.uid}

    def __str__(self) -> str:
        return f"{self.nickname}({self.uid})"


class User:
    """Represents a user in the system."""

    def __init__(self, user_id: str, platfrom: str, at_all: bool = False, subscriptions: List[int] = []):
        self.user_id: str = user_id
        self.platfrom: str = platfrom
        self.at_all: bool = at_all
        self.subscriptions: List[int] = subscriptions

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
        for uid in self.subscriptions.copy():
            if up := SubscriptionSystem.uploaders.get(uid):
                uplist.append(up)
            else:
                self.subscriptions.remove(uid)
        return uplist

    async def push_dynamic(self, text: str, url: str, image: bytes):
        handler = PUSH_HANDLER.get(self.platfrom)
        if handler:
            await handler(user=self, text=text, url=url, image=image)

    def get_sub_prompt(self):
        if not self.subscriptions:
            return "本群并未订阅任何UP主呢...\n`(*>﹏<*)′"
        ups = self.subscribe_ups
        return f"本群共订阅 {len(ups)} 个 UP:\n" + "\n".join(
            [f"{index+1}. {up.nickname}({up.uid})" for index, up in enumerate(ups)]
        )

    def add_subscription(self, uploader: Uploader) -> Union[None, str]:
        """Add a subscription for a user to an uploader."""

        if len(self.subscriptions) > plugin_config.bilichat_subs_limit:
            return "本群的订阅已经满啦\n删除无用的订阅再试吧\n`(*>﹏<*)′"

        self.subscriptions.append(uploader.uid)

        SubscriptionSystem.uploaders[uploader.uid] = uploader
        SubscriptionSystem.activate_uploaders[uploader.uid] = uploader
        SubscriptionSystem.users[self.user_id] = self

        SubscriptionSystem.get_activate_uploaders()
        SubscriptionSystem.save_to_file()

    def remove_subscription(self, uploader: Uploader) -> Union[None, str]:
        """Remove a subscription for a user from an uploader."""
        SubscriptionSystem.users[self.user_id] = self

        if uploader.uid not in self.subscriptions:
            return "本群并未订阅此UP主呢...\n`(*>﹏<*)′"

        self.subscriptions.remove(uploader.uid)
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

    # @classmethod
    # def get_up_groups(cls) -> Set[Tuple[Uploader]]:
    #     elements = tuple(cls.activate_uploaders.values())
    #     st = set()
    #     if len(elements) < 4:
    #         return {
    #             elements,
    #         }
    #     t = len(elements)  # 总长度
    #     g = math.ceil(math.sqrt(t))  # 每组的长度
    #     i = 0
    #     for i in range(t // g):
    #         st.add(elements[g * i : g * (i + 1)])
    #     if t % g != 0:
    #         st.add(elements[g * (i + 1) :])
    #     return st

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
