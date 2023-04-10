from ..config import plugin_config
from nonebot.log import logger

if plugin_config.bilichat_openai_token:
    logger.info("Using openai as summarization tool")
    from .openai_summarise import openai_summarization as summarization
elif plugin_config.bilichat_newbing_cookie:
    logger.info("Using newbing as summarization tool")
    from .newbing_summarise import newbing_summarization as summarization
