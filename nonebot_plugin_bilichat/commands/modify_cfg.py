from nonebot.log import logger
from nonebot.params import ArgPlainText
from nonebot.permission import SUPERUSER
from pydantic import ValidationError

from ..config import plugin_config
from ..model.api.subs_config import SUBS_CONFIG_NAME_MAPPING, SUBS_CONFIG_NAME_MAPPING_REVERSE
from ..subscribe.manager import SubscriptionSystem
from .base import bilichat

bili_modify_cfg = bilichat.command("cfg", permission=SUPERUSER, aliases=set(plugin_config.bilichat_cmd_modify_cfg))


@bili_modify_cfg.handle()
async def show_cfg_value():
    text = "\n".join(
        [
            f"{v}: {getattr(SubscriptionSystem.config,k) if 'rss' not in k else '**敏感信息，请通过webui查看**'}"
            for k, v in SUBS_CONFIG_NAME_MAPPING.items()
        ]
    )
    await bili_modify_cfg.send(f"当前配置为：\n{text}")


@bili_modify_cfg.got("cfg_text", prompt="请使用 “配置名 值” 的格式修改配置，例如：“全局订阅数量限制 5”")
async def modify_cfg_value(cfg_text: str = ArgPlainText()):
    try:
        cfg_name, new_value = cfg_text.strip().split(" ")
    except Exception:
        await bili_modify_cfg.reject(f"无法识别输入 “{cfg_text}” 请使用以下格式修改配置：\n全局订阅数量限制 5")

    cfg_key = SUBS_CONFIG_NAME_MAPPING_REVERSE.get(cfg_name)
    if not cfg_key:
        await bili_modify_cfg.reject(f"无法识别配置名 “{cfg_name}”")

    old_value = str(getattr(SubscriptionSystem.config, cfg_key))
    if old_value == new_value:
        await bili_modify_cfg.finish(f"{cfg_name} 已经是 {new_value} 了，未修改配置文件")

    try:
        logger.info(f"修改配置 {cfg_key}: {old_value} => {new_value}")
        cfg = SubscriptionSystem.dump_dict()
        cfg.update({"config": {cfg_key: new_value}})
        await SubscriptionSystem.load(cfg)
    except ValidationError as e:
        await bili_modify_cfg.finish(f"配置 {cfg_name} 无法修改为此值 {new_value}，参考原因：\n{e.errors()[0]['msg']}")
    except Exception as e:
        logger.exception(e)
        await bili_modify_cfg.finish(f"修改失败，请重试：{e}")

    await bili_modify_cfg.finish(f"已修改 {cfg_name}: {old_value} => {new_value}")
