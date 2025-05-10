from nonebot.log import logger
from packaging.version import Version


def v6_1_2(raw_config: dict) -> dict:
    logger.info("Migrating 6.1.2 --> 6.2.0")
    raw_config["version"] = "6.2.0"
    n_users: list[dict] = []
    o_users: dict[str, dict] = raw_config["subs"]["users"]
    for o_v in o_users.values():
        o_subs = o_v.get("subscribes", {})
        n_subs = list(o_subs.values()) if o_subs else []

        n_user = {
            "info": o_v["info"],
            "subscribes": n_subs,
        }
        n_users.append(n_user)
    raw_config["subs"]["users"] = n_users
    return raw_config


def v6_2_5(raw_config: dict) -> dict:
    logger.info("Migrating 6.2.0 --> 6.2.5")
    raw_config["version"] = "6.2.5"
    for api in raw_config["api"]["request_api"]:
        api: dict
        # if has key "enabled", change to "enable"
        if "enabled" in api:
            api["enable"] = api.pop("enabled")
        else:
            api["enable"] = False
    return raw_config


def migrate(raw_config: dict):
    version = Version(raw_config.get("version", "0.0.0"))
    if version <= Version("6.1.2"):
        raw_config = v6_1_2(raw_config)
    if version <= Version("6.2.5"):
        raw_config = v6_2_5(raw_config)

    return raw_config
