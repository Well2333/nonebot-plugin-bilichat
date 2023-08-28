from nonebot.log import logger

try:
    from sentry_sdk import capture_exception  # type: ignore
except ImportError:
    logger.warning("sentry_sdk is not installed")

    def capture_exception():
        logger.debug("an error has occurred, but sentry_sdk is not installed")
