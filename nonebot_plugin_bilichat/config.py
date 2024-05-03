import importlib.util
import json
from importlib.metadata import version
from pathlib import Path
from typing import Literal

from nonebot import get_driver, get_plugin_config, require
from nonebot.log import logger
from pydantic import BaseModel, Field, validator

from .lib.store import cache_dir

try:
    __version__ = version("nonebot_plugin_bilichat")
except Exception:
    __version__ = None


class Config(BaseModel):
    # general
    bilichat_block: bool = False
    bilichat_enable_self: bool = False
    bilichat_only_self: bool = False
    bilichat_only_to_me: bool = False
    bilichat_whitelist: list[str] = []
    bilichat_blacklist: list[str] = []
    bilichat_cd_time: int = 120
    bilichat_neterror_retry: int = 3
    bilichat_show_error_msg: bool = True
    bilichat_use_browser: bool = Field(default="Auto")
    bilichat_browser_shot_quality: int = Field(default=75, ge=10, le=100)
    bilichat_cache_serive: Literal["json", "mongodb"] = Field(default="Auto")
    bilichat_text_fonts: str = "default"
    bilichat_emoji_fonts: str = "default"
    bilichat_webui_path: str | None = "bilichat"

    # command and subscribe
    bilichat_command_to_me: bool = True
    bilichat_cmd_start: str = "bilichat"
    bilichat_cmd_add_sub: list[str] = ["订阅", "关注"]
    bilichat_cmd_remove_sub: list[str] = ["退订", "取关"]
    bilichat_cmd_check_sub: list[str] = ["查看", "查看订阅"]
    bilichat_cmd_reset_sub: list[str] = ["重置", "重置配置"]
    bilichat_cmd_at_all: list[str] = ["全体成员", "at全体"]
    bilichat_cmd_dynamic: list[str] = ["动态通知", "动态订阅"]
    bilichat_cmd_live: list[str] = ["直播通知", "直播订阅"]
    bilichat_cmd_checkdynamic: list[str] = ["查看动态"]
    bilichat_cmd_fetch: list[str] = ["获取内容", "解析内容"]
    bilichat_cmd_check_login: list[str] = ["查看登录账号"]
    bilichat_cmd_login_qrcode: list[str] = ["扫码登录"]
    bilichat_cmd_logout: list[str] = ["登出账号"]

    # basic info
    bilichat_basic_info: bool = True
    bilichat_basic_info_style: Literal["bbot_default", "style_blue"] = Field(default="Auto")
    bilichat_basic_info_url: bool = True
    bilichat_reply_to_basic_info: bool = True

    # dynamic
    bilichat_dynamic: bool = True
    bilichat_dynamic_style: Literal["dynamicrender", "browser_mobile", "browser_pc"] = Field(default="Auto")
    bilichat_bilibili_cookie: str | None = None

    # both WC and AI
    bilichat_use_bcut_asr: bool = True

    # Word Cloud
    bilichat_word_cloud: bool = False
    bilichat_word_cloud_size: list[int] = [1000, 800]

    # AI Summary
    bilichat_summary_ignore_null: bool = True
    bilichat_official_summary: bool = False
    bilichat_openai_token: str | None = None
    bilichat_openai_proxy: str | None = None
    bilichat_openai_model: Literal[
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k-0314",
    ] = "gpt-3.5-turbo-0301"
    bilichat_openai_token_limit: int = 3500
    bilichat_openai_api_base: str = "https://api.openai.com"

    @validator("bilichat_cache_serive", always=True, pre=True)
    def check_cache_serive(cls, v):
        if v == "json":
            return v
        try:
            if not importlib.util.find_spec("nonebot_plugin_mongodb"):
                raise ImportError
            require("nonebot_plugin_mongodb")
            if v == "Auto":
                logger.info("bilichat_cache_serive 可以使用 MongoDB 作为缓存服务")
            return "mongodb"
        except Exception as e:
            if v == "Auto":
                logger.info("bilichat_cache_serive 无法使用 MongoDB 作为缓存服务, 使用 JSON 文件作为缓存服务")
                return "json"
            raise RuntimeError(
                "未安装 MongoDB 所需依赖, 使用 **pip install nonebot-plugin-bilichat[all]** 来安装所需依赖"
            ) from e

    @validator("bilichat_use_browser", always=True, pre=True)
    def check_htmlrender(cls, v):
        if not v:
            return v
        try:
            require("nonebot_plugin_htmlrender")
            if v == "Auto":
                logger.info("bilichat_use_browser 所需依赖已安装，采用浏览器渲染模式")
            return True
        except Exception as e:
            if v == "Auto":
                logger.info("bilichat_use_browser 所需依赖未安装，采用绘图渲染模式")
                return False
            raise RuntimeError(
                "浏览器渲染依赖未安装, 请选择其他渲染模式或使用 **pip install nonebot-plugin-bilichat[all]** 来安装所需依赖"
            ) from e

    @validator("bilichat_basic_info_style", always=True, pre=True)
    def check_use_browser_basic(cls, v, values):
        if v == "bbot_default":
            return v
        # 不包含浏览器
        if values["bilichat_use_browser"] is not True:
            if v == "Auto":
                return "bbot_default"
            raise RuntimeError(
                f"样式 {v} 需要浏览器渲染, 请开启 **bilichat_use_browser** 或设置 bilichat_basic_info_style 为 Auto"
            )
        # 包含浏览器
        return "style_blue" if v == "Auto" else v

    @validator("bilichat_dynamic_style", always=True, pre=True)
    def check_use_browser_dynamic(cls, v, values):
        if v == "dynamicrender":
            return v
        # 不包含浏览器
        if values["bilichat_use_browser"] is not True:
            if v == "Auto":
                return "dynamicrender"
            raise RuntimeError(
                f"样式 {v} 需要浏览器渲染, 请开启 **bilichat_use_browser** 或设置 bilichat_dynamic_style 为 Auto"
            )
        # 包含浏览器
        return "browser_mobile" if v == "Auto" else v

    @validator("bilichat_bilibili_cookie", always=True)
    def check_bilibili_cookie(cls, v):
        if not v:
            return v
        # verify cookie file
        if Path(v).is_file():
            try:
                json.loads(Path(v).read_text("utf-8"))
            except Exception as e:
                raise ValueError(f"无法读取 bilichat_bilibili_cookie: {v}") from e

        elif Path(v).is_dir():
            raise ValueError(f"bilichat_browser_cookie 需要一个文件, 而 {v} 是一个文件夹")

        elif v == "api":
            cookie_file = cache_dir.joinpath("bilibili_browser_cookies.json").absolute()
            cookie_file.touch(0o755)
            logger.info(f"在 {cookie_file.as_posix()} 创建 bilichat_bilibili_cookie 文件")
            return cookie_file.as_posix()

        else:
            raise ValueError(f"路径 {v} 无法识别")

        return v

    @validator("bilichat_openai_proxy", always=True, pre=True)
    def check_openai_proxy(cls, v, values):
        if not values["bilichat_openai_token"]:
            return v
        if v is None:
            logger.warning("你设置了 bilichat_openai_token 但未设置 bilichat_openai_proxy ，这可能会导致请求失败.")
        return v

    @validator("bilichat_openai_token_limit")
    def check_token_limit(cls, v, values):
        if values["bilichat_openai_token"] is None:
            return v
        if not isinstance(v, int):
            v = int(v)
        model: str = values["bilichat_openai_model"]
        if model.startswith("gpt-3.5"):
            max_limit = 15000 if "16k" in model else 3500
        elif model.startswith("gpt-4"):
            max_limit = 32200 if "32k" in model else 7600
        else:
            max_limit = 3500
        if v > max_limit:
            logger.error(f"模型 {model} 的 token 上限为 {max_limit} 而不是 {v}, token 将被重置为 {max_limit}")
            v = max_limit
        return v

    @validator("bilichat_openai_token", always=True)
    def check_pypackage_openai(cls, v):
        if importlib.util.find_spec("tiktoken") or not v:
            return v
        else:
            raise RuntimeError(
                "openai 依赖未安装, 使用 **pip install nonebot-plugin-bilichat[summary]** 来安装所需依赖"
            )

    @validator("bilichat_word_cloud", always=True)
    def check_pypackage_wordcloud(cls, v):
        if (importlib.util.find_spec("wordcloud") and importlib.util.find_spec("jieba")) or not v:
            return v
        else:
            raise RuntimeError(
                "wordcloud 依赖未安装, 使用 **pip install nonebot-plugin-bilichat[wordcloud]** 来安装所需依赖"
            )

    @validator("bilichat_webui_path", always=True)
    def check_api(cls, v: str):
        if not v:
            return v
        v = v.strip("/")
        if "/" in v:
            raise ValueError("bilichat_webui_path 不应包含 '/'")
        return v

    def verify_permission(self, uid: str | int) -> bool:
        if self.bilichat_whitelist:
            return str(uid) in self.bilichat_whitelist
        elif self.bilichat_blacklist:
            return str(uid) not in self.bilichat_blacklist
        else:
            return True


raw_config = get_driver().config
plugin_config = get_plugin_config(Config)
