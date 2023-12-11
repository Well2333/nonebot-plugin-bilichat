import importlib.util
import json
import sys
from pathlib import Path
from typing import List, Literal, Optional, Union

from nonebot import get_driver, require
from nonebot.log import logger
from pydantic import BaseModel, Field, validator

from .lib.store import cache_dir

# get package version
if sys.version_info < (3, 10):
    from importlib_metadata import version
else:
    from importlib.metadata import version

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
    bilichat_whitelist: List[str] = []
    bilichat_blacklist: List[str] = []
    bilichat_cd_time: int = 120
    bilichat_neterror_retry: int = 3
    bilichat_show_error_msg: bool = True
    bilichat_use_browser: bool = Field(default="Auto")
    bilichat_cache_serive: Literal["json", "mongodb"] = Field(default="Auto")
    bilichat_text_fonts: str = "default"
    bilichat_emoji_fonts: str = "default"

    # command and subscribe
    bilichat_subs_limit: int = Field(5, ge=0, le=50)
    bilichat_dynamic_interval: int = Field(90, ge=60)
    bilichat_live_interval: int = Field(30, ge=10)
    bilichat_push_delay: int = Field(3, ge=0)
    bilichat_dynamic_grpc: bool = False
    bilichat_command_to_me: bool = True
    bilichat_cmd_start: str = "bilichat"
    bilichat_cmd_add_sub: List[str] = ["订阅", "关注"]
    bilichat_cmd_remove_sub: List[str] = ["退订", "取关"]
    bilichat_cmd_check_sub: List[str] = ["查看", "查看订阅"]
    bilichat_cmd_reset_sub: List[str] = ["重置", "重置配置"]
    bilichat_cmd_at_all: List[str] = ["全体成员", "at全体"]
    bilichat_cmd_dynamic: List[str] = ["动态通知", "动态订阅"]
    bilichat_cmd_live: List[str] = ["直播通知", "直播订阅"]
    bilichat_cmd_checkdynamic: List[str] = ["查看动态"]

    # basic info
    bilichat_basic_info: bool = True
    bilichat_basic_info_style: Literal["bbot_default", "style_blue"] = Field(default="Auto")
    bilichat_basic_info_url: bool = True
    bilichat_reply_to_basic_info: bool = True

    # dynamic
    bilichat_dynamic: bool = True
    bilichat_dynamic_style: Literal["dynamicrender", "browser_mobile", "browser_pc"] = Field(default="Auto")
    bilichat_bilibili_cookie: Optional[str] = None
    bilichat_bilibili_cookie_api: Optional[str] = None

    # both WC and AI
    bilichat_use_bcut_asr: bool = True

    # Word Cloud
    bilichat_word_cloud: bool = False

    # AI Summary
    bilichat_summary_ignore_null: bool = True
    bilichat_official_summary: bool = False
    bilichat_openai_token: Optional[str] = None
    bilichat_openai_proxy: Optional[str] = None
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
            require("nonebot_plugin_mongodb")
            if v == "Auto":
                logger.info("bilichat_cache_serive can use MongoDB as cache serive")
            return "mongodb"
        except Exception as e:
            if v == "Auto":
                logger.info("bilichat_cache_serive can't use MongoDB as cache serive, using JsonFile")
                return "json"
            raise RuntimeError(
                "Package(s) of MongoDB not installed, "
                "use **pip install nonebot-plugin-bilichat[all]** to install required dependencies"
            ) from e

    @validator("bilichat_use_browser", always=True, pre=True)
    def check_htmlrender(cls, v):
        if not v:
            return v
        try:
            require("nonebot_plugin_htmlrender")
            if v == "Auto":
                logger.info("bilichat_use_browser dependencies have been satisfied, enable bilichat_use_browser")
            return True
        except Exception as e:
            if v == "Auto":
                logger.info("bilichat_use_browser's dependency is not satisfied, disable bilichat_use_browser")
                return False
            raise RuntimeError(
                "Package(s) of fuction styles not installed, "
                "use **pip install nonebot-plugin-bilichat[all]** to install required dependencies"
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
                f"style {v} require browser to work, please enable **bilichat_use_browser** or set style to Auto"
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
                f"style {v} require browser to work, please enable **bilichat_use_browser** or set style to Auto"
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
                raise ValueError("Config bilichat_browser_cookie got a problem occurred") from e

        elif Path(v).is_dir():
            raise ValueError(f"Config bilichat_browser_cookie requires a file, but {v} is a folder")

        elif v == "api":
            cookie_file = cache_dir.joinpath("bilibili_browser_cookies.json").absolute()
            cookie_file.touch(0o755)
            logger.info(f"create bilibili cookies file at {cookie_file.as_posix()}")
            return cookie_file.as_posix()

        else:
            raise ValueError(f"Path {v} is not recognized")

        return v

    @validator("bilichat_openai_proxy", always=True, pre=True)
    def check_openai_proxy(cls, v, values):
        if not values["bilichat_openai_token"]:
            return v
        if v is None:
            logger.warning(
                "you have enabled openai or newbing summary without a proxy, this may cause request failure."
            )
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
            logger.error(
                f"Model {model} has a token cap of {max_limit} instead of {v}, token will be replaced with {max_limit}"
            )
            v = max_limit
        return v

    @validator("bilichat_openai_token", always=True)
    def check_pypackage_openai(cls, v):
        if importlib.util.find_spec("tiktoken_async") or not v:
            return v
        else:
            raise RuntimeError(
                "Package(s) of fuction openai summary not installed, "
                "use **pip install nonebot-plugin-bilichat[summary]** to install required dependencies"
            )

    @validator("bilichat_word_cloud", always=True)
    def check_pypackage_wordcloud(cls, v):
        if (importlib.util.find_spec("wordcloud") and importlib.util.find_spec("jieba")) or not v:
            return v
        else:
            raise RuntimeError(
                "Package(s) of fuction wordcloud not installed, "
                "use **pip install nonebot-plugin-bilichat[wordcloud]** to install required dependencies"
            )

    def verify_permission(self, uid: Union[str, int]):
        if self.bilichat_whitelist:
            return str(uid) in self.bilichat_whitelist
        elif self.bilichat_blacklist:
            return str(uid) not in self.bilichat_blacklist
        else:
            return True


raw_config = get_driver().config
plugin_config = Config.parse_obj(raw_config)
