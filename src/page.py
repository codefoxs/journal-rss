"""生成 GitHub Pages 首页：按期刊分组展示文章，区分最新一期 / Online First。

每刊有专属颜色（明/暗两套，已通过 dataviz 校验：亮度带、彩度下限、
表面对比度全过；CVD 分离度在 8–12 色允许区间内，且颜色恒与文字标签共现）。
桌面端文章卡片三列网格，移动端单列。
"""
from datetime import datetime, timezone
from xml.sax.saxutils import escape

# code -> (light, dark)
COLORS = {
    "nber": ("#a21caf", "#c04ad4"),
    "arn": ("#6a7d0a", "#7f9210"),
    "cgn": ("#00876f", "#14a396"),
    "fen": ("#178a3e", "#2fae55"),
    "aer": ("#256abf", "#3987e5"),
    "jf": ("#4a3aa7", "#6b53c8"),
    "jfe": ("#bf4e1e", "#d95926"),
    "jfqa": ("#0e7a55", "#199e70"),
    "rf": ("#9a6a00", "#c98500"),
    "rfs": ("#006300", "#008300"),
    "jae": ("#c22f2e", "#e66767"),
    "tar": ("#b1356b", "#d55181"),
    "jar": ("#0891b2", "#1499bd"),
    "rast": ("#6d28d9", "#8b5cf6"),
    "ms": ("#9c5514", "#b06a24"),
    "car": ("#d13b6a", "#d94f74"),
}

CSS = """
:root { --fg:#1c1c1c; --bg:#fff; --muted:#6b6b6b; --line:#e4e4e4; --card:#fafafa;
        --accent:#0b5cad; --chip:#eef4fb; --jc:var(--accent); }
@media (prefers-color-scheme: dark) {
  :root { --fg:#e2e2e2; --bg:#151515; --muted:#9a9a9a; --line:#333; --card:#1e1e1e;
          --accent:#7ab8ff; --chip:#1d2a3a; }
}
JOURNAL_COLORS
* { box-sizing: border-box; }
body { font-family: system-ui, "Segoe UI", sans-serif; margin: 0 auto; padding: 2rem 1.2rem 4rem;
       max-width: 1380px; line-height: 1.55; color: var(--fg); background: var(--bg); }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { font-size: 1.55rem; margin: 0 0 .3rem; }
.meta { color: var(--muted); font-size: .88rem; margin: 0 0 1.2rem; }
nav { display: flex; flex-wrap: wrap; gap: .45rem; margin-bottom: 2rem; }
nav a { color: var(--jc); background: var(--chip);
        background: color-mix(in srgb, var(--jc) 12%, transparent);
        padding: .22rem .65rem; border-radius: 99px; font-size: .85rem; font-weight: 600; }
section { margin-bottom: 2.6rem; }
h2 { font-size: 1.18rem; border-bottom: 2px solid var(--jc); padding-bottom: .35rem;
     margin: 0 0 .2rem; display: flex; align-items: baseline; gap: .6rem; flex-wrap: wrap; }
h2 > a { color: var(--jc); }
h2 .code { color: var(--muted); font-size: .8rem; font-weight: 500; }
h2 .rss { margin-left: auto; font-size: .78rem; font-weight: 600; color: var(--jc);
          border: 1px solid var(--jc); border-radius: 5px; padding: .05rem .45rem; }
h3 { font-size: .92rem; color: var(--muted); text-transform: uppercase;
     letter-spacing: .04em; margin: 1.2rem 0 .5rem; }
.cards { display: grid; grid-template-columns: 1fr; gap: .55rem; align-items: start; }
@media (min-width: 720px)  { .cards { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1100px) { .cards { grid-template-columns: repeat(3, 1fr); } }
details { background: var(--card); border: 1px solid var(--line);
          border-left: 3px solid var(--jc); border-radius: 8px; padding: .55rem .8rem;
          min-width: 0; }
summary { cursor: pointer; list-style: none; display: flex; align-items: center; gap: .8rem; }
summary::-webkit-details-marker { display: none; }
summary .left { flex: 1; min-width: 0; }
summary .t { font-weight: 600; font-size: .93rem; overflow-wrap: break-word; }
summary .a { color: var(--muted); font-size: .82rem; margin-top: .15rem; }
.jtag { color: var(--jc); background: var(--chip);
        background: color-mix(in srgb, var(--jc) 12%, transparent);
        border-radius: 4px; padding: 0 .35rem; font-size: .74rem; font-weight: 700;
        white-space: nowrap; }
.btn { flex-shrink: 0; border: 1px solid var(--jc); border-radius: 6px;
       padding: .18rem .6rem; font-size: .78rem; font-weight: 600; color: var(--jc);
       white-space: nowrap; user-select: none; }
.btn:hover { background: color-mix(in srgb, var(--jc) 10%, transparent); }
.btn::before { content: "摘要 ▾"; }
details[open] .btn::before { content: "收起 ▴"; }
details .abs { margin: .6rem 0 .2rem; font-size: .9rem; color: var(--fg); }
details .abs b { color: var(--muted); }
.empty { color: var(--muted); font-size: .88rem; font-style: italic; }
footer { color: var(--muted); font-size: .8rem; margin-top: 3rem;
         border-top: 1px solid var(--line); padding-top: 1rem; }
"""


