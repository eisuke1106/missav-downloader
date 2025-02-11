import requests

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15"
MISSAV_REFERER = "https://missav.ws/"

session = requests.Session()


def requestHttp(path: str) -> str:
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": MISSAV_REFERER,
    }
    response = session.get(path, headers=headers)
    print(f"GET:{path} - {response.status_code}")
    if response.status_code == 200:
        return response.text
    return None
