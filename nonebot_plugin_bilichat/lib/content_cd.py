from datetime import datetime, timedelta

from nonebot.exception import FinishedException
from nonebot.log import logger

from ..config import config


class BilichatCD:
    cd: dict[str, dict[str, datetime]] = {}  # {content_id: {session_id: datetime_to_expire}}
    cd_size_limit = config.analyze.cd_time // 2
    expiration_duration = timedelta(seconds=config.analyze.cd_time)

    @classmethod
    def check_cd(cls, session_id: str, content_id: str):
        logger.trace(f"当前记录信息: {cls.cd}")
        logger.trace(f"content:{content_id} session:{session_id}")
        content_record = cls.cd.get(content_id, {})
        now = datetime.now()

        if session_id in content_record and content_record[session_id] > now:
            logger.warning(f"会话 [{session_id}] 的重复内容 [{content_id}]. 跳过解析")
            raise FinishedException
        elif "global" in content_record and content_record["global"] > now:
            logger.warning(f"会话 [全局] 的重复内容 [{content_id}]. 跳过解析")
            raise FinishedException
        else:
            cls.record_cd(session_id, content_id)

    @classmethod
    def record_cd(cls, session_id: str, content_id: str) -> None:
        content_record = cls.cd.get(content_id, {})
        now = datetime.now()

        # Clean up expired entries
        cls.clean_expired_entries(content_record, now)

        # Record new entry
        content_record[session_id] = now + cls.expiration_duration
        cls.cd[content_id] = content_record

    @classmethod
    def clean_expired_entries(cls, content_record: dict[str, datetime], current_time: datetime) -> None:
        expired_entries = [
            session_id for session_id, expire_time in content_record.items() if expire_time <= current_time
        ]
        for session_id in expired_entries:
            del content_record[session_id]
