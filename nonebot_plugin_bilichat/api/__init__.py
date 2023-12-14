from typing import List

from nonebot.log import logger

from ..config import plugin_config, raw_config

if plugin_config.bilichat_api_path:
    from . import base, bilibili_cookies, subs_config  # noqa: F401

    def generate_framed_text(content: List[str], width=88, padding=4):
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

    propmt = [
        "SETTING UP BILICHAT API AT",
        f"http://{raw_config.host}:{raw_config.port}/{plugin_config.bilichat_api_path}/api/",
    ]
    if plugin_config.bilichat_api_path == "bilichat":
        propmt.extend(
            [
                "WARNING: Bilichat API is currently running on default path. "
                "Please consider to use different path via adding config `bilichat_api_path` in .env file.",
            ]
        )
    logger.success("\n" + generate_framed_text(propmt))
