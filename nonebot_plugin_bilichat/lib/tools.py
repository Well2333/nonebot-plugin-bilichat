import datetime
import re


def calc_time_total(t):
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


def obfuscate_urls_in_text(text, replacement_char="。"):
    """
    Obfuscates URLs in a given text by replacing '.' with a specified character and removing any protocol (http, https).

    Args:
    text (str): The text containing URLs.
    replacement_char (str): The character to replace '.' in URLs.

    Returns:
    str: The text with obfuscated URLs.
    """
    # Regular expression to find URLs
    url_regex = r"\b(?:https?://)?\S+\.\S+\b"

    def obfuscate_url(match):
        url = match.group(0)
        # Removing http or https if present
        url = url.replace("http://", "").replace("https://", "")
        # Replacing '.' with the specified character
        return url.replace(".", replacement_char)

    return re.sub(url_regex, obfuscate_url, text)
