from nonebot.log import logger

try:
    from . import onebot_v11

    logger.success("OneBot V11 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import onebot_v12

    logger.success("OneBot V12 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import mirai2

    logger.success("mirai2 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import qqguild

    logger.success("QQ Guild adapter was loaded successfully")
except Exception:
    pass
