import time

from pydantic import BaseModel, Field


class PartOutline(BaseModel):
    timestamp: int
    content: str


class Outline(BaseModel):
    title: str
    """分段标题"""
    part_outline: list[PartOutline]
    """分段中的细分内容"""
    timestamp: int


class ModelResult(BaseModel):
    result_type: int
    summary: str
    """视频总结"""
    outline: list[Outline]
    """分段总结"""

    @staticmethod
    def _format_ts(ts: int):
        return time.strftime("%M:%S", time.gmtime(ts))

    def markdown(self) -> str:
        ls = [f"{self.summary}"]
        for o in self.outline:
            ls.append(f"- {o.title}")
            for p in o.part_outline:
                ls.append(f"    + *{self._format_ts(p.timestamp)}* {p.content}")
        msg = "\n".join(ls).replace('"', '\\"')
        return msg


class SummaryApiResponse(BaseModel):
    code: int
    result: ModelResult = Field(alias="model_result")
    stid: str
    status: int
    like_num: int
    dislike_num: int
