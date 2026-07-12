# journal-rss

12 本金融/会计/经济顶刊（AER, JF, JFE, JFQA, RF, RFS, JAE, TAR, JAR, RAST, MS, CAR）的
最新一期 + Online First 文章 RSS 订阅源。

- 元数据来源：[Crossref API](https://api.crossref.org)（标题、作者、日期、DOI 链接、部分摘要）
- 摘要补充：[OpenAlex API](https://openalex.org)（覆盖 Cloudflare 保护的 TAR/MS 等站点，无需抓官网）
- 每天由 GitHub Actions 定时构建，发布到 GitHub Pages

## 本地运行

```bash
pip install -r requirements.txt
python src/main.py   # 输出到 public/feeds/*.xml
```

## 订阅

访问 GitHub Pages 首页查看所有 feed 链接，或直接订阅
`https://<user>.github.io/journal-rss/feeds/all.xml`（合并源）
或 `feeds/<期刊代码>.xml`（单刊源）。
