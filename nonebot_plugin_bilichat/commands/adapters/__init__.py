from typing import Callable, Dict

PUSH_HANDLER: Dict[str, Callable] = {}
ID_HANDLER: Dict[str, Callable] = {}
UP_HANDLER: Dict[str, Callable] = {}

try:
    from . import onebot_v11

    PUSH_HANDLER["OneBot V11"] = onebot_v11.push
    ID_HANDLER["OneBot V11"] = onebot_v11.get_user_id
    UP_HANDLER["OneBot V11"] = onebot_v11.get_activate_ups
except Exception:
    pass

try:
    from . import onebot_v12
except Exception:
    pass

try:
    from . import mirai2

    PUSH_HANDLER["mirai2"] = mirai2.push
    ID_HANDLER["mirai2"] = mirai2.get_user_id
    UP_HANDLER["mirai2"] = mirai2.get_activate_ups
except Exception:
    pass

try:
    from . import qqguild
except Exception:
    pass
