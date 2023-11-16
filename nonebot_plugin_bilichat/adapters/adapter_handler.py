from typing import Callable, Dict

from nonebot.log import logger

PUSH_HANDLER: Dict[str, Callable] = {}
ID_HANDLER: Dict[str, Callable] = {}
UP_HANDLER: Dict[str, Callable] = {}

try:
    from .onebot_v11 import adapter_handler as onebot_v11

    PUSH_HANDLER["OneBot V11"] = onebot_v11.push
    ID_HANDLER["OneBot V11"] = onebot_v11.get_user_id
    UP_HANDLER["OneBot V11"] = onebot_v11.get_activate_ups
except Exception as e:
    logger.error(e)

try:
    from .mirai2 import adapter_handler as mirai2

    PUSH_HANDLER["mirai2"] = mirai2.push
    ID_HANDLER["mirai2"] = mirai2.get_user_id
    UP_HANDLER["mirai2"] = mirai2.get_activate_ups
except Exception as e:
    logger.error(e)