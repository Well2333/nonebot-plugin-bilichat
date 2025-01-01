from nonebot import get_driver

from .fetch_and_push import dynamic, live
from .status import SubsStatus

driver = get_driver()

driver.on_bot_connect(SubsStatus.refresh_online_users)
driver.on_bot_disconnect(SubsStatus.refresh_online_users)

__all__ = ["dynamic", "live"]
