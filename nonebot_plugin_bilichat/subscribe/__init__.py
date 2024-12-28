from nonebot import get_driver
from nonebot.log import logger
from nonebot_plugin_uninfo.target import to_target

from nonebot_plugin_bilichat.config import plugin_config

driver = get_driver()


async def refresh_online_users():
    logger.info("重新检查可推送的用户")
    async with plugin_config.push._modify_lock:
        plugin_config.push._online_users.clear()
        for user in plugin_config.push.users.values():
            target = to_target(user.info)
            try:
                bot = await target.select()
                logger.info(f"用户 [{user.info.id}] 在线, 可用的bot: {bot}")
                plugin_config.push._online_users[user.info.id] = user
            except Exception as e:
                logger.warning(f"用户 [{user.info.id}] 未在线: {e}")
        logger.info(f"当前可推送的用户: {plugin_config.push._online_users}")


driver.on_bot_connect(refresh_online_users)
driver.on_bot_disconnect(refresh_online_users)
