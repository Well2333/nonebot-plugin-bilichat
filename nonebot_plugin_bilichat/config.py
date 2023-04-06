import sys
from typing import Literal, Optional, Sequence, Union

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
    bilichat_enable_v12_channel: bool = True
    bilichat_enable_unkown_src: bool = False
    bilichat_whitelist: Sequence[str] = []
    bilichat_blacklist: Sequence[str] = []
    bilichat_dynamic_font: Optional[str]
    bilichat_cd_time: int = 120

    # both WC and AI
    bilichat_use_bcut_asr: bool = True
    
    # Word Cloud
    bilichat_word_cloud : bool = True

    # AI Summary
    bilichat_openai_token: Optional[str]
    bilichat_openai_proxy: Optional[str]
    bilichat_openai_model: Literal[
        "gpt-3.5-turbo-0301", "gpt-4-0314", "gpt-4-32k-0314"
    ] = "gpt-3.5-turbo-0301"
    bilichat_openai_token_limit: int = 3500

    @validator("bilichat_openai_proxy")
    def check_openai_proxy(cls, v, values):
        if values["bilichat_openai_token"] is None:
            return v
        if v is None:
            logger.warning(
                "you have enabled openai summary without a proxy, this may cause request failure."
            )
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
    
    def verify_permission(self,uid:Union[str,int]):
        if self.bilichat_whitelist:
            return str(uid) in self.bilichat_whitelist
        elif self.bilichat_blacklist:
            return str(uid) not in self.bilichat_blacklist
        else:
            return True


plugin_config = Config.parse_obj(get_driver().config)
