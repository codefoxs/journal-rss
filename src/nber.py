"""NBER 工作论文（Corporate Finance 板块）：官方搜索 API，最新 50 篇。

列表返回的摘要是截断的，先留空让 OpenAlex/S2 按 DOI (10.3386/wNNNNN)
补全文摘要，补不到的再用截断版兜底（见 main.py）。
"""
import re
import time
from datetime import datetime

import requests

API = "https://www.nber.org/api/v1/working_page_listing/contentType/working_paper/_/_/search"
TAG_RE = re.compile(r"<[^>]+>")


def fetch_corporate_finance(rows: int = 50) -> list[dict]:
    params = {
        "page": 1,
        "perPage": rows,
        "sortBy": "public_date",
        "facet": "topics:Corporate Finance",
    }
    for attempt in range(3):
        try:
            r = requests.get(
                API, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=60
            )
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))

    articles = []
    for res in r.json()["results"]:
        if res.get("type") != "working_paper" or not res.get("url"):
            continue
        wid = res["url"].rstrip("/").rsplit("/", 1)[-1]  # w35385
        if not re.fullmatch(r"w\d+", wid):
            continue
        try:
            dt = datetime.strptime(res.get("displaydate", ""), "%B %Y")
            date = (dt.year, dt.month, 1)
        except ValueError:
            continue
        teaser = (res.get("abstract") or "").strip()
        articles.append(
            {
                "doi": f"10.3386/{wid}",
                "title": TAG_RE.sub("", res.get("title", "")).strip(),
                "authors": [TAG_RE.sub("", a).strip() for a in res.get("authors", [])],
                "date": date,
                "url": f"https://www.nber.org{res['url']}",
                "abstract": "",  # 先留空，交给 OpenAlex/S2 补全文
                "teaser": teaser,  # API 返回的截断摘要，兜底用
                "volume": "",
                "issue": "",
            }
        )
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles
