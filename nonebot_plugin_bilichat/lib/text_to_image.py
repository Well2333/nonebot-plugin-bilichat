import re
from io import BytesIO
from pathlib import Path

import skia
from dynamicadaptor.Content import RichTextDetail, Text
from dynrender_skia.DynConfig import SetDynStyle
from dynrender_skia.DynText import BiliText
from nonebot.log import logger

from ..config import plugin_config
from .fonts_provider import get_font_sync
from .store import cache_dir

data_path = cache_dir.joinpath("render")
data_path.mkdir(parents=True, exist_ok=True)


render = BiliText(
    static_path=str(data_path),
    style=SetDynStyle(
        font_family=str(
            get_font_sync("HarmonyOS_Sans_SC_Medium.ttf")
            if plugin_config.bilichat_text_fonts == "default"
            else plugin_config.bilichat_text_fonts
        ),
        emoji_font_family=str(
            get_font_sync("nte.ttf")
            if plugin_config.bilichat_emoji_fonts == "default"
            else plugin_config.bilichat_emoji_fonts
        ),
        font_style="Normal",
    ).set_style,
)
cache = cache_dir.joinpath("text2image")
cache.mkdir(0o755, parents=True, exist_ok=True)
cache = str(cache.absolute())


async def rich_text2image(data: str, src: str):
    data = (
        f"AI Summarization, Powered by A60 & Well404 \nNLP Model: {src}\n====================================\n{data}"
    )
    image_array = await render.run(
        Text(
            text=data,
            topic=None,
            rich_text_nodes=[RichTextDetail(type="RICH_TEXT_NODE_TYPE_TEXT", text=data, orig_text=data, emoji=None)],
        )
    )
    bio = BytesIO()
    img = skia.Image.fromarray(image_array, colorType=skia.ColorType.kRGBA_8888_ColorType)
    img.save(bio)
    return bio.getvalue()


async def pw_text2image(data: str, src: str):
    import jinja2
    from nonebot_plugin_htmlrender import get_new_page

    from ..lib.browser import pw_font_injecter

    if src == plugin_config.bilichat_openai_model:
        src = "openai"
    else:
        src = "bilibili"
    data = r"\n".join(data.splitlines())

    summary = Path(__file__).parent.parent.joinpath("static", "summary")
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(summary),
        enable_async=True,
    )
    template_path = f"file:///{summary.joinpath('index.html').absolute()}".replace("////", "///")
    template = template_env.get_template("index.html")
    html = await template.render_async(
        **{
            "data": data,
            "src": src,
        }
    )

    async with get_new_page() as page:
        await page.route(re.compile("^https://fonts.bbot/(.+)$"), pw_font_injecter)
        await page.set_viewport_size({"width": 800, "height": 2000})
        await page.goto(template_path)
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(5)
        img_raw = await page.get_by_alt_text("main").screenshot(
            type="png",
        )
    return img_raw


async def t2i(data: str, src: str):
    try:
        if len(data.strip()) < 30:
            return data
        if plugin_config.bilichat_use_browser:
            return await pw_text2image(data, src)
        return await rich_text2image(data, src)
    except Exception as e:
        logger.exception(e)
        return f"总结图片生成失败 {e}\n {data}"
