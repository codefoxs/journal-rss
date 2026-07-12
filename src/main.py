"""抓取 12 本期刊最新文章并生成 RSS feed 到 public/feeds/。"""
import sys
import time
from pathlib import Path

from config import ARTICLES_PER_JOURNAL, JOURNALS
from crossref import fetch_journal
from feed import build_feed
import elsevier
import openalex
import semanticscholar

OUT = Path(__file__).resolve().parent.parent / "public" / "feeds"
SITE = "https://SITE_PLACEHOLDER"  # 由 index.html 生成时替换，feed 内只作 channel link


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_articles = []
    doi_to_journal = {}
    failed = []

    for code, meta in JOURNALS.items():
        try:
            articles = fetch_journal(meta["issns"], ARTICLES_PER_JOURNAL)
        except Exception as e:
            print(f"[FAIL] {code}: {e}", file=sys.stderr)
            failed.append(code)
            continue

        # 摘要兜底：OpenAlex -> Semantic Scholar
        for source in (openalex, semanticscholar, elsevier):
            missing = [a["doi"] for a in articles if not a["abstract"]]
            if not missing:
                break
            found = source.fetch_abstracts(missing)
            for a in articles:
                if not a["abstract"] and a["doi"] in found:
                    a["abstract"] = found[a["doi"]]

        n_abs = sum(1 for a in articles if a["abstract"])
        print(f"[OK] {code}: {len(articles)} articles, {n_abs} with abstract")

        xml = build_feed(
            title=meta["name"],
            link=meta["homepage"],
            description=f"Latest articles from {meta['name']} (issues + online first)",
            articles=articles,
        )
        (OUT / f"{code}.xml").write_text(xml, encoding="utf-8")

        for a in articles:
            doi_to_journal[a["doi"]] = meta["name"]
        all_articles.extend(articles)
        time.sleep(1)  # 对 Crossref 客气一点

    # 合并 feed：全部期刊按日期倒序，取前 200
    all_articles.sort(key=lambda a: a["date"], reverse=True)
    xml = build_feed(
        title="Top Finance & Accounting Journals",
        link=SITE,
        description="Combined feed: AER, JF, JFE, JFQA, RF, RFS, JAE, TAR, JAR, RAST, MS, CAR",
        articles=all_articles[:200],
        journal_name_of=lambda a: doi_to_journal[a["doi"]],
    )
    (OUT / "all.xml").write_text(xml, encoding="utf-8")
    print(f"[OK] all.xml: {min(len(all_articles), 200)} articles")

    if failed:
        print(f"Failed journals: {failed}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
