import asyncio
import json
import random
import time
from datetime import datetime
from typing import Any

from apscheduler.job import Job
from nonebot import get_driver
from nonebot.adapters import Bot
from nonebot.compat import PYDANTIC_V2
from nonebot.log import logger
from nonebot_plugin_alconna.uniseg import AtAll, Image, Target, UniMessage
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_auto_bot_selector import get_bots, refresh_bots
from nonebot_plugin_auto_bot_selector.expection import NoBotFoundError
from nonebot_plugin_auto_bot_selector.registries import BOT_CACHE
from nonebot_plugin_auto_bot_selector.target import (
    PlatformTarget,
    SupportedPlatform,
    TargetKaiheilaChannel,
    TargetQQGroup,
    TargetQQGuildChannel,
    TargetQQPrivate,
)
from nonebot_plugin_auto_bot_selector.utils.alconna import create_target, extract_target
from pydantic import BaseModel, Field, validator

from ..lib.store import cache_dir, data_dir
from ..lib.tools import calc_time_total
from ..lib.uid_extract import uid_extract_sync
from ..optional import capture_exception

CONFIG_LOCK = asyncio.Lock()

SUBSCRIBE_FILE = data_dir.joinpath("subscribe.json")
SUBSCRIBE_FILE.touch(0o755, True)
SUBSCRIBE_FILE_ARCHIVE_DIR = cache_dir.joinpath("subscribe_archive")
SUBSCRIBE_FILE_ARCHIVE_DIR.mkdir(0o755, True, True)

driver = get_driver()


class Uploader(BaseModel):
    """Represents an Uploader"""

    nickname: str
    uid: int
    living: int = -1
    dyn_offset: int = 0

    def __init__(self, **values):
        super().__init__(**values)
        # 没有昵称的则搜索昵称
        if not self.nickname:
            up = uid_extract_sync(f"UID: {self.uid}")
            if isinstance(up, str):
                raise ValueError(f"未找到 uid 为 {self.uid} 的 UP")
            self.nickname = up.nickname
    
    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if isinstance(other, Uploader):
            return self.uid == other.uid
        return False

    @property
    def subscribed_users(self) -> list["User"]:
        """Get a list of user IDs subscribed to this uploader."""
        return [user for user in SubscriptionSystem.users.values() if self.uid in user.subscriptions]

    def dict(self, **kwargs) -> dict[str, Any]:
        exclude_properties = {name for name, value in type(self).__dict__.items() if isinstance(value, property)}
        exclude_properties.add("living")
        exclude_properties.add("dyn_offset")
        if PYDANTIC_V2:
            dict_ = super().model_dump(**{**kwargs, "exclude": exclude_properties})  # type: ignore
        else:
            dict_ = super().dict(**{**kwargs, "exclude": exclude_properties})  # type: ignore
        return dict_

    def __str__(self) -> str:
        if self.living > 100000:
            live = f" 🔴直播中: {calc_time_total(time.time() - self.living)}"
        elif self.living > 0:
            live = " 🔴直播中"
        else:
            live = ""
        return f"{self.nickname}({self.uid}){live}"


class UserSubConfig(BaseModel):
    uid: int
    dynamic: bool = True
    dynamic_at_all: bool = False
    live: bool = True
    live_at_all: bool = False

    def is_defualt_val(self) -> bool:
        """
        Checks if all the attributes of the object have their default values.

        Returns:
            bool: True if all attributes have their default values, False otherwise.
        """
        if PYDANTIC_V2:
            return not any(
                (
                    self.__getattribute__(field_name) != self.model_fields[field_name].default  # type: ignore
                    if field_name != "uid"
                    else False
                )
                for field_name in self.model_fields  # type: ignore
            )
        else:
            return not any(
                (
                    self.__getattribute__(field_name) != self.__fields__[field_name].default  # type: ignore
                    if field_name != "uid"
                    else False
                )
                for field_name in self.__fields__  # type: ignore
            )


