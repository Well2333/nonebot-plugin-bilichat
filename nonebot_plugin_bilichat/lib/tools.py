import datetime


def calc_time_total(t: float | int):
    """
    Calculate the total time in a human-readable format.

    Args:
        t (float | int): The time in seconds.

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
