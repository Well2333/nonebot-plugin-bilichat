import time
from os import PathLike
from pathlib import Path
from typing import List, Literal, Optional, Union, Tuple

import httpx
from loguru import logger

from ..model.bcut_asr import (
    ResourceCompleteRspSchema,
    ResourceCreateRspSchema,
    ResultRspSchema,
    TaskCreateRspSchema,
)

__version__ = "0.0.2"

API_REQ_UPLOAD = (
    "https://member.bilibili.com/x/bcut/rubick-interface/resource/create"  # 申请上传
)
API_COMMIT_UPLOAD = "https://member.bilibili.com/x/bcut/rubick-interface/resource/create/complete"  # 提交上传
API_CREATE_TASK = "https://member.bilibili.com/x/bcut/rubick-interface/task"  # 创建任务
API_QUERY_RESULT = (
    "https://member.bilibili.com/x/bcut/rubick-interface/task/result"  # 查询结果
)

SUPPORT_SOUND_FORMAT = Literal["flac", "aac", "m4a", "mp3", "wav"]


class APIError(Exception):
    "接口调用错误"

    def __init__(self, code, msg) -> None:
        self.code = code
        self.msg = msg
        super().__init__()

    def __str__(self) -> str:
        return f"{self.code}:{self.msg}"


class BcutASR:
    "必剪 语音识别接口"
    session: httpx.AsyncClient
    sound_name: str
    sound_bin: bytes
    sound_fmt: SUPPORT_SOUND_FORMAT
    __in_boss_key: str
    __resource_id: str
    __upload_id: str
    __upload_urls: List[str]
    __per_size: int
    __clips: int
    __etags: List[str]
    __download_url: str
    task_id: str

    def __init__(self, file: Optional[Union[str, PathLike]] = None) -> None:
        self.session = httpx.AsyncClient()
        self.task_id = ""
        self.__etags = []
        if file:
            self.set_data(file)

    def set_data(
        self,
        _file: Optional[Union[str, PathLike]] = None,
        raw_data: Optional[bytes] = None,
        data_fmt: Optional[SUPPORT_SOUND_FORMAT] = None,
    ) -> None:
        "设置欲识别的数据"
        if _file:
            if not isinstance(_file, (str, PathLike)):
                raise TypeError("unknow file ptr")
            # 文件类
            _file = Path(_file)
            self.sound_bin = open(_file, "rb").read()
            suffix = data_fmt or _file.suffix[1:]
            self.sound_name = _file.name
        elif raw_data:
            # bytes类
            self.sound_bin = raw_data
            suffix = data_fmt
            self.sound_name = f"{int(time.time())}.{suffix}"
        else:
            raise ValueError("none set data")
        if suffix not in ("flac", "aac", "m4a", "mp3", "wav"):
            raise TypeError("format is not support")
        self.sound_fmt = suffix  # type: ignore
        logger.debug(f"file loading complete: {self.sound_name}")

    async def upload(self) -> None:
        "申请上传"
        if not self.sound_bin or not self.sound_fmt:
            raise ValueError("none set data")
        resp = await self.session.post(
            API_REQ_UPLOAD,
            data={
                "type": 2,
                "name": self.sound_name,
                "size": len(self.sound_bin),
                "resource_file_type": self.sound_fmt,
                "model_id": 7,
            },
        )
        resp.raise_for_status()
        resp = resp.json()
        if code := resp["code"]:
            raise APIError(code, resp["message"])
        resp_data = ResourceCreateRspSchema.parse_obj(resp["data"])
        self.__in_boss_key = resp_data.in_boss_key
        self.__resource_id = resp_data.resource_id
        self.__upload_id = resp_data.upload_id
        self.__upload_urls = resp_data.upload_urls
        self.__per_size = resp_data.per_size
        self.__clips = len(resp_data.upload_urls)
        logger.info(
            f"Upload success, total size {resp_data.size // 1024}KB, "
            f"Total {self.__clips} clip(s), clip(s) size {resp_data.per_size // 1024}KB: {self.__in_boss_key}"
        )
        await self.__upload_part()
        await self.__commit_upload()

    async def __upload_part(self) -> None:
        "上传音频数据"
        for clip in range(self.__clips):
            start_range = clip * self.__per_size
            end_range = (clip + 1) * self.__per_size
            logger.debug(f"Uploading clip {clip}: {start_range}-{end_range}")
            resp = await self.session.put(
                self.__upload_urls[clip],
                data=self.sound_bin[start_range:end_range],  # type: ignore
            )
            resp.raise_for_status()
            etag = resp.headers.get("Etag")
            self.__etags.append(etag)
            logger.debug(f"Clip {clip} uploaded: {etag}")

    async def __commit_upload(self) -> None:
        "提交上传数据"
        resp = await self.session.post(
            API_COMMIT_UPLOAD,
            data={
                "in_boss_key": self.__in_boss_key,
                "resource_id": self.__resource_id,
                "etags": ",".join(self.__etags),
                "upload_id": self.__upload_id,
                "model_id": 7,
            },
        )
        resp.raise_for_status()
        resp = resp.json()
        if code := resp["code"]:
            raise APIError(code, resp["message"])
        resp_data = ResourceCompleteRspSchema.parse_obj(resp["data"])
        self.__download_url = resp_data.download_url
        logger.debug("commit complete")

    async def create_task(self) -> str:
        "开始创建转换任务"
        resp = await self.session.post(
            API_CREATE_TASK, json={"resource": self.__download_url, "model_id": "7"}
        )
        resp.raise_for_status()
        resp = resp.json()
        if code := resp["code"]:
            raise APIError(code, resp["message"])
        resp_data = TaskCreateRspSchema.parse_obj(resp["data"])
        self.task_id = resp_data.task_id
        logger.info(f"Conversion task created: {self.task_id}")
        return self.task_id

    async def result(self, task_id: Optional[str] = None) -> ResultRspSchema:
        "查询转换结果"
        resp = await self.session.get(
            API_QUERY_RESULT, params={"model_id": 7, "task_id": task_id or self.task_id}
        )
        resp.raise_for_status()
        resp = resp.json()
        if code := resp["code"]:
            raise APIError(code, resp["message"])
        return ResultRspSchema.parse_obj(resp["data"])
