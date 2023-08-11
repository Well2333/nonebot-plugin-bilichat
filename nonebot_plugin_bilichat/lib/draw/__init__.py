from ...config import plugin_config
from ..fonts_provider import get_font_sync
from .video import VideoImage  # noqa: F401

font_semibold = str(get_font_sync("sarasa-mono-sc-semibold.ttf"))
font_bold = str(get_font_sync("sarasa-mono-sc-bold.ttf"))
font_vanfont = str(get_font_sync("vanfont.ttf"))


if plugin_config.bilichat_basic_info_style == "bbot_default":
    from .video import bbot_default  # noqa: F401
elif plugin_config.bilichat_basic_info_style == "style_blue":
    from .video import style_blue  # noqa: F401
