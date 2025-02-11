from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from myHttp import requestHttp
from models.AvInfo import AvInfo

MISSAV_URL = "https://missav.ws/"
executor = ThreadPoolExecutor(max_workers=10)


def getAvPageNumMax(path: str) -> int:
    return getMissAvTotalPageNum(path)


def getAvTitleInfoAll(path: str, startPage: int = 1, lastPage: int = 1) -> list[AvInfo]:
    titleAllInfo = []
    # with ThreadPoolExecutor(max_workers=1) as executor:

    results = executor.map(
        getAvTitleInfo,
        [f"{MISSAV_URL}{path}?page={i}" for i in range(startPage, lastPage + 1)],
    )
    for result in results:
        titleAllInfo.extend(result)

    # for i in range(startPage, lastPage + 1):
    #     future = executor.submit(getAvTitleInfo, f"{MISSAV_URL}{path}?page={i}")
    #     titleAllInfo.extend(future.result())
    return titleAllInfo


def getAvTitleInfo(path: str) -> list:
    html = requestHttp(path)
    if html:
        return analyzeAvList(html)
    return []


def getMissAvTotalPageNum(path: str) -> int:
    html = requestHttp(f"{MISSAV_URL}{path}")
    if html:
        return analyzeTotalPageNum(html)
    return 0


def analyzeTotalPageNum(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    print(soup.find("form", class_="relative").text.strip())

    # ページ数を取得
    import re

    pattern = re.compile(r"/\s(\d.*)")
    text = soup.find("form", class_="relative").text.strip()
    result = re.match(pattern, text)

    if result.group(1):
        return int(result.group(1))
    return 0


def analyzeAvList(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")

    avList = []
    for item in soup.find_all("a", class_="text-secondary"):
        title = item.text.strip()
        url = item.get("href")
        avList.append(AvInfo(title, url))  # strip()メソッドを使用

    return avList


def getM3U8List(avList: list[AvInfo]):
    for av in avList:
        future = executor.submit(getM3U8, av)
        future.result()
        print(av.to_json())


def getM3U8(avInfo: AvInfo):
    html = requestHttp(avInfo.url)
    if html == None:
        return None

    soup = BeautifulSoup(html, "html.parser")
    avInfo.releaseDate = soup.find_all("span", text="配信開始日:")[
        0
    ].next_sibling.next_sibling.text
    avInfo.productCode = soup.find_all("span", text="品番:")[
        0
    ].next_sibling.next_sibling.text

    actorElements = soup.find_all("span", text="女優:")
    if actorElements:
        actorElement = actorElements[0].previous_element.previous_element.find_all("a")
        avInfo.actors = [actor.text for actor in actorElement]

    start = html.find("m3u8|")
    end = html.find("playlist|source") + len("playlist|source")
    s = html[start:end].split("|")
    hlsUrlDic = {}
    if html[start - 1] == "'":  # m3u8が先頭にある
        baseUrl = f"{s[8]}://{s[7]}.{s[6]}/{s[5]}-{s[4]}-{s[3]}-{s[2]}-{s[1]}"
        videoExt = f"{s[9]}.{s[0]}"
        if len(s) == 16:  # 1080p and 720p
            playlistExt = f"{s[14]}.{s[0]}"
            hlsUrlDic[s[11]] = f"{baseUrl}/{s[12]}/{videoExt}"  # 1080p
            hlsUrlDic[s[13]] = f"{baseUrl}/{s[10]}/{videoExt}"  # 720p
            hlsUrlDic[s[15]] = f"{baseUrl}/{playlistExt}"  # playlist
        elif len(s) == 15:  # 720p
            playlistExt = f"{s[13]}.{s[0]}"
            hlsUrlDic[s[11]] = ""
            hlsUrlDic[s[12]] = f"{baseUrl}/{s[10]}/{videoExt}"  # 720p
            hlsUrlDic[s[14]] = f"{baseUrl}/{playlistExt}"  # playlist
        else:
            print("m3u8ファイルが取得できませんでした")
    else:
        # 特殊パターンがたまにある（m3u8が先頭にない）
        start = html.find("|m3u8|") - 4
        end = html.find("playlist|source") + len("playlist|source")
        s = html[start:end].split("|")
        baseUrl = f"{s[7]}://{s[6]}.{s[5]}/{s[4]}-{s[0]}-{s[0]}-{s[3]}-{s[2]}"
        videoExt = f"{s[8]}.{s[1]}"
        if len(s) == 15:  # 1080p and 720p
            playlistExt = f"{s[13]}.{s[0]}"
            hlsUrlDic[s[10]] = f"{baseUrl}/{s[9]}/{videoExt}"  # 1080p
            hlsUrlDic[s[12]] = f"{baseUrl}/{s[11]}/{videoExt}"  # 720p
            hlsUrlDic[s[14]] = f"{baseUrl}/{playlistExt}"  # playlist
        else:
            print("m3u8ファイルが取得できませんでした")

    if len(hlsUrlDic) > 0:
        avInfo.hls["source"] = hlsUrlDic["source"]
        avInfo.hls["source1280"] = hlsUrlDic["source1280"]
        avInfo.hls["source842"] = hlsUrlDic["source842"]

    # f=\\\'8://7.6/5-4-3-2-1/e.0\\\';
    # d=\\\'8://7.6/5-4-3-2-1/c/9.0\\\';
    # b=\\\'8://7.6/5-4-3-2-1/a/9.0\\\';


def getM3U8onSeleniumList(avList: list):
    with ProcessPoolExecutor(max_workers=1) as executor:
        for av in avList:
            future = executor.submit(getM3U8, av.url)
            av.m3u8 = future.result()
            print(av.to_json())


def getM3U8onSelenium(url: str) -> str:
    # Chromeのオプションを設定（ヘッドレスモード）
    chrome_options = Options()
    # ヘッドレスだとうまく取れない
    # chrome_options.add_argument("--headless=new")

    # ChromeDriverのパスを指定してブラウザを起動
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1280, 720)
    # driver = webdriver.Chrome()

    driver.set_page_load_timeout(10)

    # ページを開く
    driver.get(url)

    # JavaScriptを実行してページのタイトルを取得
    m3u8 = driver.execute_script("return window.source1280;")
    print(f"m3u8: {m3u8}")

    # ブラウザを閉じる
    driver.quit()

    return m3u8


def dumpAvList(avList: list):
    avList_json = json.dumps(
        [av.to_dict() for av in avList], ensure_ascii=False, indent=4
    )
    print(avList_json)


def dumpAvListToFile(avList: list):
    with open("data.json", "w") as f:
        avList_json = json.dump(
            [av.to_dict() for av in avList], f, ensure_ascii=False, indent=4
        )
