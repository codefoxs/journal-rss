"""OpenAlex API：为 Crossref 缺摘要的文章批量补摘要（免抓 Cloudflare 官网）。"""
import time

import requests

from config import MAILTO

API = "https://api.openalex.org/works"
HEADERS = {"User-Agent": f"journal-rss/1.0 (mailto:{MAILTO})"}
BATCH = 50  # OpenAlex OR 过滤上限


def _rebuild(inverted: dict) -> str:
    """OpenAlex 摘要是倒排索引，重建为原文。"""
    positions = []
    for word, idxs in inverted.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def fetch_abstracts(dois: list[str]) -> dict[str, str]:
    """返回 {doi: abstract}，查不到的不在结果里。"""
    result = {}
    for i in range(0, len(dois), BATCH):
        batch = dois[i : i + BATCH]
        params = {
            "filter": "doi:" + "|".join(batch),
            "select": "doi,abstract_inverted_index",
            "per-page": BATCH,
            "mailto": MAILTO,
        }
        try:
            r = requests.get(API, params=params, headers=HEADERS, timeout=60)
            r.raise_for_status()
        except requests.RequestException:
            continue  # 摘要缺失可容忍，不中断整体流程
        for w in r.json().get("results", []):
            inv = w.get("abstract_inverted_index")
            doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
            if inv and doi:
                result[doi] = _rebuild(inv)
        time.sleep(0.2)
    return result
