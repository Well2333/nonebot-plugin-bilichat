import json
from abc import ABC
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Dict,
    Literal,
    Optional,
)

from nonebot.compat import PYDANTIC_V2, ConfigDict, type_validate_python
from nonebot.plugin import on_notice
from pydantic import BaseModel
from typing_extensions import Self

target_changed = on_notice(block=False)


class SupportedPlatform(str, Enum):
    qq_group = "QQ Group"
    qq_private = "QQ Private"
    qq_group_openid = "QQ Group OpenID"
    qq_private_openid = "QQ Private OpenID"
    qq_guild_channel = "QQ Guild Channel"
    qq_guild_direct = "QQ Guild Direct"
    kaiheila_channel = "Kaiheila Channel"
    kaiheila_private = "Kaiheila Private"
    unknown_ob12 = "Unknow Onebot 12 Platform"
    unknown_satori = "Unknown Satori Platform"
    dodo_channel = "DoDo Channel"
    dodo_private = "DoDo Private"


class Level(Enum):
    MetaBase = 1
    Base = 2
    Normal = 3


class SerializationMeta(BaseModel, ABC):
    _index_key: ClassVar[str]
    _deserializer_dict: ClassVar[Dict]
    _level: ClassVar[Level] = Level.MetaBase

    if PYDANTIC_V2:
        model_config = ConfigDict(
            frozen=True,
            from_attributes=True,
        ) # type: ignore

        @classmethod
        def __pydantic_init_subclass__(cls, *args, **kwargs) -> None:
            cls._register_subclass(cls.model_fields)

    else:

        class Config:
            frozen = True
            orm_mode = True

        @classmethod
        def __init_subclass__(cls, *args, **kwargs) -> None:
            cls._register_subclass(cls.__fields__)

            super().__init_subclass__(*args, **kwargs)

    @classmethod
    def _register_subclass(cls, fields) -> None:
        if cls._level == Level.MetaBase:
            cls._level = Level.Base
            cls._deserializer_dict = {}
        elif cls._level == Level.Base:
            cls._level = Level.Normal
            cls._deserializer_dict[fields[cls._index_key].default] = cls
        elif cls._level == Level.Normal:
            pass
        else:
            raise RuntimeError("SerializationMeta init error")

    @classmethod
    def deserialize(cls, source: Any) -> Self:
        if isinstance(source, str):
            raw_obj = json.loads(source)
        else:
            raw_obj = source

        key = raw_obj.get(cls._index_key)
        assert key
        return type_validate_python(cls._deserializer_dict[key], raw_obj)


class PlatformTarget(SerializationMeta):
    _index_key = "platform_type"

    platform_type: SupportedPlatform

    if PYDANTIC_V2:
        model_config = ConfigDict(
            frozen=True,
            from_attributes=True,
        ) # type: ignore
    else:

        class Config:
            frozen = True
            orm_mode = True


class TargetQQGroup(PlatformTarget):
    """QQ群

    参数
        group_id: 群号
    """

    platform_type: Literal[SupportedPlatform.qq_group] = SupportedPlatform.qq_group
    group_id: int


class TargetQQPrivate(PlatformTarget):
    """QQ私聊

    参数
        user_id: QQ号
    """

    platform_type: Literal[SupportedPlatform.qq_private] = SupportedPlatform.qq_private
    user_id: int


class TargetQQGuildChannel(PlatformTarget):
    """QQ频道子频道

    参数
        channel_id: 子频道号
    """

    platform_type: Literal[SupportedPlatform.qq_guild_channel] = SupportedPlatform.qq_guild_channel
    channel_id: int


class TargetQQGuildDirect(PlatformTarget):
    """QQ频道私聊

    参数
        recipient_id: 接收人ID
        source_guild_id: 来自的频道号
    """

    platform_type: Literal[SupportedPlatform.qq_guild_direct] = SupportedPlatform.qq_guild_direct
    recipient_id: int
    source_guild_id: int


class TargetOB12Unknow(PlatformTarget):
    """暂未识别的 Onebot v12 发送目标

    参数
        detail_type: "private" or "group" or "channel"
        user_id, group_id, channel_id, guild_id: 同 ob12 定义
    """

    platform_type: Literal[SupportedPlatform.unknown_ob12] = SupportedPlatform.unknown_ob12
    platform: str
    detail_type: Literal["private", "group", "channel"]
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None


class TargetSatoriUnknown(PlatformTarget):
    """暂未识别的 Satori 发送目标

    参数
        platform: 平台名
        user_id: 用户 ID
        guild_id: 群组 ID
        channel_id: 频道 ID
    """

    platform_type: Literal[SupportedPlatform.unknown_satori] = SupportedPlatform.unknown_satori
    platform: str
    user_id: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None


class TargetKaiheilaChannel(PlatformTarget):
    """开黑啦频道

    参数
        channel_id: 频道ID
    """

    platform_type: Literal[SupportedPlatform.kaiheila_channel] = SupportedPlatform.kaiheila_channel
    channel_id: str


class TargetKaiheilaPrivate(PlatformTarget):
    """开黑啦私聊

    参数
        user_id: 接收人ID
    """

    platform_type: Literal[SupportedPlatform.kaiheila_private] = SupportedPlatform.kaiheila_private
    user_id: str


class TargetDoDoChannel(PlatformTarget):
    """DoDo Channel

    参数
        channel_id: 频道ID
        dodo_source_id: 用户 ID(可选)
    """

    platform_type: Literal[SupportedPlatform.dodo_channel] = SupportedPlatform.dodo_channel
    channel_id: str
    dodo_source_id: Optional[str] = None


class TargetDoDoPrivate(PlatformTarget):
    """DoDo Private

    参数
        dodo_source_id: 用户 ID
        island_source_id: 群 ID
    """

    platform_type: Literal[SupportedPlatform.dodo_private] = SupportedPlatform.dodo_private
    island_source_id: str
    dodo_source_id: str
