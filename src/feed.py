"""生成 RSS 2.0 XML。"""
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape


def _rfc822(date: tuple) -> str:
    y, m, d = date
    return format_datetime(datetime(y, m, d, 12, 0, tzinfo=timezone.utc))


def _item_xml(a: dict, journal_name: str) -> str:
    authors = ", ".join(a["authors"]) or "N/A"
    desc_parts = [f"<b>Authors:</b> {escape(authors)}"]
    if a.get("volume"):
        vi = f"Vol. {a['volume']}" + (f", Issue {a['issue']}" if a.get("issue") else "")
        desc_parts.append(f"<b>{escape(vi)}</b>")
    if a.get("abstract"):
        desc_parts.append(f"<b>Abstract:</b> {escape(a['abstract'])}")
    else:
        desc_parts.append("<i>(No abstract available)</i>")
    description = "<br/><br/>".join(desc_parts).replace("]]>", "]]&gt;")
    return f"""    <item>
      <title>{escape(a['title'])}</title>
      <link>{escape(a['url'])}</link>
      <guid isPermaLink="false">{escape(a['doi'])}</guid>
      <pubDate>{_rfc822(a['date'])}</pubDate>
      <dc:creator>{escape(authors)}</dc:creator>
      <category>{escape(journal_name)}</category>
      <description><![CDATA[{description}]]></description>
    </item>"""


def build_feed(title: str, link: str, description: str, articles: list[dict],
               journal_name_of=None) -> str:
    """articles 已按日期倒序；journal_name_of(a) 用于合并 feed 标注来源期刊。"""
    now = format_datetime(datetime.now(timezone.utc))
    items = []
    for a in articles:
        jname = journal_name_of(a) if journal_name_of else title
        items.append(_item_xml(a, jname))
    items_xml = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(title)}</title>
    <link>{escape(link)}</link>
    <description>{escape(description)}</description>
    <language>en</language>
    <lastBuildDate>{now}</lastBuildDate>
    <generator>journal-rss</generator>
{items_xml}
  </channel>
</rss>
"""
