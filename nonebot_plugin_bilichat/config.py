import importlib.util
import json
import sys
from pathlib import Path
from typing import List, Literal, Optional, Union

from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseModel, validator

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
    bilichat_enable_private: bool = True
    bilichat_enable_self: bool = False
    bilichat_enable_v12_channel: bool = True
    bilichat_enable_unkown_src: bool = False
    bilichat_whitelist: List[str] = []
    bilichat_blacklist: List[str] = []
    bilichat_dynamic_font: Optional[str]
    bilichat_cd_time: int = 120
    bilichat_neterror_retry = 3
    nickname: List[str] = ["awesome-nonebot"]

    # basic info
    bilichat_basic_info: bool = True
    bilichat_reply_to_basic_info: bool = True

    # both WC and AI
    bilichat_use_bcut_asr: bool = True

    # Word Cloud
    bilichat_word_cloud: bool = True

    # AI Summary
    bilichat_newbing_cookie: Optional[str]
    bilichat_newbing_token_limit: int = 0
    bilichat_newbing_preprocess: bool = True
    bilichat_openai_token: Optional[str]
    bilichat_openai_proxy: Optional[str]
    bilichat_openai_model: Literal["gpt-3.5-turbo-0301", "gpt-4-0314", "gpt-4-32k-0314"] = "gpt-3.5-turbo-0301"
    bilichat_openai_token_limit: int = 3500

    @validator("nickname")
    def check_nickname(cls, v):
        return list(v) or ["awesome-nonebot"]

    @validator("bilichat_openai_proxy")
    def check_openai_proxy(cls, v, values):
        if not (values["bilichat_openai_token"] or values["bilichat_newbing_cookie"]):
            return v
        if v is None:
            logger.warning("you have enabled openai summary without a proxy, this may cause request failure.")
        return v

    @validator("bilichat_openai_token_limit")
    def check_token_limit(cls, v, values):
        if values["bilichat_openai_token"] is None:
            return v
        if not isinstance(v, int):
            v = int(v)
        model = values["bilichat_openai_model"]
        max_limit = {
            "gpt-3.5-turbo-0301": 3500,
            "gpt-4-0314": 7600,
            "gpt-4-32k-0314": 32200,
        }.get(model, 3500)
        if v > max_limit:
            logger.error(
                f"Model {model} has a token cap of {max_limit} instead of {v}, token will be replaced with {max_limit}"
            )
            v = max_limit
        return v

    @validator("bilichat_openai_token", always=True)
    def check_pypackage_openai(cls, v):
        if (importlib.util.find_spec("tiktoken_async") and importlib.util.find_spec("minidynamicrender")) or not v:
            return v
        else:
            raise RuntimeError(
                "Package(s) of fuction openai summary not installed, use **nb plugin install nonebot-plugin-bilichat[openai]** to install required dependencies"
            )

    @validator("bilichat_newbing_cookie", always=True)
    def check_pypackage_newbing_and_cookie(cls, v):
        if not v:
            return v
        if not importlib.util.find_spec("EdgeGPT") or not importlib.util.find_spec("minidynamicrender"):
            raise RuntimeError(
                "Package(s) of fuction newbing summary not installed, use **nb plugin install nonebot-plugin-bilichat[newbing]** to install required dependencies"
            )

        # verify cookie file
        try:
            if Path(v).is_file():
                json.loads(Path(v).read_text("utf-8"))
        except Exception as e:
            raise ValueError("Config bilichat_newbing_cookie got a problem occurred") from e

        return v

    @validator("bilichat_word_cloud", always=True)
    def check_pypackage_wordcloud(cls, v):
        if (importlib.util.find_spec("wordcloud") and importlib.util.find_spec("jieba")) or not v:
            return v
        else:
            raise RuntimeError(
                "Package(s) of fuction wordcloud not installed, use **nb plugin install nonebot-plugin-bilichat[wordcloud]** to install required dependencies"
            )

    def verify_permission(self, uid: Union[str, int]):
        if self.bilichat_whitelist:
            return str(uid) in self.bilichat_whitelist
        elif self.bilichat_blacklist:
            return str(uid) not in self.bilichat_blacklist
        else:
            return True


plugin_config = Config.parse_obj(get_driver().config)
