# journal-rss

<img src="public/FOX.png" width="96" align="right" alt="logo">

金融/会计/经济学术前沿追踪：12 本顶刊 + NBER 公司金融 + SSRN 三大网络，
自动生成 RSS 订阅源和网页速递，每周一更新。

**在线访问**：<https://codefoxs.github.io/journal-rss/>

## 覆盖范围

| 板块 | 内容 |
|---|---|
| 12 本顶刊 | AER, JF, JFE, JFQA, RF, RFS, JAE, TAR, JAR, RAST, MS, CAR（最新一期 + Online First） |
| NBER | Corporate Finance 最新 50 篇工作论文 |
| SSRN | ARN（会计）/ CGN（公司治理）/ FEN（金融经济学）各 50 篇最新工作论文 |

## 数据来源

- 期刊元数据：[Crossref API](https://api.crossref.org)（标题、作者、日期、DOI、部分摘要）
- NBER：官方搜索 API；SSRN：官方内容 API
- 摘要多级补齐：Crossref →（NBER/SSRN 走 DOI 批量）→ [OpenAlex](https://openalex.org) → [Semantic Scholar](https://www.semanticscholar.org) → ScienceDirect / SSRN 页面兜底；
  SSRN 最新论文因 Crossref 注册滞后约一半暂无摘要，页面显示"获取失败，请前往主页查看"
- 每周一由 GitHub Actions 定时构建（UTC 02:30，北京时间 10:30），发布到 GitHub Pages

## 页面特性

- 按板块分组展示，每板块专属配色（明/暗双主题，已通过色觉友好校验）
- 桌面端三列卡片，点击"摘要"按钮展开/收起
- 期刊区分"最新一期 / Online First"，工作论文按批准日期倒序

## 本地运行

```bash
pip install -r requirements.txt
python src/main.py   # 输出到 public/feeds/*.xml 和 public/index.html
```

## 订阅

- 合并源（全部板块按日期倒序，前 200 篇）：`https://codefoxs.github.io/journal-rss/feeds/all.xml`
- 单板块源：`feeds/<代码>.xml`，如 `feeds/jf.xml`、`feeds/nber.xml`、`feeds/fen.xml`