class User(BaseModel):
    """Represents a user in the system."""

    user_id: str
    platform: str
    at_all: bool = False
    subscriptions: dict[int, UserSubConfig] = {}

    @validator("subscriptions", pre=True, always=True)
    def validate_subscriptions(cls, v: dict[str, dict[str, Any]] | list[dict[str, Any]]):
        if not v:
            return {}

        if isinstance(v, list):
            # 列表形式的输入：直接解包每个字典创建 UserSubConfig 实例
            return {sub.get("uid"): UserSubConfig(**sub) for sub in v if sub.get("uid") is not None}

        # 字典形式的输入
        validated_subs = {}
        for uid, sub in v.items():
            try:
                # 如果sub中存在uid，直接传递整个字典
                if "uid" in sub:
                    validated_subs[sub["uid"]] = UserSubConfig(**sub)
                # 否则，显式地设置uid
                else:
                    validated_subs[int(uid)] = UserSubConfig(uid=int(uid), **sub)
            except (ValueError, TypeError):
                # 处理 uid 转换为 int 时可能发生的错误
                continue

        return validated_subs
    
    def __hash__(self):
        return hash((self.platform, self.user_id))

    def __eq__(self, other):
        if isinstance(other, User):
            return self.platform == other.platform and self.user_id == other.user_id
        return False

    @classmethod
    def extract_alc_target(cls, target: Target) -> tuple[str, str]:
        t = extract_target(target)
        return t.platform_type.value, target.id

    def create_saa_target(self) -> PlatformTarget:
        if self.platform == SupportedPlatform.qq_group:
            return TargetQQGroup(group_id=int(self.user_id))
        elif self.platform == SupportedPlatform.qq_private:
            return TargetQQPrivate(user_id=int(self.user_id))
        elif self.platform == SupportedPlatform.qq_guild_channel:
            return TargetQQGuildChannel(channel_id=int(self.user_id))
        elif self.platform == SupportedPlatform.kaiheila_channel:
            return TargetKaiheilaChannel(channel_id=self.user_id)
        # Other
        else:
            raise NotImplementedError("Unsupported platform type")

    def create_alc_target(self) -> Target:
        return create_target(self.create_saa_target())

    def dict(self, **kwargs) -> dict[str, Any]:
        exclude_properties = {name for name, value in type(self).__dict__.items() if isinstance(value, property)}
        exclude_properties.add("subscriptions")
        if PYDANTIC_V2:
            dict_ = super().model_dump(**{**kwargs, "exclude": exclude_properties})  # type: ignore
        else:
            dict_ = super().dict(**{**kwargs, "exclude": exclude_properties})  # type: ignore
        dict_["subscriptions"] = [sub.dict() for sub in self.subscriptions.values()]
        return dict_

    @property
    def subscribe_ups(self) -> list[Uploader]:
        uplist = []
        for uid in self.subscriptions.keys():
            if up := SubscriptionSystem.uploaders.get(int(uid)):
                uplist.append(up)
            else:
                del self.subscriptions[uid]
        return uplist

    @property
    def _id(self) -> str:
        return f"{self.platform}-_-{self.user_id}"

    async def push_to_user(self, content: list[str | bytes], at_all: bool | None = None):
        if not at_all:
            at = ""
        elif self.platform == SupportedPlatform.qq_group:
            at = AtAll()
        elif self.platform == SupportedPlatform.qq_guild_channel:
            at = "@everyone"
        else:
            at = ""
        msg = UniMessage(at)
        msg.extend([Image(raw=x) if isinstance(x, bytes) else x for x in content])  # type: ignore

        try:
            bots = get_bots(target=self.create_saa_target())
        except NoBotFoundError:
            logger.warning(f"用户 {self.user_id} 无可用的推送Bot")
            return
        random.shuffle(bots)
        logger.info(f"向 {self.user_id} 推送消息，可用的bots： {bots}")
        for bot in bots:
            logger.debug(f"开始推送 -> {bot}")
            try:
                await msg.send(bot=bot, target=self.create_alc_target())
                logger.debug(f"推送成功 -> {bot}")
                return
            except Exception as e:
                capture_exception(e)
                logger.exception(f"推送失败 -> {bot}")
        logger.error(f"无法为用户 {self.user_id} 推送消息")

        await asyncio.sleep(SubscriptionSystem.config.push_delay)

    def add_subscription(self, uploader: Uploader) -> str | None:
        """Add a subscription for a user to an uploader."""

        if len(self.subscriptions) > SubscriptionSystem.config.subs_limit:
            return "本群的订阅已经满啦\n删除无用的订阅再试吧\n`(*>﹏<*)′"

        if uploader.uid in self.subscriptions:
            return "本群已经订阅了此UP主呢...\n`(*>﹏<*)′"

        self.subscriptions[uploader.uid] = UserSubConfig(uid=uploader.uid)  # type: ignore

        SubscriptionSystem.uploaders[uploader.uid] = uploader
        SubscriptionSystem.activate_uploaders[uploader.uid] = uploader
        SubscriptionSystem.users[self._id] = self

        SubscriptionSystem.get_activate_uploaders()
        SubscriptionSystem.save_to_file()

    async def remove_subscription(self, uploader: Uploader) -> str | None:
        """Remove a subscription for a user from an uploader."""
        if uploader.uid not in self.subscriptions:
            return "本群并未订阅此UP主呢...\n`(*>﹏<*)′"

        del self.subscriptions[uploader.uid]
        SubscriptionSystem.users[self._id] = self
        if not self.subscriptions:
            del SubscriptionSystem.users[self._id]

        if not uploader.subscribed_users:
            del SubscriptionSystem.uploaders[uploader.uid]

        await SubscriptionSystem.refresh_activate_uploaders()
        SubscriptionSystem.save_to_file()


