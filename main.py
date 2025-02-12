import asyncio
from missAv import (
    getAvPageNumMax,
    getAvTitleInfoAll,
    getM3U8List,
    dumpAvListToFile,
)
import downloader

CAPTURE_DICT = {
    "無修正リーク": "dm620/ja/uncensored-leak",
    "今日最も閲覧された": "dm291/ja/today-hot",
    "美園和花": "dm81/ja/actresses/美園和花",
    "楓カレン": "dm37/ja/actresses/楓カレン%20%28田中レモン%29",
}


async def main():
    target = list(CAPTURE_DICT.values())[0]

    totalPageNum = getAvPageNumMax(target)
    print(f"totalPageNum: {totalPageNum}")
    if totalPageNum == 0:
        print("ページ数取得エラー")
        return

    # テストで5ページまで取得
    totalPageNum = 1
    avList = getAvTitleInfoAll(target, 1, totalPageNum)
    getM3U8List(avList)
    dumpAvListToFile(avList)

    for i in range(1, 3):
        title = avList[i].title
        url = avList[i].hls["source"]
        downloader.download_stream(title, url)


if __name__ == "__main__":
    asyncio.run(main())
