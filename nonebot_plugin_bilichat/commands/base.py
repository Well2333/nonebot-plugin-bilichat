from nonebot.permission import SUPERUSER
from nonebot.plugin import CommandGroup
from nonebot.rule import to_me

from ..config import plugin_config

bilichat = CommandGroup(
    plugin_config.bilichat_command_start,
    permission=SUPERUSER,
    rule=to_me() if plugin_config.bilichat_command_to_me else None,
)
