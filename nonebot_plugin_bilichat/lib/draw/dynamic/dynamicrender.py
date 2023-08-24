from io import BytesIO
from typing import Dict

import skia
from dynamicadaptor.DynamicConversion import formate_message
from dynrender_skia.Core import DynRender

from ...fonts_provider import get_font_sync
from ...store import cache_dir

data_path = cache_dir.joinpath("render")
data_path.mkdir(parents=True, exist_ok=True)


render = DynRender(
    static_path=str(data_path),
    font_family=str(get_font_sync("HarmonyOS_Sans_SC_Medium.ttf")),
    emoji_font_family=str(get_font_sync("nte.ttf")),
)


async def skia_dynamic(dynid: str, raw: Dict, raw_type: str, **kwargs):
    if dynamic_formate := await formate_message(raw_type, raw):
        img_bio = BytesIO()
        image_array = await render.run(dynamic_formate)
        img = skia.Image.fromarray(image_array, colorType=skia.ColorType.kRGBA_8888_ColorType)
        img.save(img_bio)
        return img_bio.getvalue()
