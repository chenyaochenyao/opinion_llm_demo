import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from urllib.parse import quote
import logging
import nest_asyncio
from typing import List, Dict, Set
import json
import pickle

# 应用nest_asyncio以解决异步环境问题
nest_asyncio.apply()

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class FastNewEnergyCrawler:
    def __init__(self):
        self.industry = "新能源"
        self.keywords = ["补贴", "政策", "营收", "价格", "风险"]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        # 搜索引擎配置
        self.search_engines = [
            {
                'name': '百度新闻',
                'base_url': 'https://news.baidu.com/ns?word={}&pn={}&cl=2&ct=0&tn=news&rn=50&ie=utf-8',
                'parser': self.parse_baidu_news,
                'pages_per_keyword': 2,
                'results_per_page': 50
            },
            {
                'name': '搜狗新闻',
                'base_url': 'https://news.sogou.com/news?query={}&page={}',
                'parser': self.parse_sogou_news,
                'pages_per_keyword': 2,
                'results_per_page': 20
            }
        ]

        # 新闻API备用方案
        self.news_apis = [
            {
                'name': '聚合数据',
                'url': 'https://v.juhe.cn/toutiao/index',
                'params': {'type': 'keji', 'key': 'YOUR_API_KEY'},  # 需要申请API key
                'enabled': False
            }
        ]

        # 缓存已爬取的URL，避免重复
        self.visited_urls = set()
        self.cache_file = 'news_cache.pkl'
        self.load_cache()

    def load_cache(self):
        """加载缓存"""
        try:
            with open(self.cache_file, 'rb') as f:
                self.visited_urls = pickle.load(f)
            logger.info(f"已加载 {len(self.visited_urls)} 个缓存URL")
        except FileNotFoundError:
            self.visited_urls = set()

    def save_cache(self):
        """保存缓存"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.visited_urls, f)
        logger.info(f"已缓存 {len(self.visited_urls)} 个URL")

    async def fetch_url(self, session: aiohttp.ClientSession, url: str, timeout: int = 8):
        """异步获取URL内容"""
        try:
            async with session.get(url, headers=self.headers, timeout=timeout) as response:
                if response.status == 200:
                    text = await response.text()
                    return text
                else:
                    logger.warning(f"请求失败: {url}, 状态码: {response.status}")
                    return None
        except Exception as e:
            logger.warning(f"请求异常 {url}: {str(e)}")
            return None

    async def search_keyword_concurrently(self, keyword: str, engine: dict):
        """并发搜索一个关键词"""
        all_news = []
        tasks = []

        async with aiohttp.ClientSession() as session:
            # 为每个页面创建任务
            for page in range(engine['pages_per_keyword']):
                start = page * engine['results_per_page']
                url = engine['base_url'].format(
                    quote(f"{self.industry} {keyword}"),
                    start if engine['name'] == '百度新闻' else page + 1
                )
                tasks.append(self.fetch_search_page(session, url, keyword, engine))

            # 并发执行所有任务
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 收集结果
            for result in results:
                if isinstance(result, list):
                    all_news.extend(result)

        return all_news

    async def fetch_search_page(self, session: aiohttp.ClientSession, url: str, keyword: str, engine: dict):
        """获取单个搜索结果页"""
        logger.info(f"获取页面: {url}")
        html = await self.fetch_url(session, url)

        if html:
            soup = BeautifulSoup(html, 'html.parser')
            news_items = engine['parser'](soup, keyword)

            # 并发获取新闻详情
            if news_items:
                # 创建详情获取任务
                detail_tasks = []
                for item in news_items:
                    if item.get('原文链接') and item['原文链接'] not in self.visited_urls:
                        detail_tasks.append(
                            self.fetch_news_detail(session, item['原文链接'], item)
                        )
                        self.visited_urls.add(item['原文链接'])

                # 并发获取详情
                if detail_tasks:
                    detailed_items = await asyncio.gather(*detail_tasks, return_exceptions=True)
                    # 过滤有效结果
                    valid_items = [item for item in detailed_items
                                   if isinstance(item, dict) and item.get('新闻标题')]
                    return valid_items

            return news_items
        return []

    async def fetch_news_detail(self, session: aiohttp.ClientSession, url: str, base_item: dict):
        """异步获取新闻详情"""
        try:
            html = await self.fetch_url(session, url, timeout=5)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # 快速内容提取策略
                content = self.extract_content_fast(soup)

                # 更新时间戳
                base_item['正文/摘要'] = content[:300] if content else base_item.get('正文/摘要', '')
                base_item['采集时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                return base_item
        except Exception as e:
            logger.warning(f"获取详情失败 {url}: {str(e)}")

        return base_item

    def extract_content_fast(self, soup: BeautifulSoup) -> str:
        """快速内容提取策略"""
        # 常见新闻网站的内容标签
        content_patterns = [
            ('div', {'class': ['article-content', 'content', 'article-body']}),
            ('article', {}),
            ('div', {'id': ['artibody', 'content', 'article']}),
            ('div', {'class': 'main-content'}),
        ]

        for tag, attrs in content_patterns:
            element = soup.find(tag, attrs)
            if element:
                # 快速清理
                for script in element.find_all(['script', 'style', 'iframe']):
                    script.decompose()

                text = element.get_text(separator='\n', strip=True)
                if len(text) > 100:  # 确保有足够内容
                    return text[:500]  # 限制长度

        # 如果未找到，提取所有段落
        paragraphs = soup.find_all('p')
        if paragraphs:
            texts = [p.get_text().strip() for p in paragraphs[:15] if len(p.get_text().strip()) > 20]
            return '\n'.join(texts)

        return ""

    def parse_baidu_news(self, soup: BeautifulSoup, keyword: str) -> List[Dict]:
        """解析百度新闻（优化版）"""
        news_list = []

        # 百度新闻搜索结果通常在这个容器中
        results = soup.find_all('div', class_='result')
        if not results:
            results = soup.find_all('div', class_=re.compile(r'c-container'))

        for result in results[:30]:  # 限制处理数量
            try:
                # 快速提取标题和链接
                title_elem = result.find(['h3', 'h2', 'h4'])
                if not title_elem:
                    continue

                link_elem = title_elem.find('a')
                if not link_elem:
                    continue

                title = link_elem.get_text().strip()
                link = link_elem.get('href', '')

                # 快速提取来源和时间
                source_time_elem = result.find('p', class_='c-author') or result.find('div',
                                                                                      class_=re.compile(r'author'))
                source = ""
                pub_time = ""

                if source_time_elem:
                    text = source_time_elem.get_text().strip()
                    # 简单的时间提取
                    time_match = re.search(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?\s*\d{1,2}:\d{2}', text)
                    if time_match:
                        pub_time = time_match.group()
                        source = text.replace(pub_time, '').strip()

                # 提取摘要
                summary_elem = result.find('div', class_='c-summary') or result.find('span',
                                                                                     class_='content-right_8Zs40')
                summary = summary_elem.get_text().strip() if summary_elem else ''

                news_item = {
                    '新闻标题': title,
                    '发布时间': pub_time,
                    '来源': source[:50],
                    '正文/摘要': summary[:200],
                    '所属行业': self.industry,
                    '搜索关键词': keyword,
                    '原文链接': link
                }

                news_list.append(news_item)

            except Exception as e:
                continue

        return news_list

    def parse_sogou_news(self, soup: BeautifulSoup, keyword: str) -> List[Dict]:
        """解析搜狗新闻"""
        news_list = []

        results = soup.find_all('div', class_='vrwrap')
        if not results:
            results = soup.find_all('div', class_=re.compile(r'result'))

        for result in results[:30]:
            try:
                # 标题
                title_elem = result.find('h3')
                if title_elem and title_elem.a:
                    title = title_elem.a.get_text().strip()
                    link = title_elem.a.get('href', '')
                else:
                    continue

                # 来源和时间
                source_info = result.find('div', class_='news-from')
                source = ""
                pub_time = ""

                if source_info:
                    text = source_info.get_text().strip()
                    # 提取时间
                    time_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', text)
                    if time_match:
                        pub_time = time_match.group()
                        source = text.split(pub_time)[0].strip()

                # 摘要
                summary_elem = result.find('div', class_='news-detail')
                summary = summary_elem.get_text().strip() if summary_elem else ''

                news_item = {
                    '新闻标题': title,
                    '发布时间': pub_time,
                    '来源': source[:50],
                    '正文/摘要': summary[:200],
                    '所属行业': self.industry,
                    '搜索关键词': keyword,
                    '原文链接': link
                }

                news_list.append(news_item)

            except Exception as e:
                continue

        return news_list

    async def crawl_all_keywords(self):
        """并发爬取所有关键词"""
        all_tasks = []

        for engine in self.search_engines:
            for keyword in self.keywords:
                task = self.search_keyword_concurrently(keyword, engine)
                all_tasks.append(task)

        # 并发执行所有搜索任务
        results = await asyncio.gather(*all_tasks, return_exceptions=True)

        # 合并结果
        all_news = []
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)

        # 去重
        seen_titles = set()
        unique_news = []

        for item in all_news:
            title = item.get('新闻标题', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)

        return unique_news

    def save_results(self, news_items: List[Dict], filename: str = None):
        """保存结果"""
        if not news_items:
            logger.warning("没有数据可保存")
            return

        df = pd.DataFrame(news_items)

        # 设置文件名
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'新能源新闻_{timestamp}.xlsx'

        # 保存到Excel
        df.to_excel(filename, index=False, encoding='utf-8-sig')

        # 同时保存JSON格式（便于后续处理）
        json_file = filename.replace('.xlsx', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(news_items, f, ensure_ascii=False, indent=2)

        logger.info(f"已保存 {len(news_items)} 条新闻到 {filename}")
        return df


async def main():
    """主函数"""
    print("=" * 60)
    print("高速新能源新闻爬虫 v2.0")
    print("使用异步并发技术，大幅提升爬取速度")
    print("=" * 60)

    crawler = FastNewEnergyCrawler()

    try:
        # 开始并发爬取
        print(f"开始并发爬取 {len(crawler.keywords)} 个关键词...")
        start_time = datetime.now()

        news_items = await crawler.crawl_all_keywords()

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        print(f"\n爬取完成！耗时: {elapsed:.2f}秒")
        print(f"获取新闻总数: {len(news_items)}")

        # 显示统计信息
        keyword_counts = {}
        for item in news_items:
            keyword = item.get('搜索关键词', '未知')
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        print("\n关键词统计:")
        for keyword, count in keyword_counts.items():
            print(f"  {keyword}: {count}条")

        # 保存结果
        if news_items:
            save = input("\n是否保存结果？(y/n): ").lower()
            if save == 'y':
                df = crawler.save_results(news_items)

                # 显示预览
                print("\n数据预览:")
                print(df[['新闻标题', '发布时间', '来源', '搜索关键词']].head(10).to_string())

        # 保存缓存
        crawler.save_cache()

    except Exception as e:
        logger.error(f"爬取过程出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())