class SubscriptionConfig(BaseModel):
    subs_limit: int = Field(5, ge=0, le=50)
    dynamic_interval: int = Field(90, ge=10)
    live_interval: int = Field(30, ge=10)
    push_delay: int = Field(3, ge=0)
    dynamic_grpc: bool = False


class SubscriptionCfgFile(BaseModel):
    config: SubscriptionConfig = SubscriptionConfig(**{})
    uploaders: list[Uploader] = []
    users: list[User] = []

    @validator("uploaders", always=True, pre=True)
    def validate_uploaders(cls, v: dict[str, dict[str, Any]] | list[dict[str, Any]]):
        if not v:
            return []
        ups = v.values() if isinstance(v, dict) else v
        return [Uploader(**up) for up in ups]

    @validator("users", always=True, pre=True)
    def validate_users(cls, v: dict[str, dict[str, Any]] | list[dict[str, Any]]):
        if not v:
            return []
        users = v.values() if isinstance(v, dict) else v
        users_obj = []
        for user in users:
            # 兼容旧版本配置文件
            if "platfrom" in user:
                user["platform"] = user.pop("platfrom")
            if user["platform"] in ["OneBot V11", "mirai2"]:
                user["platform"] = SupportedPlatform.qq_group.value
            # 移除无订阅的用户
            if len(user["subscriptions"]) == 0:
                continue
            users_obj.append(User(**user))
        return users_obj


class SubscriptionSystem:
    """Manages the subscription system."""

    uploaders: dict[int, Uploader] = {}
    activate_uploaders: dict[int, Uploader] = {}
    users: dict[str, User] = {}
    config: SubscriptionConfig = SubscriptionConfig(**{})

    @classmethod
    def dump_dict(cls):
        return {
            "config": cls.config.dict(),
            "uploaders": [up.dict() for up in cls.uploaders.values()],
            "users": [user.dict() for user in cls.users.values()],
        }

    @classmethod
    async def load(cls, data: dict[str, dict[str, Any] | list[dict[str, Any]]]):
        raw_cfg = SubscriptionCfgFile.parse_obj(data)
        while CONFIG_LOCK.locked():
            await asyncio.sleep(0)
        async with CONFIG_LOCK:
            cls.config = raw_cfg.config
            cls.uploaders.update({up.uid: up for up in raw_cfg.uploaders})
            cls.users = {f"{u.platform}-_-{u.user_id}": u for u in raw_cfg.users}

            # 清理无订阅的UP
            for uploader in cls.uploaders.copy().values():
                if not uploader.subscribed_users:
                    del SubscriptionSystem.uploaders[uploader.uid]

            # 添加缺失的UP
            for user in cls.users.values():
                for sub in user.subscriptions.keys():
                    if sub not in cls.uploaders:
                        cls.uploaders[sub] = Uploader(nickname="", uid=sub)

            # 更新定时任务
            dyn_job: Job = scheduler.get_job("dynamic_update")  # type: ignore
            dyn_job.reschedule(
                "interval",
                seconds=cls.config.dynamic_interval,
                jitter=cls.config.dynamic_interval // 3,
            )
            live_job: Job = scheduler.get_job("live_update")  # type: ignore
            live_job.reschedule(
                "interval",
                seconds=cls.config.live_interval,
                jitter=cls.config.live_interval // 3,
            )

            cls.save_to_file()
            await cls.refresh_activate_uploaders()

    @classmethod
    async def load_from_file(cls):
        """Load data from the JSON file."""
        try:
            text = SUBSCRIBE_FILE.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("subscribe.json 非 UTF-8 编码, 尝试使用系统默认编码")
            text = SUBSCRIBE_FILE.read_text()
        await cls.load(json.loads(text or "{}"))

    @classmethod
    def save_to_file(cls):
        """Save data to the JSON file."""
        try:
            old = SUBSCRIBE_FILE.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("subscribe.json 非 UTF-8 编码, 尝试使用系统默认编码")
            old = SUBSCRIBE_FILE.read_text()
        data = json.dumps(
            cls.dump_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        if old == data:
            logger.info("配置文件未更改，无需保存")
            return
        SUBSCRIBE_FILE.write_text(
            data=data,
            encoding="utf-8",
        )
        backup_file = SUBSCRIBE_FILE_ARCHIVE_DIR.joinpath(f"{datetime.now().strftime('%Y-%m-%dT%H_%M_%S')}.json")
        backup_file.touch(0o755, True)
        backup_file.write_text(data=data, encoding="utf-8")
        logger.info(f"配置文件已更改，备份修改后的配置文件到 {backup_file}")

    @classmethod
    def get_activate_uploaders(cls):
        at_ups = "\n".join([str(up) for up in cls.activate_uploaders.values()])
        logger.debug("已激活的UP:\n" + (at_ups or "无已激活的UP"))
        return at_ups

    @classmethod
    async def refresh_activate_uploaders(cls, refresh: bool = False):
        """通过当前 Bot 覆盖的平台，激活需要推送的UP"""
        if refresh:
            logger.info("正在刷新目标缓存")
            await refresh_bots()
        logger.info("正在刷新激活的UP列表")
        cls.activate_uploaders = {}
        for user in cls.users.values():
            logger.debug(f"正在尝试激活用户 {user._id} 订阅的 UP")
            target = user.create_saa_target()
            try:
                get_bots(target)
                cls.activate_uploaders.update({int(up): cls.uploaders[int(up)] for up in user.subscriptions.keys()})
            except NoBotFoundError:
                logger.debug(f"用户 {user._id} 无可用推送 Bot")
                continue
        cls.get_activate_uploaders()


driver.on_startup(SubscriptionSystem.load_from_file)


@driver.on_bot_connect
async def _(bot: Bot):
    logger.info("重新检查可推送的用户")
    while True:
        if bot in BOT_CACHE.keys():
            await SubscriptionSystem.refresh_activate_uploaders()
            logger.info("检查可推送的用户完成")
            return
        await asyncio.sleep(0.5)


@driver.on_bot_disconnect
async def _(bot: Bot):
    logger.info("重新检查可推送的用户")
    while True:
        if bot not in BOT_CACHE.keys():
            await SubscriptionSystem.refresh_activate_uploaders()
            logger.info("检查可推送的用户完成")
            return
        await asyncio.sleep(0.5)
