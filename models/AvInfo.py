import json


class AvInfo(object):
    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url
        self.releaseDate = ""
        self.productCode = ""
        self.actors = []
        self.hls = {}

    def __repr__(self):
        return f"タイトル：{self.title}, URL：{self.url}, hls{self.hls}"

    def __str__(self):
        return f"タイトル：{self.title}, URL：{self.url}, hls{self.hls}"

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "releaseDate": self.releaseDate,
            "productCode": self.productCode,
            "actors": self.actors,
            "hls": self.hls,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)
