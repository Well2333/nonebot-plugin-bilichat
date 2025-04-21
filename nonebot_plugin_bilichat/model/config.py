from importlib.metadata import version

from pydantic import BaseModel, Field, computed_field, field_validator

from .subscribe import UserInfo


class WebUIConfig(BaseModel):
    """WebUI 相关配置"""

    enable: bool = Field(
        default=True,
        title="启用 WebUI",
        description="是否启用 WebUI",
        json_schema_extra={"ui:options": {"disabled": True, "placeholder": "请输入"}},
    )
    api_path: str = Field(
        default="bilichatwebui",
        title="WebUI 挂载路径",
        description="WebUI 挂载路径",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    api_access_token: str = Field(
        default="", title="WebUI Token", description="WebUI Token", json_schema_extra={"ui:options": {"disabled": True}}
    )


class NoneBotConfig(BaseModel):
    """nonebot 相关配置"""

    block: bool = Field(
        default=False,
        title="拦截事件",
        description="是否拦截事件(防止其他插件二次解析)",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    fallback: bool = Field(
        default=True,
        title="启用发送失败回退",
        description="是否启用 Alconna 的发送失败回退机制",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    enable_self: bool = Field(
        default=False,
        title="响应自身的消息",
        description="是否允许响应自身的消息",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    only_self: bool = Field(
        default=False,
        title="仅响应自身的消息",
        description="是否仅响应自身的消息, 开启后会覆盖全部其他规则(人机合一特供)",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    only_to_me: bool = Field(
        default=False,
        title="仅@机器人",
        description="非自身消息是否需要 @机器人 或使用机器人的昵称才响应",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    command_to_me: bool = Field(
        default=True,
        title="命令需要@机器人",
        description="命令是否需要@机器人或使用机器人的昵称才响应",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    cmd_start: str = Field(
        default="bilichat",
        title="命令的起始词",
        description="命令的起始词, 可设置为空",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    cmd_add_sub: list[str] = Field(
        default=["订阅", "关注"],
        title="订阅命令别名",
        description="`sub`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_remove_sub: list[str] = Field(
        default=["退订", "取关"],
        title="退订命令别名",
        description="`unsub`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_check_sub: list[str] = Field(
        default=["查看", "查看订阅"],
        title="查看订阅命令别名",
        description="`check`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_reset_sub: list[str] = Field(
        default=["重置", "重置配置"],
        title="重置配置命令别名",
        description="`reset`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_at_all: list[str] = Field(
        default=["全体成员", "at全体"],
        title="全体命令别名",
        description="`atall`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_dynamic: list[str] = Field(
        default=["动态通知", "动态订阅"],
        title="动态命令别名",
        description="`dynamic`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_live: list[str] = Field(
        default=["直播通知", "直播订阅"],
        title="直播命令别名",
        description="`live`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_checkdynamic: list[str] = Field(
        default=["查看动态"],
        title="查看动态命令别名",
        description="`checkdynamic`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_fetch: list[str] = Field(
        default=["获取内容", "解析内容"],
        title="获取内容命令别名",
        description="`fetch`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_check_login: list[str] = Field(
        default=["查看登录账号"],
        title="查看登录账号命令别名",
        description="`check_login`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_login_qrcode: list[str] = Field(
        default=["扫码登录"],
        title="扫码登录命令别名",
        description="`qrlogin`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_logout: list[str] = Field(
        default=["登出账号"],
        title="登出账号命令别名",
        description="`logout`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )
    cmd_modify_cfg: list[str] = Field(
        default=["修改配置"],
        title="修改配置命令别名",
        description="`cfg`命令的别名",
        json_schema_extra={"ui:options": {"disabled": True}, "ui:hidden": True},
    )


class AnalyzeConfig(BaseModel):
    """解析相关配置"""

    video: bool = Field(default=True, title="解析视频", description="是否解析视频")
    dynamic: bool = Field(default=True, title="解析动态", description="是否解析动态")
    column: bool = Field(default=True, title="解析专栏", description="是否解析专栏")
    cd_time: int = Field(default=120, title="响应冷却时间", description="对同一视频的响应冷却时间(防止刷屏)")


class LocalApiConfig(BaseModel):
    """本地 API 相关配置"""

    enable: bool = Field(
        default=False,
        title="启用本地 API",
        description="是否启用本地 API",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    api_path: str = Field(
        default="bilichatapi",
        title="本地 API 挂载路径",
        description="本地 API 挂载路径",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    api_access_token: str = Field(
        default="",
        title="本地 API Token",
        description="本地 API Token",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    api_sub_dynamic_limit: str = Field(
        default="720/hour",
        title="动态订阅限速",
        description="动态订阅限速",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    api_sub_live_limit: str = Field(
        default="1800/hour",
        title="直播订阅限速",
        description="直播订阅限速",
        json_schema_extra={"ui:options": {"disabled": True}},
    )

    class Config:
        extra = "allow"


class RequestApiInfo(BaseModel):
    """请求 API 信息"""

    api: str = Field(default=..., title="API 地址", description="API 地址")
    token: str = Field(default=..., title="API Token", description="API Token, 服务端未设置则留空")
    weight: int = Field(default=1, title="权重", description="权重, 用于负载均衡, 越大越优先")
    enable: bool = Field(default=True, title="是否启用", description="是否启用")
    note: str = Field(default="", title="备注", description="备注")


class ApiConfig(BaseModel):
    """API 相关配置"""

    request_api: list[RequestApiInfo] = Field(
        default=[],
        title="API 请求列表",
        description="bilichat-request 的 API",
        json_schema_extra={"ui:options": {"showIndexNumber": True}},
    )
    local_api_config: LocalApiConfig = Field(
        default=LocalApiConfig(),
        title="本地 API 配置",
        description="本地 API 的配置",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    browser_shot_quality: int = Field(
        default=75, title="浏览器截图质量", description="浏览器截图质量, 范围为 10-100", ge=10, le=100
    )


class SubscribeConfig(BaseModel):
    """推送相关配置"""

    dynamic_interval: int = Field(default=300, title="动态轮询间隔", description="动态轮询间隔, 单位为秒", ge=15)
    live_interval: int = Field(default=60, title="直播轮询间隔", description="直播轮询间隔, 单位为秒", ge=10)
    push_delay: int = Field(default=3, title="推送延迟", description="每条推送的延迟, 单位为秒", ge=0)
    # users: list[UserInfo] = Field(default=[], title="已订阅用户", description="已添加订阅的用户")
    users_dict: dict[str, UserInfo] = Field(default={}, alias="users", exclude=True)

    @computed_field(
        title="用户", description="已添加订阅的用户", json_schema_extra={"ui:options": {"showIndexNumber": True}}
    )
    @property
    def users(self) -> list[UserInfo]:
        return list(self.users_dict.values())

    @field_validator("users_dict", mode="before")
    @classmethod
    def users_setter(cls, value: list[UserInfo] | dict[str, UserInfo]) -> dict[str, UserInfo]:
        if isinstance(value, list):
            users = {}
            for _user in value:
                user = UserInfo.model_validate(_user)
                users[user.id] = user
            return users
        else:
            return value


class Config(BaseModel):
    version: str = Field(
        default=version("nonebot_plugin_bilichat"),
        title="插件版本",
        description="插件版本",
        json_schema_extra={"ui:options": {"disabled": True}},
    )
    webui: WebUIConfig = Field(
        default=WebUIConfig(), title="WebUI 配置", description="WebUI 相关配置", json_schema_extra={"ui:hidden": True}
    )
    nonebot: NoneBotConfig = Field(default=NoneBotConfig(), title="nonebot 配置", description="nonebot 相关配置")
    api: ApiConfig = Field(default=ApiConfig(), title="API 配置", description="API 相关配置")
    analyze: AnalyzeConfig = Field(default=AnalyzeConfig(), title="内容解析配置", description="解析相关配置")
    subs: SubscribeConfig = Field(default=SubscribeConfig(), title="订阅配置", description="推送相关配置")

    @field_validator("version")
    @classmethod
    def _version_validator(cls, _: str) -> str:
        return version("nonebot_plugin_bilichat")
