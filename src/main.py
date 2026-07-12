"""抓取 12 本期刊最新文章并生成 RSS feed 到 public/feeds/。"""
import sys
import time
from pathlib import Path

from config import ARTICLES_PER_JOURNAL, JOURNALS
from crossref import fetch_journal
from feed import build_feed
from page import build_page
import elsevier
import openalex
import semanticscholar

OUT = Path(__file__).resolve().parent.parent / "public" / "feeds"
SITE = "https://SITE_PLACEHOLDER"  # 由 index.html 生成时替换，feed 内只作 channel link


def pick_latest_issue(print_arts: list[dict]):
    """从按 published-print 倒序的列表里选出最新一期。

    常规期刊按 (卷, 期) 分组；Elsevier 等无 issue 字段的按卷分组。
    返回 (label, issue_dois, volume_only, latest_vol)。
    """
    with_issue = [a for a in print_arts if a["volume"] and a["issue"]]
    if with_issue:
        latest = max(with_issue, key=lambda a: a["date"])
        cur = (latest["volume"], latest["issue"])
        dois = {a["doi"] for a in with_issue if (a["volume"], a["issue"]) == cur}
        return f"Vol. {cur[0]}, Issue {cur[1]}", dois, False, cur[0]
    with_vol = [a for a in print_arts if a["volume"]]
    if with_vol:
        latest = max(with_vol, key=lambda a: a["date"])
        vol = latest["volume"]
        dois = {a["doi"] for a in with_vol if a["volume"] == vol}
        return f"Vol. {vol}", dois, True, vol
    return "", set(), False, ""


def split_issue_online(online_arts, print_arts, all_by_doi):
    label, issue_dois, volume_only, latest_vol = pick_latest_issue(print_arts)
    issue_articles = [all_by_doi[d] for d in issue_dois]
    issue_articles.sort(key=lambda a: a["date"], reverse=True)

    online = []
    for a in online_arts:
        if a["doi"] in issue_dois or a["issue"]:
            continue  # 已在最新一期，或属于更早的正式期
        if volume_only and a["volume"]:
            # Elsevier：卷号 <= 最新卷的是旧文章，> 最新卷的是待刊（算 online）
            try:
                if int(a["volume"]) <= int(latest_vol):
                    continue
            except ValueError:
                pass
        online.append(all_by_doi[a["doi"]])
    return label, issue_articles, online


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_articles = []
    doi_to_journal = {}
    page_results = {}
    failed = []

    for code, meta in JOURNALS.items():
        try:
            # 两次查询：online 序抓 Online First，print 序抓最新正式期
            online_arts = fetch_journal(
                meta["issns"], ARTICLES_PER_JOURNAL, sort="published-online"
            )
            time.sleep(1)
            print_arts = fetch_journal(
                meta["issns"], ARTICLES_PER_JOURNAL, sort="published-print"
            )
        except Exception as e:
            print(f"[FAIL] {code}: {e}", file=sys.stderr)
            failed.append(code)
            continue

        # 合并去重（同一 DOI 保留一个对象，摘要补齐对两组同时生效）
        by_doi = {}
        for a in online_arts + print_arts:
            by_doi.setdefault(a["doi"], a)
        articles = sorted(by_doi.values(), key=lambda a: a["date"], reverse=True)

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

        label, issue_articles, online = split_issue_online(
            online_arts, print_arts, by_doi
        )
        page_results[code] = {
            "issue_label": label,
            "issue_articles": issue_articles,
            "online_articles": online,
        }

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

    # 生成首页
    index = OUT.parent / "index.html"
    index.write_text(build_page(JOURNALS, page_results), encoding="utf-8")
    print("[OK] index.html")

    if failed:
        print(f"Failed journals: {failed}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
