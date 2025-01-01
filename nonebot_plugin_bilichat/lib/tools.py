import datetime
import re
import string
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


def get_cut_str(str_in, cut):
    """
    自动断行, 用于 Pillow 等不会自动换行的场景
    """
    punc = """，,、。.？?（）》】“"‘'；;：:！!·`~%^& """
    si = 0
    i = 0
    next_str = str_in
    str_list = []

    while re.search(r"\n\n\n\n\n", next_str):
        next_str = re.sub(r"\n\n\n\n\n", "\n", next_str)
    for s in next_str:
        si += 1 if s in string.printable else 2
        i += 1
        if next_str == "":
            break
        elif next_str[0] == "\n":
            next_str = next_str[1:]
        elif s == "\n":
            str_list.append(next_str[: i - 1])
            next_str = next_str[i - 1 :]
            si = 0
            i = 0
            continue
        if si > cut:
            try:
                if next_str[i] in punc:
                    i += 1
            except IndexError:
                str_list.append(next_str)
                return str_list
            str_list.append(next_str[:i])
            next_str = next_str[i:]
            si = 0
            i = 0
    str_list.append(next_str)
    i = 0
    non_wrap_str = []
    for p in str_list:
        if p == "":
            break
        elif p[-1] == "\n":
            p = p[:-1]
        non_wrap_str.append(p)
        i += 1
    return non_wrap_str


def generate_framed_text(content: list[str], width=88, padding=4):
    """
    Generates a framed text block with specified width and padding.

    Parameters:
    content (list of str): The content to be framed.
    width (int): The total width of the framed block including the border.
    padding (int): The padding between the text and the border.

    Returns:
    str: The framed text block.
    """
    # Calculate the width available for text
    text_width = width - 2 - (padding * 2)
    framed_lines = []

    # Function to split lines according to text_width and padding
    def split_line(line):
        words = line.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= text_width:
                current_line += word + " "
            else:
                framed_lines.append(current_line.rstrip())
                current_line = word + " "
        framed_lines.append(current_line.rstrip())

    # Process each line in the content
    for line in content:
        split_line(line)

        # Adding an empty line between paragraphs
        if line != content[-1]:
            framed_lines.append("")

    # Add padding and border to each line
    framed_text = "\n".join(
        ["*" + " " * padding + line.ljust(text_width) + " " * padding + "*" for line in framed_lines]
    )
    # Add the top and bottom border
    border = "*" * width
    line = "*" + " " * (width - 2) + "*"
    framed_text = border + "\n" + line + "\n" + framed_text + "\n" + line + "\n" + border

    return framed_text


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
