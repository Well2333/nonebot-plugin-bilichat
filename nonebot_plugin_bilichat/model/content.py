from typing import List

class Video:
    def __init__(self, aid: int, cid: int, title: str):
        self.aid: int = aid
        self.cid: int = cid
        self.title: str = title


class Column:
    def __init__(self, cvid: int, title: str, text: List[str]):
        self.aid: int = cvid
        self.cid: str = "0"
        self.title: str = title
        self.text: List[str] = text
