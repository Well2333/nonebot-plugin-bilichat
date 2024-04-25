import re
import string


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
