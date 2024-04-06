import random
from collections import OrderedDict
from typing import Dict, List, Literal, Optional

import httpx
import tiktoken
from nonebot.log import logger

from ..config import plugin_config
from ..model.openai import OpenAI, TokenUsage

logger.info("加载 OpenAI Token enc 模型, 这可能需要一段时间进行下载")
tiktoken_enc = tiktoken.encoding_for_model(plugin_config.bilichat_openai_model)
logger.success(f"Enc 模型 {tiktoken_enc.name} 加载成功")


def get_summarise_prompt(title: str, transcript: str, type_: Literal["视频字幕", "专栏文章"] = "视频字幕"):
    title = title.replace("\n", " ").strip() if title else ""
    transcript = transcript.replace("\n", " ").strip() if transcript else ""
    return get_full_prompt(
        prompt=(
            f"使用以下Markdown模板为我总结{type_}数据，除非{type_[2:]}中的内容无意义，或者内容较少无法总结，或者未提供{type_[2:]}数据，或者无有效内容，你就不使用模板回复，只回复“无意义”："
            "\n## 概述"
            "\n{内容，尽可能精简总结内容不要太详细}"
            "\n## 要点"
            "\n- {使用不重复并合适的emoji，仅限一个，禁止重复} {内容不换行大于15字，可多项，条数与有效内容数量呈正比}"
            "\n不要随意翻译任何内容。仅使用中文总结。"
            "\n不说与总结无关的其他内容，你的回复仅限固定格式提供的“概述”和“要点”两项。"
            f"{type_[:2]}标题为“{title}”，{type_}数据如下，立刻开始总结：“{transcript}”"
        )
    )


def count_tokens(prompts: List[Dict[str, str]]):
    """根据内容计算 token 数"""

    if plugin_config.bilichat_openai_model.startswith("gpt-3.5"):
        tokens_per_message = 4
        tokens_per_name = -1
    elif plugin_config.bilichat_openai_model.startswith("gpt-4"):
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise ValueError(f"Unknown model name {plugin_config.bilichat_openai_model}")

    num_tokens = 0
    for message in prompts:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(tiktoken_enc.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens


def get_small_size_transcripts(
    title: str, text_data: List[str], token_limit: int = plugin_config.bilichat_openai_token_limit
):
    unique_texts = list(OrderedDict.fromkeys(text_data))
    while count_tokens(get_summarise_prompt(title, " ".join(unique_texts))) > token_limit:
        unique_texts.pop(random.randint(0, len(unique_texts) - 1))
    return " ".join(unique_texts)


def get_full_prompt(prompt: Optional[str] = None, system: Optional[str] = None, language: Optional[str] = None):
    plist: List[Dict[str, str]] = []
    if system:
        plist.append({"role": "system", "content": system})
    if prompt:
        plist.append({"role": "user", "content": prompt})
    if language:
        plist.extend(
            (
                {
                    "role": "assistant",
                    "content": "What language do you want to output?",
                },
                {"role": "user", "content": language},
            )
        )
    if not plist:
        raise ValueError("No prompt provided")
    return plist


async def openai_req(
    prompt_message: List[Dict[str, str]],
    token: Optional[str] = plugin_config.bilichat_openai_token,
    model: str = plugin_config.bilichat_openai_model,
    temperature: Optional[float] = None,
    api_base: str = plugin_config.bilichat_openai_api_base,
):
    if not token:
        return OpenAI(error=True, message="未配置 OpenAI API Token")
    async with httpx.AsyncClient(
        proxies=plugin_config.bilichat_openai_proxy,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
        },
        timeout=100,
    ) as client:
        data = {
            "model": model,
            "messages": prompt_message,
        }
        if temperature:
            data["temperature"] = temperature
        req = await client.post(f"{api_base}/v1/chat/completions", json=data)
        if req.status_code != 200:
            return OpenAI(error=True, message=req.text, raw=req.json())
        logger.info(f"[OpenAI] Response:\n{req.json()['choices'][0]['message']['content']}")
        usage = req.json()["usage"]
        logger.info(f"[OpenAI] Response 实际 token 消耗: {usage}")
        return OpenAI(
            response=req.json()["choices"][0]["message"]["content"],
            raw=req.json(),
            token_usage=TokenUsage(**usage),
        )
