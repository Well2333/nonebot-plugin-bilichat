import re
from typing import Any, Dict, List, Literal

from nonebot.log import logger
from pydantic import BaseModel, validator
from typing_extensions import Literal

from .exception import (
    BingChatAccountReachLimitException,
    BingChatInvalidSessionException,
    BingChatResponseException,
    BingChatUnknownException,
)


class BingChatResponse(BaseModel):
    raw: Dict[Any, Any]

    @validator("raw")
    def raw_validator(cls, v: Dict[Any, Any]) -> Dict[Any, Any]:
        logger.debug(v)
        if v.get("item", {}).get("result", {}).get("value") == "Throttled":
            logger.error("<Bing账号到达今日请求上限>")
            raise BingChatAccountReachLimitException("<Bing账号到达今日请求上限>")

        if v.get("item", {}).get("result", {}).get("value") == "InvalidSession":
            logger.error("<无效的会话>")
            raise BingChatInvalidSessionException("<无效的会话>")

        if (
            v.get("item", {}).get("result", {}).get("value") == "Success"
            and len(v.get("item", {}).get("messages", [])) >= 2
            and v.get("item", {}).get("messages", [])[1].get("offense", "None") != "None"
        ):
            logger.error("<Bing检测到冒犯性文字，拒绝回答")
            raise BingChatResponseException("<Bing检测到冒犯性文字，拒绝回答>")

        if (
            v.get("item", {}).get("result", {}).get("value") == "Success"
            and len(v.get("item", {}).get("messages", [])) >= 2
            and v.get("item", {}).get("messages", [])[1].get("hiddenText", "")
        ):
            hidden_text = v.get("item", {}).get("messages", [])[1].get("hiddenText")
            logger.error(f"<Bing检测到敏感问题，自动隐藏>\n{hidden_text}")
            raise BingChatResponseException(f"<Bing检测到敏感问题，自动隐藏>\n{hidden_text}")

        if (
            v.get("item", {}).get("result", {}).get("value") == "Success"
            and len(v.get("item", {}).get("messages", [])) >= 2
            and v.get("item", {}).get("messages", [])[1].get("text", "")
        ):
            return v

        logger.error("<未知的错误>")
        raise BingChatUnknownException("<未知的错误, 请管理员查看控制台>")

    @staticmethod
    def remove_quote_str(string: str) -> str:
        return re.sub(r"\[\^\d+?\^]", "", string)

    @property
    def content_answer(self):
        return self.remove_quote_str(self.raw["item"]["messages"][1]["text"])

    @property
    def content_reference(self):
        return "\n".join(f"- {i}" for i in self.source_attributions_url_list)

    @property
    def content_suggested_question(self):
        print(self.suggested_question_list)
        return "\n".join(f"- {i}" for i in self.suggested_question_list)

    def adaptive_cards(self) -> List[str]:
        return list(self.raw["item"]["messages"][1]["adaptiveCards"][0]["body"])

    @property
    def source_attributions_url_list(self):
        return [i["seeMoreUrl"] for i in self.raw["item"]["messages"][1]["sourceAttributions"]]

    @property
    def suggested_question_list(self):
        return [i["text"] for i in self.raw["item"]["messages"][1]["suggestedResponses"]]

    def get_content(self, type: Literal["answer", "reference", "suggested-question"] = "answer"):
        if type == "answer":
            return self.content_answer
        elif type == "reference":
            return self.content_reference
        elif type == "suggested-question":
            return self.content_suggested_question
        else:
            raise TypeError(f"<无效的类型：{type}>")
