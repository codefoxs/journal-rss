"""生成 GitHub Pages 首页：按期刊分组展示文章，区分最新一期 / Online First。"""
from datetime import datetime, timezone
from xml.sax.saxutils import escape

CSS = """
:root { --fg:#1c1c1c; --bg:#fff; --muted:#6b6b6b; --line:#e4e4e4; --card:#fafafa;
        --accent:#0b5cad; --chip:#eef4fb; }
@media (prefers-color-scheme: dark) {
  :root { --fg:#e2e2e2; --bg:#151515; --muted:#9a9a9a; --line:#333; --card:#1e1e1e;
          --accent:#7ab8ff; --chip:#1d2a3a; }
}
* { box-sizing: border-box; }
body { font-family: system-ui, "Segoe UI", sans-serif; margin: 0 auto; padding: 2rem 1.2rem 4rem;
       max-width: 880px; line-height: 1.55; color: var(--fg); background: var(--bg); }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { font-size: 1.55rem; margin: 0 0 .3rem; }
.meta { color: var(--muted); font-size: .88rem; margin: 0 0 1.2rem; }
nav { display: flex; flex-wrap: wrap; gap: .45rem; margin-bottom: 2rem; }
nav a { background: var(--chip); padding: .22rem .65rem; border-radius: 99px;
        font-size: .85rem; font-weight: 600; }
section { margin-bottom: 2.6rem; }
h2 { font-size: 1.18rem; border-bottom: 2px solid var(--line); padding-bottom: .35rem;
     margin: 0 0 .2rem; display: flex; align-items: baseline; gap: .6rem; flex-wrap: wrap; }
h2 .code { color: var(--muted); font-size: .8rem; font-weight: 500; }
h2 .rss { margin-left: auto; font-size: .78rem; font-weight: 600;
          border: 1px solid var(--accent); border-radius: 5px; padding: .05rem .45rem; }
h3 { font-size: .92rem; color: var(--muted); text-transform: uppercase;
     letter-spacing: .04em; margin: 1.2rem 0 .5rem; }
details { background: var(--card); border: 1px solid var(--line); border-radius: 8px;
          margin-bottom: .5rem; padding: .55rem .8rem; }
summary { cursor: pointer; list-style: none; display: flex; align-items: center; gap: .8rem; }
summary::-webkit-details-marker { display: none; }
summary .left { flex: 1; min-width: 0; }
summary .t { font-weight: 600; }
summary .a { color: var(--muted); font-size: .84rem; margin-top: .12rem; }
.btn { flex-shrink: 0; border: 1px solid var(--accent); border-radius: 6px;
       padding: .18rem .6rem; font-size: .78rem; font-weight: 600; color: var(--accent);
       white-space: nowrap; user-select: none; }
.btn:hover { background: var(--chip); }
.btn::before { content: "摘要 ▾"; }
details[open] .btn::before { content: "收起 ▴"; }
details .abs { margin: .6rem 0 .2rem; font-size: .9rem; color: var(--fg); }
details .abs b { color: var(--muted); }
.empty { color: var(--muted); font-size: .88rem; font-style: italic; }
footer { color: var(--muted); font-size: .8rem; margin-top: 3rem;
         border-top: 1px solid var(--line); padding-top: 1rem; }
"""


def _fmt_date(date: tuple) -> str:
    y, m, d = date
    return f"{y}-{m:02d}-{d:02d}"


def _article_html(a: dict) -> str:
    authors = escape(", ".join(a["authors"]) or "N/A")
    abstract = (
        f'<p class="abs"><b>Abstract</b> — {escape(a["abstract"])}</p>'
        if a["abstract"]
        else '<p class="abs empty">暂无摘要</p>'
    )
    return f"""<details>
<summary><div class="left"><div class="t"><a href="{escape(a['url'])}" target="_blank" rel="noopener" onclick="event.stopPropagation()">{escape(a['title'])}</a></div>
<div class="a">{authors} · {_fmt_date(a['date'])}</div></div><span class="btn" role="button" aria-label="展开/收起摘要"></span></summary>
{abstract}
</details>"""


def _group_html(title: str, articles: list[dict]) -> str:
    if not articles:
        return f"<h3>{escape(title)}</h3>\n<p class='empty'>暂无</p>"
    items = "\n".join(_article_html(a) for a in articles)
    return f"<h3>{escape(title)} · {len(articles)} 篇</h3>\n{items}"


def build_page(journals: dict, results: dict) -> str:
    """results: code -> {"issue_label", "issue_articles", "online_articles"}"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    nav = "\n".join(
        f'<a href="#{code}">{escape(code.upper())}</a>'
        for code in journals if code in results
    )
    sections = []
    for code, meta in journals.items():
        r = results.get(code)
        if r is None:
            continue
        issue_title = (
            f"最新一期 · {r['issue_label']}" if r["issue_label"] else "最新一期"
        )
        sections.append(f"""<section id="{code}">
<h2><a href="{escape(meta['homepage'])}" target="_blank" rel="noopener">{escape(meta['name'])}</a>
<span class="code">{code.upper()}</span>
<a class="rss" href="feeds/{code}.xml">RSS</a></h2>
{_group_html(issue_title, r['issue_articles'])}
{_group_html('Online First', r['online_articles'])}
</section>""")
    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>顶刊速递 · Finance &amp; Accounting</title>
<style>{CSS}</style>
</head>
<body>
<h1>📚 顶刊速递</h1>
<p class="meta">12 本金融/会计/经济顶刊 · 每周一自动更新 · 更新于 {now} ·
<a href="feeds/all.xml">合并 RSS</a></p>
<nav>{nav}</nav>
{body}
<footer>数据来源：Crossref · OpenAlex · Semantic Scholar · 点击文章标题跳转原文，点击卡片展开摘要。<br>
RSS 订阅：合并源 <code>feeds/all.xml</code>，单刊源 <code>feeds/&lt;code&gt;.xml</code>。</footer>
</body>
</html>
"""
