"""Crossref API 数据源：按 ISSN 拉取期刊最新文章（含 online first）。"""
import html
import re
import time

import requests

from config import MAILTO

API = "https://api.crossref.org/works"
HEADERS = {"User-Agent": f"journal-rss/1.0 (mailto:{MAILTO})"}

# 排除勘误、社论等非正式文章
EXCLUDE_TITLE = re.compile(
    r"^(erratum|corrigendum|correction|retraction|editorial board|"
    r"issue information|front matter|back matter|masthead|"
    r"announcement|miscellanea|forthcoming papers)",
    re.I,
)


def _strip_jats(text: str) -> str:
    """去掉 Crossref 摘要里的 JATS XML 标签。"""
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def _date_parts(item: dict):
    """取最早的发表日期（online 优先），返回 (y, m, d)。"""
    for key in ("published", "published-online", "published-print", "created"):
        parts = item.get(key, {}).get("date-parts", [[None]])[0]
        if parts and parts[0]:
            y = parts[0]
            m = parts[1] if len(parts) > 1 else 1
            d = parts[2] if len(parts) > 2 else 1
            return y, m, d
    return None


def _authors(item: dict) -> list[str]:
    out = []
    for a in item.get("author", []):
        name = " ".join(x for x in (a.get("given"), a.get("family")) if x)
        if not name:
            name = a.get("name", "")
        if name:
            out.append(name)
    return out


def fetch_journal(issns: list[str], rows: int = 40) -> list[dict]:
    """返回按发表日期倒序的文章列表。"""
    filters = ",".join(f"issn:{i}" for i in issns) + ",type:journal-article"
    params = {
        "filter": filters,
        "sort": "published",
        "order": "desc",
        "rows": rows,
        "select": "DOI,title,author,abstract,published,published-online,"
        "published-print,created,volume,issue,URL,container-title",
        "mailto": MAILTO,
    }
    for attempt in range(3):
        try:
            r = requests.get(API, params=params, headers=HEADERS, timeout=60)
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))

    articles = []
    for item in r.json()["message"]["items"]:
        title_list = item.get("title") or []
        title = _strip_jats(title_list[0]) if title_list else ""
        if not title or EXCLUDE_TITLE.match(title):
            continue
        date = _date_parts(item)
        if not date:
            continue
        abstract = item.get("abstract", "")
        articles.append(
            {
                "doi": item["DOI"].lower(),
                "title": title,
                "authors": _authors(item),
                "date": date,  # (y, m, d)
                "url": f"https://doi.org/{item['DOI']}",
                "abstract": _strip_jats(abstract) if abstract else "",
                "volume": item.get("volume", ""),
                "issue": item.get("issue", ""),
            }
        )
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles
