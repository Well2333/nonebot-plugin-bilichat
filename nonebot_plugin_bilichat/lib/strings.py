import re
import string
import random


def num_fmt(num: int):
    if num < 10000:
        return str(num)
    elif num < 100000000:
        return ("%.2f" % (num / 10000)) + "万"
    else:
        return ("%.2f" % (num / 100000000)) + "亿"


def get_cut_str(str_in, cut):
    """
    自动断行，用于 Pillow 等不会自动换行的场景
    """
    punc = """，,、。.？?）》】“"‘'；;：:！!·`~%^& """
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
            next_str = next_str[i - 1:]
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


def getCutStr(str_in, cut):
    cut_str = str_in
    si = 0
    i = 0
    for s in str_in:
        si += 2 if "\u4e00" <= s <= "\u9fff" else 1
        i += 1
        if si > cut:
            cut_str = f"{str_in[:i]}...."
            break

    return cut_str


def generate_verify_code():
    return str(random.randint(100000, 999999))
