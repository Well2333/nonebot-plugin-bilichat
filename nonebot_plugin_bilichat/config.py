from pydantic import BaseModel, validator
from nonebot import get_driver
from typing import Sequence, Literal, Optional
from nonebot.log import logger
from yarl import URL


class Config(BaseModel):
    # general
    bili_block: bool = False
    bili_whitelist: Sequence[int] = []
    
    bili_use_bcut_asr: bool = True

    # AI Summary
    bili_openai_token: Optional[str]
    bili_openai_proxy: Optional[URL]
    bili_openai_model: Literal[
        "gpt-3.5-turbo-0301", "gpt-4-0314", "gpt-4-32k-0314"
    ] = "gpt-3.5-turbo-0301"
    bili_openai_token_limit: int = 3500

    @validator("bili_openai_proxy")
    def check_openai_proxy(cls, v, values):
        if values["bili_openai_token"] is None:
            return v
        if v is None:
            logger.warning(
                "you have enabled openai summary without a proxy, this may cause request failure."
            )
        return v

    @validator("bili_openai_token_limit")
    def check_token_limit(cls, v, values):
        if values["bili_openai_token"] is None:
            return v
        if not isinstance(v, int):
            v = int(v)
        model = values["bili_openai_model"]
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


plugin_config = Config.parse_obj(get_driver().config)