def _journal_colors_css() -> str:
    light = "\n".join(f".j-{c} {{ --jc: {l}; }}" for c, (l, _) in COLORS.items())
    dark = "\n".join(f"  .j-{c} {{ --jc: {d}; }}" for c, (_, d) in COLORS.items())
    return f"{light}\n@media (prefers-color-scheme: dark) {{\n{dark}\n}}"


def _fmt_date(date: tuple) -> str:
    y, m, d = date
    return f"{y}-{m:02d}-{d:02d}"


def _article_html(a: dict, code: str) -> str:
    authors = escape(", ".join(a["authors"]) or "N/A")
    abstract = (
        f'<p class="abs"><b>Abstract</b> — {escape(a["abstract"])}</p>'
        if a["abstract"]
        else '<p class="abs empty">暂无摘要</p>'
    )
    return f"""<details>
<summary><div class="left"><div class="t"><a href="{escape(a['url'])}" target="_blank" rel="noopener" onclick="event.stopPropagation()">{escape(a['title'])}</a></div>
<div class="a">{authors} · {_fmt_date(a['date'])} <span class="jtag">{code.upper()}</span></div></div><span class="btn" role="button" aria-label="展开/收起摘要"></span></summary>
{abstract}
</details>"""


def _group_html(title: str, articles: list[dict], code: str) -> str:
    if not articles:
        return f"<h3>{escape(title)}</h3>\n<p class='empty'>暂无</p>"
    items = "\n".join(_article_html(a, code) for a in articles)
    return f'<h3>{escape(title)} · {len(articles)} 篇</h3>\n<div class="cards">\n{items}\n</div>'


def build_page(journals: dict, results: dict) -> str:
    """results: code -> {"issue_label", "issue_articles", "online_articles"}"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    nav = "\n".join(
        f'<a class="j-{code}" href="#{code}">{escape(code.upper())}</a>'
        for code in journals if code in results
    )
    sections = []
    for code, meta in journals.items():
        r = results.get(code)
        if r is None:
            continue
        if "groups" in r:  # 自定义分组（如 NBER 只有一组 working papers）
            groups = r["groups"]
        else:
            issue_title = (
                f"最新一期 · {r['issue_label']}" if r["issue_label"] else "最新一期"
            )
            groups = [
                (issue_title, r["issue_articles"]),
                ("Online First", r["online_articles"]),
            ]
        groups_html = "\n".join(_group_html(t, arts, code) for t, arts in groups)
        sections.append(f"""<section id="{code}" class="j-{code}">
<h2><a href="{escape(meta['homepage'])}" target="_blank" rel="noopener">{escape(meta['name'])}</a>
<span class="code">{code.upper()}</span>
<a class="rss" href="feeds/{code}.xml">RSS</a></h2>
{groups_html}
</section>""")
    body = "\n".join(sections)
    css = CSS.replace("JOURNAL_COLORS", _journal_colors_css())
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>顶刊速递 · Finance &amp; Accounting</title>
<style>{css}</style>
</head>
<body>
<h1>📚 顶刊速递</h1>
<p class="meta">12 本金融/会计/经济顶刊 + NBER 公司金融 + SSRN 三大网络 · 每周一自动更新 · 更新于 {now} ·
<a href="feeds/all.xml">合并 RSS</a></p>
<nav>{nav}</nav>
{body}
<footer>数据来源：Crossref · OpenAlex · Semantic Scholar · NBER · SSRN · 点击文章标题跳转原文，点击"摘要"按钮展开。<br>
RSS 订阅：合并源 <code>feeds/all.xml</code>，单刊源 <code>feeds/&lt;code&gt;.xml</code>。</footer>
</body>
</html>
"""
