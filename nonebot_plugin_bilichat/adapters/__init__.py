from nonebot.log import logger

try:
    from . import onebot_v11  # noqa: F401

    logger.success("OneBot V11 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import onebot_v12  # noqa: F401

    logger.success("OneBot V12 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import mirai2  # noqa: F401

    logger.success("mirai2 adapter was loaded successfully")
except Exception:
    pass

try:
    from . import qq  # noqa: F401

    logger.success("QQ adapter was loaded successfully")
except Exception:
    pass
