"""Semantic Scholar 批量 API：第二层摘要兜底（主要针对 Elsevier 期刊）。"""
import time

import requests

API = "https://api.semanticscholar.org/graph/v1/paper/batch"
BATCH = 100


def fetch_abstracts(dois: list[str]) -> dict[str, str]:
    """返回 {doi: abstract}，查不到的不在结果里。无 key，限速温和重试。"""
    result = {}
    for i in range(0, len(dois), BATCH):
        batch = dois[i : i + BATCH]
        for attempt in range(3):
            try:
                r = requests.post(
                    API,
                    params={"fields": "abstract,externalIds"},
                    json={"ids": [f"DOI:{d}" for d in batch]},
                    timeout=60,
                )
                if r.status_code == 429:
                    time.sleep(10 * (attempt + 1))
                    continue
                r.raise_for_status()
                for paper in r.json():
                    if not paper:
                        continue
                    doi = (paper.get("externalIds") or {}).get("DOI", "").lower()
                    if doi and paper.get("abstract"):
                        result[doi] = paper["abstract"].strip()
                break
            except requests.RequestException:
                time.sleep(5)
        time.sleep(1)
    return result
