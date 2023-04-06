import asyncio
import random
from collections import OrderedDict
from typing import Dict, List, Optional

import httpx
import tiktoken_async
from loguru import logger

from ..config import plugin_config
from ..model.openai import AISummary

if plugin_config.bilichat_openai_token:
    logger.info("Loading OpenAI Token enc model")
    tiktoken_enc = asyncio.run(
        tiktoken_async.encoding_for_model(plugin_config.bilichat_openai_model)
    )
    logger.success(f"Enc model {tiktoken_enc.name} load successfully")


def get_user_prompt(title: str, transcript: str) -> List[Dict[str, str]]:
    title = title.replace("\n", " ").strip() if title else ""
    transcript = transcript.replace("\n", " ").strip() if transcript else ""
    language = "Chinese"
    sys_prompt = (
        "Your output should use the following template:\n## 总结\n## 要点\n"
        "- [Emoji] Bulletpoint\n\n"
        "Your task is to summarise the video I have given you in up to 2 to 6 concise bullet points, "
        "starting with a short highlight, each bullet point is at least 15 words. "
        "Choose an appropriate emoji for each bullet point. "
        "Use the video above: {{Title}} {{Transcript}}."
        "If you think that the content in the transcript is meaningless, "
        "Or if there is very little content that cannot be well summarized, "
        "then you can simply output the two words 'no meaning'. Remember, not to output anything else."
    )
    return get_full_prompt(
        f'Title: "{title}"\nTranscript: "{transcript}"', sys_prompt, language
    )


def count_tokens(prompts: List[Dict[str, str]]):
    """根据内容计算 token 数"""

    if plugin_config.bilichat_openai_model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4
        tokens_per_name = -1
    elif plugin_config.bilichat_openai_model == "gpt-4":
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
    text_data: List[str], token_limit: int = plugin_config.bilichat_openai_token_limit
):
    unique_texts = list(OrderedDict.fromkeys(text_data))
    while count_tokens(get_user_prompt("", " ".join(unique_texts))) > token_limit:
        unique_texts.pop(random.randint(0, len(unique_texts) - 1))
    return " ".join(unique_texts)


def get_full_prompt(
    prompt: str, system: Optional[str] = None, language: Optional[str] = None
):
    plist: List[Dict[str, str]] = []
    if system:
        plist.append({"role": "system", "content": system})
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
    return plist


async def openai_req(
    prompt_message: List[Dict[str, str]],
    token: Optional[str] = plugin_config.bilichat_openai_token,
    model: str = plugin_config.bilichat_openai_model,
) -> AISummary:
    async with httpx.AsyncClient(
        proxies=plugin_config.bilichat_openai_proxy,  # type: ignore
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
        },
        timeout=100,
    ) as client:
        req = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": model,
                "messages": prompt_message,
            },
        )
        if req.status_code != 200:
            return AISummary(error=True, message=req.text, raw=req.json())
        logger.info(
            f"[OpenAI] Response:\n{req.json()['choices'][0]['message']['content']}"
        )
        logger.info(f"[OpenAI] Response token usage: {req.json()['usage']}")
        return AISummary(
            summary=req.json()["choices"][0]["message"]["content"], raw=req.json()
        )
