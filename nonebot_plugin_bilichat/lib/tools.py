import datetime
from typing import Any


def calc_time_total(t: float):
    """
    Calculate the total time in a human-readable format.

    Args:
        t (float): The time in seconds.

    Returns:
        str: The total time in a human-readable format.

    Example:
        >>> calc_time_total(4.5)
        '4500 毫秒'
        >>> calc_time_total(3600)
        '1 小时'
        >>> calc_time_total(3660)
        '1 小时 1 分钟'

    """
    t = int(t * 1000)
    if t < 5000:
        return f"{t} 毫秒"

    timedelta = datetime.timedelta(seconds=t // 1000)
    day = timedelta.days
    hour, mint, sec = tuple(int(n) for n in str(timedelta).split(",")[-1].split(":"))

    total = ""
    if day:
        total += f"{day} 天 "
    if hour:
        total += f"{hour} 小时 "
    if mint:
        total += f"{mint} 分钟 "
    if sec and not day and not hour:
        total += f"{sec} 秒 "
    return total


def num_fmt(num: int):
    if num < 10000:
        return str(num)
    elif num < 100000000:
        return ("%.2f" % (num / 10000)) + "万"
    else:
        return ("%.2f" % (num / 100000000)) + "亿"


def shorten_long_items(
    obj: Any,  # noqa:
    max_length: int = 100,
    prefix_length: int = 10,
    suffix_length: int = 10,
    max_list_length: int = 50,
    list_prefix: int = 3,
    list_suffix: int = 1,
) -> Any:
    """
    递归遍历 JSON 对象, 缩短超过指定长度的字符串和列表。

    :param obj: 要处理的 JSON 对象(可以是 dict, list, str, etc.)
    :param max_length: 定义何时需要缩短的最大长度阈值
    :param prefix_length: 缩短后保留的前缀长度
    :param suffix_length: 缩短后保留的后缀长度
    :param max_list_length: 定义何时需要缩短的最大列表长度阈值
    :param list_prefix: 缩短后保留的列表前缀长度
    :param list_suffix: 缩短后保留的列表后缀长度
    :return: 处理后的 JSON 对象
    """

    if isinstance(obj, dict):
        return {k: shorten_long_items(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        if len(obj) > max_list_length:
            placeholder = f"...[total:{len(obj)}]..."
            shortened = obj[:list_prefix] + [placeholder] + obj[-list_suffix:]
            return [shorten_long_items(item) if item != placeholder else item for item in shortened]
        else:
            return [shorten_long_items(item) for item in obj]
    elif isinstance(obj, str):
        return f"{obj[:prefix_length]}...[total:{len(obj)}]...{obj[-suffix_length:]}" if len(obj) > max_length else obj
    elif isinstance(obj, tuple | set):
        processed = shorten_long_items(list(obj))
        return type(obj)(processed)
    else:
        return obj
