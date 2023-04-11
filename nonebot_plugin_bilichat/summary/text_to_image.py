from io import BytesIO

from dynamicadaptor.Content import RichTextDetail, Text
from minidynamicrender.DynConfig import ConfigInit
from minidynamicrender.DynText import DynTextRender

from ..lib.fonts_provider import get_font
from ..lib.store import cache_dir


cache = cache_dir.joinpath("text2image")
cache.mkdir(0o755, parents=True, exist_ok=True)
cache = str(cache.absolute())


async def rich_text2image(data: str, src: str):
    config = ConfigInit(
        data_path=cache,
        font_path={
            "text": str(await get_font("HarmonyOS_Sans_SC_Medium.ttf")),
            "extra_text": str(await get_font("sarasa-mono-sc-bold.ttf")),
            "emoji": str(await get_font("nte.ttf")),
        },
    )
    data = f"AI Summarization, Powered by A60 & Well404 \nNLP Model: {src}\n==========================================={data}"
    if config.dyn_color and config.dyn_font and config.dy_size:
        render = DynTextRender(config.static_path, config.dyn_color, config.dyn_font, config.dy_size)
        image = await render.run(
            Text(
                text=data,
                topic=None,
                rich_text_nodes=[
                    RichTextDetail(type="RICH_TEXT_NODE_TYPE_TEXT", text=data, orig_text=data, emoji=None)
                ],
            )
        )
        if image:
            bio = BytesIO()
            image.convert("RGB").save(bio, "jpeg", optimize=True)
            return bio.getvalue()
