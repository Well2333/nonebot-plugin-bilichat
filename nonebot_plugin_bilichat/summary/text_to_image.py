from io import BytesIO
import re
from pathlib import Path

from dynamicadaptor.Content import RichTextDetail, Text
from minidynamicrender.DynConfig import ConfigInit
from minidynamicrender.DynText import DynTextRender
from nonebot.log import logger

from ..config import plugin_config
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


async def pw_text2image(data: str, src: str):
    import jinja2
    from nonebot_plugin_htmlrender import get_new_page
    from ..lib.browser import pw_font_injecter

    src = "openai" if src == plugin_config.bilichat_openai_model else "newbing"
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
        if len(data) < 30:
            return data
        if plugin_config.bilichat_basic_info_style != "bbot_default":
            return await pw_text2image(data, src)
        return await rich_text2image(data, src)
    except Exception as e:
        logger.exception(e)
        return f"总结图片生成失败 {e}\n {data}"
