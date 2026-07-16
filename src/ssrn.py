"""SSRN 三大网络（ARN/CGN/FEN）：内容 API 取最新 50 篇。

api.ssrn.com 在 Cloudflare 后面，但 curl_cffi 伪装 Chrome 可过；
papers.ssrn.com 论文页是 JS 质询，部分出口 IP 会被拦，抓摘要
采取尽力而为策略（连续失败即放弃），缺的交给 OpenAlex/S2。
DOI 规则：10.2139/ssrn.{abstract_id}。
"""
import html
import re
import time
from datetime import datetime

from curl_cffi import requests

API = "https://api.ssrn.com/content/v1/bindings/{binding}/papers"
TAG_RE = re.compile(r"<[^>]+>")
ABS_RE = re.compile(
    r'<div class="abstract-text">.*?<p>(.*?)</div>', re.S
)
META_RE = re.compile(r'<meta name="description" content="([^"]+)"')


def fetch_network(binding: int, rows: int = 50) -> list[dict]:
    params = {"index": 0, "count": rows, "sort": 0}
    for attempt in range(3):
        try:
            r = requests.get(
                API.format(binding=binding), params=params,
                headers={"Accept": "application/json"},
                impersonate="chrome", timeout=60,
            )
            r.raise_for_status()
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))

    articles = []
    for p in r.json()["papers"]:
        aid = p.get("id")
        if not aid:
            continue
        try:
            dt = datetime.strptime(p.get("approved_date", ""), "%d %b %Y")
            date = (dt.year, dt.month, dt.day)
        except ValueError:
            continue
        title = html.unescape(TAG_RE.sub("", p.get("title", ""))).strip()
        authors = [
            f"{a.get('first_name', '')} {a.get('last_name', '')}".strip()
            for a in p.get("authors", [])
        ]
        articles.append(
            {
                "doi": f"10.2139/ssrn.{aid}",
                "title": title,
                "authors": [a for a in authors if a],
                "date": date,
                "url": p.get("url")
                or f"https://papers.ssrn.com/sol3/papers.cfm?abstract_id={aid}",
                "abstract": "",
                "volume": "",
                "issue": "",
            }
        )
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


def fetch_abstracts(dois: list[str]) -> dict[str, str]:
    """尽力从 papers.ssrn.com 论文页抓摘要；连续 3 次失败即放弃。"""
    found = {}
    fails = 0
    session = requests.Session(impersonate="chrome")
    for doi in dois:
        m = re.fullmatch(r"10\.2139/ssrn\.(\d+)", doi)
        if not m:
            continue
        url = f"https://papers.ssrn.com/sol3/papers.cfm?abstract_id={m.group(1)}"
        try:
            r = session.get(url, timeout=30)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}")
            text = None
            am = ABS_RE.search(r.text)
            if am:
                text = html.unescape(TAG_RE.sub(" ", am.group(1)))
            else:
                mm = META_RE.search(r.text)
                if mm:
                    text = html.unescape(mm.group(1))
            if text:
                text = re.sub(r"\s+", " ", text).strip()
                if len(text) > 50:
                    found[doi] = text
            fails = 0
        except Exception:
            fails += 1
            if fails >= 3:
                break  # 该出口 IP 被质询拦截，全部放弃
        time.sleep(2)
    return found
