from importlib.metadata import version

from pydantic import BaseModel, Field

from .subscribe import User


class LocalApiConfig(BaseModel):
    enable: bool = False
    """是否启用本地 API"""
    api_path: str = "bilichatapi"
    """本地 API 挂载路径"""
    api_access_token: str = ""
    """本地 API Token, 服务端未设置则留空"""
    api_sub_dynamic_limit: str = "720/hour"
    """动态订阅限速"""
    api_sub_live_limit: str = "1800/hour"
    """直播订阅限速"""
    
    class Config:
        extra = "allow"


class NoneBotConfig(BaseModel):
    """nonebot 相关配置, 无法热修改"""

    block: bool = False
    """是否拦截事件(防止其他插件二次解析)"""
    enable_self: bool = False
    """是否允许响应自身的消息"""
    only_self: bool = False
    """是否仅响应自身的消息, 开启后会覆盖全部其他规则(人机合一特供)"""
    only_to_me: bool = False
    """非自身消息是否需要 @机器人 或使用机器人的昵称才响应"""
    command_to_me: bool = True
    """命令是否需要@机器人或使用机器人的昵称才响应"""
    cmd_start: str = "bilichat"
    """命令的起始词, 可设置为空"""
    cmd_add_sub: list[str] = ["订阅", "关注"]
    """`sub`命令的别名"""
    cmd_remove_sub: list[str] = ["退订", "取关"]
    """`unsub`命令的别名"""
    cmd_check_sub: list[str] = ["查看", "查看订阅"]
    """`check`命令的别名"""
    cmd_reset_sub: list[str] = ["重置", "重置配置"]
    """`reset`命令的别名"""
    cmd_at_all: list[str] = ["全体成员", "at全体"]
    """`atall`命令的别名"""
    cmd_dynamic: list[str] = ["动态通知", "动态订阅"]
    """`dynamic`命令的别名"""
    cmd_live: list[str] = ["直播通知", "直播订阅"]
    """`live`命令的别名"""
    cmd_checkdynamic: list[str] = ["查看动态"]
    """`checkdynamic`命令的别名"""
    cmd_fetch: list[str] = ["获取内容", "解析内容"]
    """`fetch`命令的别名"""
    cmd_check_login: list[str] = ["查看登录账号"]
    """`check_login`命令的别名"""
    cmd_login_qrcode: list[str] = ["扫码登录"]
    """`qrlogin`命令的别名"""
    cmd_logout: list[str] = ["登出账号"]
    """`logout`命令的别名"""
    cmd_modify_cfg: list[str] = ["修改配置"]
    """`cfg`命令的别名"""


class AnalyzeConfig(BaseModel):
    """解析相关配置"""

    video: bool = True
    """是否解析视频"""
    dynamic: bool = True
    """是否解析动态"""
    column: bool = True
    """是否解析专栏"""
    whitelist: list[str] = []
    """响应的会话名单, 会覆盖黑名单"""
    blacklist: list[str] = []
    """不响应的会话名单"""
    cd_time: int = 120
    """对同一视频的响应冷却时间(防止刷屏)"""


class RequestApiInfo(BaseModel):
    api: str
    """API 地址"""
    token: str
    """API Token, 服务端未设置则留空"""
    weight: int = 1
    """权重, 用于负载均衡, 越大越优先"""
    enabled: bool = True
    """是否启用"""
    note: str = ""
    """备注"""


class ApiConfig(BaseModel):
    """API 相关配置"""

    request_api: list[RequestApiInfo] = []
    """bilichat-request 的 API, 留空则会本地启动"""
    local_api_config: LocalApiConfig | None = None
    """本地 API 的配置"""
    browser_shot_quality: int = Field(default=75, ge=10, le=100)
    """浏览器截图质量, 范围为 10-100"""


class SubscribeConfig(BaseModel):
    """推送相关配置"""

    subs_limit: int = Field(5, ge=0, le=50)
    """全局订阅数量限制"""
    dynamic_interval: int = Field(180, ge=15)
    """动态轮询间隔, 单位为秒"""
    live_interval: int = Field(60, ge=10)
    """直播轮询间隔, 单位为秒"""
    push_delay: int = Field(3, ge=0)
    """每条推送的延迟, 单位为秒"""

    # 推送数据
    users: dict[str, User] = {}
    """已添加订阅的用户"""


class Config(BaseModel):
    version: str = version("nonebot_plugin_bilichat")
    """插件版本"""
    nonebot: NoneBotConfig = NoneBotConfig()
    """nonebot 相关配置, 无法热修改"""
    analyze: AnalyzeConfig = AnalyzeConfig()
    """解析相关配置"""
    api: ApiConfig = ApiConfig()
    """API 相关配置"""
    subs: SubscribeConfig = SubscribeConfig()  # type: ignore
    """推送相关配置"""
