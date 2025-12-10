# config/crawl_config.py
# -*- coding: utf-8 -*-
"""
舆情采集核心配置文件
功能：统一管理行业/企业舆情采集的参数，无需修改核心代码即可调整采集规则
适用：适配core/yuqing_crawl.py中的crawl_industry_yuqing/crawl_enterprise_yuqing函数
"""

# ===================== 基础全局配置 =====================
# Python解释器编码（避免中文乱码）
import sys
sys.setdefaultencoding = lambda x, enc="utf-8": None

TUSHARE_TOKEN="2a81c5e44a8c2e6195c557690878c3c5fa5f2cf30cce8e17c3e6d505"

STOCK_CODE_PREFIX = ""

# 调试模式开关（True：打印采集日志；False：静默采集）
DEBUG_MODE = True

# 采集总开关（False：暂停所有采集，用于维护）
CRAWL_ENABLE = True

# ===================== 采集数量配置 =====================
# 每个关键词组合采集的最大条数（Demo建议5-10，生产环境可设20-50）
CRAWL_ITEM_NUM_PER_COMBINATION = 5

# 采集页数（新浪财经/证券日报每页约20条，建议仅采集第1页，避免反爬）
CRAWL_PAGE_NUM = 1

# 采集总条数上限（防止采集过量导致内存溢出）
CRAWL_TOTAL_LIMIT = 100

# ===================== 防反爬配置（核心） =====================
# 请求头（模拟Chrome浏览器，避免被识别为爬虫）
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://finance.sina.com.cn/",  # 新增：添加来源页，模拟真实访问
    "Cookie": "UOR=www.baidu.com,finance.sina.com.cn,; SINAGLOBAL=1234567890; ULV=1234567890123:1:1:1:1234567890123:;",  # 新增：模拟Cookie（可随便填）
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Connection": "keep-alive"
}

# 请求超时时间（秒）：超过该时间未响应则放弃采集
REQUEST_TIMEOUT = 10

# 关键词间请求间隔（秒）：防止请求过快被封禁（建议1-3秒）
REQUEST_INTERVAL = 1

# 请求失败重试次数：单关键词采集失败后重试次数
REQUEST_RETRY_TIMES = 2

# ===================== 行业舆情专属配置 =====================
# 默认行业事件关键词（采集函数未传入时使用）
INDUSTRY_DEFAULT_EVENT_KEYWORDS = [
    "补贴", "政策", "风险", "逾期", "集采", "营收",
    "价格波动", "装机量", "出口", "审批", "临床试验"
]

# 行业舆情数据源优先级（扩展用，当前仅用新浪财经）
INDUSTRY_DATA_SOURCE = [
    "sina_finance",  # 新浪财经（默认）
    "eastmoney",     # 东方财富网（扩展）
    "stockstar"      # 证券之星（扩展）
]

# ===================== 企业舆情专属配置 =====================
# 默认企业风险关键词（采集函数未传入时使用）
ENTERPRISE_DEFAULT_RISK_KEYWORDS = [
    "债务逾期", "评级下调", "资金链", "集采中标价",
    "营收下滑", "监管", "商票逾期", "土地流拍", "研发失败"
]

# 企业舆情数据源优先级（扩展用，当前仅用证券日报）
ENTERPRISE_DATA_SOURCE = [
    "zqrb",          # 证券日报（默认）
    "qcc",           # 企查查（扩展）
    "tianyancha"     # 天眼查（扩展）
]

# 企业别名映射（扩展用：解决同企业不同名称问题）
ENTERPRISE_ALIAS_MAP = {
    "浦发银行": ["上海浦东发展银行", "浦发"],
    "万科": ["万科企业", "万科集团"],
    "比亚迪": ["比亚迪股份", "BYD"]
}

# ===================== 数据过滤配置 =====================
# 文本长度过滤：过滤过短/无意义文本（字符数）
TEXT_MIN_LENGTH = 10  # 最小文本长度
TEXT_MAX_LENGTH = 500  # 最大文本长度（避免超长广告文本）

# 敏感词过滤：过滤无关/违规内容（采集结果自动剔除包含这些词的舆情）
FILTER_SENSITIVE_WORDS = [
    "违法", "违规", "色情", "暴力", "赌博", "毒品",
    "邪教", "反动", "虚假宣传", "诈骗"
]

# 来源白名单：仅保留这些来源的舆情（保证权威性）
FILTER_SOURCE_WHITELIST = [
    "新浪财经", "证券日报", "上海证券报",
    "中国证券报", "东方财富网", "证券时报"
]

# ===================== 存储配置 =====================
# 原始舆情数据存储表名（SQLite）
TABLE_NAME_RAW = "opinion_raw"

# 清洗后舆情数据存储表名（SQLite）
TABLE_NAME_CLEAN = "opinion_clean"

# 数据存储格式（扩展用：csv/sqlite/json）
STORAGE_FORMAT = "sqlite"

# SQLite数据库文件路径（项目根目录下的data文件夹）
SQLITE_DB_PATH = "./data/opinion_demo.db"

# ===================== 扩展配置（可选） =====================
# 时间范围过滤：仅采集指定时间段内的舆情（格式：YYYY-MM-DD）
# 若为None则采集所有时间
CRAWL_TIME_START = None
CRAWL_TIME_END = None

# 是否开启增量采集（True：仅采集新增舆情，需配合时间戳）
INCREMENTAL_CRAWL = False