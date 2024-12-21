from importlib.metadata import version
from pathlib import Path

from nonebot import get_driver, get_plugin_config, require
from nonebot.log import logger
from pydantic import BaseModel, Field

try:
    __version__ = version("nonebot_plugin_bilichat")
except Exception:
    __version__ = None


require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store  # noqa: E402

cache_dir = store.get_cache_dir("nonebot_plugin_bilichat")
data_dir = store.get_data_dir("nonebot_plugin_bilichat")
static_dir = Path(__file__).parent.parent.joinpath("static")

logger.info(f"nonebot_plugin_bilichat 缓存文件夹 ->  {cache_dir.absolute()}")
logger.info(f"nonebot_plugin_bilichat 数据文件夹 ->  {data_dir.absolute()}")


class RequestApiInfo(BaseModel):
    api: str
    """API 地址"""
    token: str
    """API Token, 服务端未设置则留空"""
    weight: int = 1
    """权重, 用于负载均衡, 越大越优先"""


class Config(BaseModel):
    # bilichat_request 相关
    bilichat_request_api: list[RequestApiInfo] = []
    """bilichat-request 的 API, 留空则会本地启动"""
    bilichat_enable_local_api: bool = False
    """是否启用本地 API"""
    bilichat_local_api_token: str = ""
    """本地 API 的 Token"""
    bilichat_browser_shot_quality: int = Field(default=75, ge=10, le=100)
    """浏览器截图质量, 范围为 10-100"""

    # 解析相关
    bilichat_video: bool = True
    """是否解析视频"""
    bilichat_dynamic: bool = True
    """是否解析动态"""
    bilichat_column: bool = True
    """是否解析专栏"""

    # 会话控制
    bilichat_block: bool = False
    """是否拦截事件(防止其他插件二次解析)"""
    bilichat_enable_self: bool = False
    """是否允许响应自身的消息"""
    bilichat_only_self: bool = False
    """是否仅响应自身的消息, 开启后会覆盖全部其他规则(人机合一特供)"""
    bilichat_only_to_me: bool = False
    """非自身消息是否需要 @机器人 或使用机器人的昵称才响应"""
    bilichat_whitelist: list[str] = []
    """响应的会话名单, 会覆盖黑名单"""
    bilichat_blacklist: list[str] = []
    """不响应的会话名单"""
    bilichat_cd_time: int = 120
    """对同一视频的响应冷却时间(防止刷屏)"""

    # 推送控制
    bilichat_subs_limit: int = Field(5, ge=0, le=50)
    """全局订阅数量限制"""
    bilichat_dynamic_interval: int = Field(90, ge=10)
    """动态轮询间隔, 单位为秒"""
    bilichat_live_interval: int = Field(30, ge=10)
    """直播轮询间隔, 单位为秒"""
    bilichat_push_delay: int = Field(3, ge=0)
    """每条推送的延迟, 单位为秒"""

    # 指令
    bilichat_command_to_me: bool = True
    """命令是否需要@机器人或使用机器人的昵称才响应"""
    bilichat_cmd_start: str = "bilichat"
    """命令的起始词, 可设置为空"""
    bilichat_cmd_add_sub: list[str] = ["订阅", "关注"]
    """`sub`命令的别名"""
    bilichat_cmd_remove_sub: list[str] = ["退订", "取关"]
    """`unsub`命令的别名"""
    bilichat_cmd_check_sub: list[str] = ["查看", "查看订阅"]
    """`check`命令的别名"""
    bilichat_cmd_reset_sub: list[str] = ["重置", "重置配置"]
    """`reset`命令的别名"""
    bilichat_cmd_at_all: list[str] = ["全体成员", "at全体"]
    """`atall`命令的别名"""
    bilichat_cmd_dynamic: list[str] = ["动态通知", "动态订阅"]
    """`dynamic`命令的别名"""
    bilichat_cmd_live: list[str] = ["直播通知", "直播订阅"]
    """`live`命令的别名"""
    bilichat_cmd_checkdynamic: list[str] = ["查看动态"]
    """`checkdynamic`命令的别名"""
    bilichat_cmd_fetch: list[str] = ["获取内容", "解析内容"]
    """`fetch`命令的别名"""
    bilichat_cmd_check_login: list[str] = ["查看登录账号"]
    """`check_login`命令的别名"""
    bilichat_cmd_login_qrcode: list[str] = ["扫码登录"]
    """`qrlogin`命令的别名"""
    bilichat_cmd_logout: list[str] = ["登出账号"]
    """`logout`命令的别名"""
    bilichat_cmd_modify_cfg: list[str] = ["修改配置"]
    """`cfg`命令的别名"""


raw_config = get_driver().config
plugin_config = get_plugin_config(Config)
