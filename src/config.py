# 期刊配置：代码 -> (全名, ISSN 列表[印刷版+电子版], 主页链接)
JOURNALS = {
    "aer": {
        "name": "American Economic Review",
        "issns": ["0002-8282", "1944-7981"],
        "homepage": "https://www.aeaweb.org/journals/aer",
    },
    "jf": {
        "name": "The Journal of Finance",
        "issns": ["0022-1082", "1540-6261"],
        "homepage": "https://onlinelibrary.wiley.com/journal/15406261",
    },
    "jfe": {
        "name": "Journal of Financial Economics",
        "issns": ["0304-405X", "1879-2774"],
        "homepage": "https://www.sciencedirect.com/journal/journal-of-financial-economics",
    },
    "jfqa": {
        "name": "Journal of Financial and Quantitative Analysis",
        "issns": ["0022-1090", "1756-6916"],
        "homepage": "https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis",
    },
    "rf": {
        "name": "Review of Finance",
        "issns": ["1572-3097", "1573-692X"],
        "homepage": "https://academic.oup.com/rof",
    },
    "rfs": {
        "name": "The Review of Financial Studies",
        "issns": ["0893-9454", "1465-7368"],
        "homepage": "https://academic.oup.com/rfs",
    },
    "jae": {
        "name": "Journal of Accounting and Economics",
        "issns": ["0165-4101", "1879-1980"],
        "homepage": "https://www.sciencedirect.com/journal/journal-of-accounting-and-economics",
    },
    "tar": {
        "name": "The Accounting Review",
        "issns": ["0001-4826", "1558-7967"],
        "homepage": "https://publications.aaahq.org/accounting-review",
    },
    "jar": {
        "name": "Journal of Accounting Research",
        "issns": ["0021-8456", "1475-679X"],
        "homepage": "https://onlinelibrary.wiley.com/journal/1475679x",
    },
    "rast": {
        "name": "Review of Accounting Studies",
        "issns": ["1380-6653", "1573-7136"],
        "homepage": "https://link.springer.com/journal/11142",
    },
    "ms": {
        "name": "Management Science",
        "issns": ["0025-1909", "1526-5501"],
        "homepage": "https://pubsonline.informs.org/journal/mnsc",
    },
    "car": {
        "name": "Contemporary Accounting Research",
        "issns": ["0823-9150", "1911-3846"],
        "homepage": "https://onlinelibrary.wiley.com/journal/19113846",
    },
}

# NBER Corporate Finance 板块（非期刊，走 nber.py 的搜索 API，页面上排在 AER 前面）
NBER = {
    "name": "NBER Working Papers · Corporate Finance",
    "homepage": "https://www.nber.org/papers?page=1&perPage=50&sortBy=public_date"
    "&facet=topics%3ACorporate+Finance",
}

# SSRN 三大网络（走 ssrn.py 的内容 API，页面上排在 NBER 之后、AER 之前）
SSRN = {
    "arn": {
        "name": "SSRN · Accounting Research Network",
        "binding": 204,
        "homepage": "https://www.ssrn.com/index.cfm/en/arn/",
    },
    "cgn": {
        "name": "SSRN · Corporate Governance Network",
        "binding": 1566963,
        "homepage": "https://www.ssrn.com/index.cfm/en/cgn/",
    },
    "fen": {
        "name": "SSRN · Financial Economics Network",
        "binding": 203,
        "homepage": "https://www.ssrn.com/index.cfm/en/fen/",
    },
}

# 联系邮箱：进入 Crossref/OpenAlex 的 polite pool，限速更宽松
MAILTO = "chenzhiwu2023@outlook.com"

# 每刊抓取的最新文章数
ARTICLES_PER_JOURNAL = 40
