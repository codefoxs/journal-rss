"""ScienceDirect 摘要抓取（JFE/JAE 兜底）。

Elsevier 不向 Crossref/OpenAlex 提供摘要，最新文章只能抓官网。
用 curl_cffi 伪装 Chrome TLS 指纹绕过反爬；失败可容忍（摘要留空）。
"""
import html
import re
import time

from curl_cffi import requests as cr

SD_URL = "https://www.sciencedirect.com/science/article/abs/pii/{pii}"
ABSTRACT_RE = re.compile(
    r'<div class="abstract author"[^>]*>.*?</h2>(.*?)</div>\s*</div>', re.S
)
TAG_RE = re.compile(r"<[^>]+>")


def _clean(fragment: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", TAG_RE.sub(" ", fragment))).strip()


def fetch_abstracts(dois: list[str]) -> dict[str, str]:
    """仅处理 Elsevier DOI (10.1016/*)，返回 {doi: abstract}。"""
    targets = [d for d in dois if d.startswith("10.1016/")]
    if not targets:
        return {}
    result = {}
    with cr.Session(impersonate="chrome") as s:
        for doi in targets:
            try:
                # doi.org -> linkinghub.elsevier.com/retrieve/pii/<PII>
                r = s.get(f"https://doi.org/{doi}", timeout=60, allow_redirects=True)
                pii = r.url.rstrip("/").rsplit("/", 1)[-1]
                if not re.fullmatch(r"S?[0-9X]+", pii, re.I):
                    continue
                r2 = s.get(SD_URL.format(pii=pii), timeout=60)
                if r2.status_code != 200:
                    continue
                m = ABSTRACT_RE.search(r2.text)
                if m:
                    text = _clean(m.group(1))
                    if len(text) > 50:
                        result[doi] = text
            except Exception:
                pass
            time.sleep(2)  # 控制频率，避免触发封锁
    return result
