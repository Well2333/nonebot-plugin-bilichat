from typing import List

from nonebot.log import logger

from ..config import plugin_config, raw_config

if plugin_config.bilichat_webui_url:
    from . import base, bilibili_cookies, subs  # noqa: F401

    def generate_framed_text(content: List[str], width=88, padding=4):
        """
        Generates a text frame around the given content.

        Parameters:
        content (list[str]): The content to be framed.
        width (int): The total width of the framed text, including borders.
        padding (int): The padding between the content and the frame.

        Returns:
        str: The framed text.
        """

        # Calculate the inner width (width - borders - padding)
        inner_width = width - 2 - (padding * 2)

        # Initialize an empty list to store each line of the framed text
        framed_text = []

        # Add the top border
        framed_text.append("*" * width)

        # Process each line of the content
        for line in content:
            # Split long lines into multiple lines
            while len(line) > inner_width:
                # Extract a substring of the maximum allowed length
                substring = line[:inner_width]
                # Add padding and borders to the substring
                framed_text.append("*" + " " * padding + substring + " " * padding + "*")
                # Remove the processed substring from the original line
                line = line[inner_width:]

            # Add padding and borders to the line
            line = line + " " * (inner_width - len(line))  # Padding for short lines
            framed_text.append("*" + " " * padding + line + " " * padding + "*")

        # Add the bottom border
        framed_text.append("*" * width)

        # Join the framed text lines with newlines and return
        return "\n".join(framed_text)

    propmt = [
        "",
        "SETTING UP BILICHAT WEB USER INTERFACE AT",
        "",
        f"http://{raw_config.host}:{raw_config.port}/{plugin_config.bilichat_webui_url}/web/",
        "",
    ]
    if plugin_config.bilichat_webui_url == "bilichat":
        propmt.extend(
            [
                "WARNING: Bilichat WebUI is currently running on default path. "
                "Please consider to use different path via adding config `bilichat_webui_url` in .env file. ",
                "",
            ]
        )
    logger.success("\n" + generate_framed_text(propmt))
