import requests
import json
import pandas as pd
from datetime import datetime
import time

# ===================== 配置项 =====================


INDUSTRY_NAME = "新能源行业"
KEYWORDS = ["补贴政策", "技术突破", "企业营收", "价格波动", "行业风险"]
START_DATE = "2025-12-01"
END_DATE = "2025-12-08"
NEWS_PER_KEYWORD = 5  # 每个关键词采集的新闻数量

# API配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
NEWS_API_URL = "https://newsapi.org/v2/everything"

HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}


def search_real_news(keyword, max_results=10):
    """
    使用NewsAPI搜索真实新闻
    返回：新闻列表
    """
    if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWS_API_KEY":
        print(f"⚠️  未配置NewsAPI密钥，跳过真实新闻搜索")
        return []

    params = {
        "q": f"{keyword} {INDUSTRY_NAME}",
        "apiKey": NEWS_API_KEY,
        "from": START_DATE,
        "to": END_DATE,
        "language": "zh",
        "sortBy": "publishedAt",
        "pageSize": max_results
    }

    try:
        print(f"🔍 正在搜索「{keyword}」相关新闻...")
        response = requests.get(NEWS_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "ok" and data.get("articles"):
            articles = data["articles"]
            print(f"✅ 找到「{keyword}」相关新闻 {len(articles)} 条")
            return articles
        else:
            print(f"⚠️  未找到「{keyword}」相关新闻")
            return []
    except Exception as e:
        print(f"❌ NewsAPI搜索失败: {e}")
        return []


def generate_structured_news_data():
    """
    生成结构化新闻数据
    使用DeepSeek根据关键词生成模拟新闻数据
    """
    all_news = []

    for keyword in KEYWORDS:
        print(f"\n📝 生成「{keyword}」相关新闻数据...")

        # 构建Prompt，要求生成结构化数据
        prompt = f"""
        请为{INDUSTRY_NAME}在{START_DATE}至{END_DATE}期间生成{NEWS_PER_KEYWORD}条与「{keyword}」相关的模拟新闻数据。

        要求：
        1. 每条新闻必须是模拟的真实新闻，内容详实可信
        2. 数据格式为JSON数组，包含以下字段：
           - 标题 (title): 新闻标题
           - 发布时间 (publish_time): 格式为YYYY-MM-DD HH:MM:SS
           - 来源 (source): 新闻媒体名称（如：财经网、新华网、新浪财经等）
           - 核心摘要 (summary): 新闻核心内容摘要（150-300字）
           - 详情链接 (url): 模拟的新闻链接（可以为空字符串）
        3. 新闻内容应基于{INDUSTRY_NAME}的实际情况，反映市场动态
        4. 只返回JSON数组，不要添加任何解释文字

        示例格式：
        [
          {{
            "title": "新能源汽车补贴政策再次延长三年",
            "publish_time": "2025-12-05 10:30:00",
            "source": "财经网",
            "summary": "财政部今日发布通知，新能源汽车购置补贴政策将延长至2028年底...",
            "url": "https://example.com/news/12345"
          }}
        ]
        """

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=HEADERS,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # 提取JSON数据
            content = result["choices"][0]["message"]["content"].strip()

            # 清理可能的Markdown代码块标记
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # 解析JSON
            news_data = json.loads(content)

            # 添加行业和关键词信息
            for news_item in news_data:
                news_item["所属行业"] = INDUSTRY_NAME
                news_item["采集关键词"] = keyword
                news_item["采集时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 确保所有必需字段都存在
                if "url" not in news_item:
                    news_item["url"] = ""

                all_news.append(news_item)

            print(f"✅ 成功生成「{keyword}」新闻 {len(news_data)} 条")

            # 避免API调用过于频繁
            time.sleep(1)

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print("原始内容:", content[:500])
        except Exception as e:
            print(f"❌ 生成「{keyword}」新闻失败: {e}")
            continue

    return all_news


def get_hybrid_news_data():
    """
    混合模式：先尝试获取真实新闻，不足部分用模拟数据补充
    """
    all_news = []

    for keyword in KEYWORDS:
        print(f"\n{'=' * 60}")
        print(f"处理关键词: {keyword}")

        # 先尝试获取真实新闻
        real_articles = search_real_news(keyword, max_results=NEWS_PER_KEYWORD)

        collected_count = 0

        # 处理真实新闻
        if real_articles:
            for article in real_articles[:NEWS_PER_KEYWORD]:
                news_item = {
                    "title": article.get("title", "无标题"),
                    "publish_time": article.get("publishedAt", "").replace("T", " ").replace("Z", ""),
                    "source": article.get("source", {}).get("name", "未知来源"),
                    "summary": article.get("description", article.get("content", "无摘要"))[:300],
                    "url": article.get("url", ""),
                    "所属行业": INDUSTRY_NAME,
                    "采集关键词": keyword,
                    "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "数据来源": "NewsAPI"
                }
                all_news.append(news_item)
                collected_count += 1

        # 如果真实新闻不足，用模拟数据补充
        if collected_count < NEWS_PER_KEYWORD:
            needed_count = NEWS_PER_KEYWORD - collected_count
            print(f"需要补充 {needed_count} 条模拟新闻")

            # 生成模拟新闻
            prompt = f"""
            请为{INDUSTRY_NAME}生成{needed_count}条与「{keyword}」相关的模拟新闻数据。

            要求：
            1. 每条新闻必须是模拟的真实新闻，内容详实可信
            2. 数据格式为JSON数组，包含以下字段：
               - title: 新闻标题
               - publish_time: 格式为YYYY-MM-DD HH:MM:SS（在{START_DATE}至{END_DATE}期间）
               - source: 新闻媒体名称
               - summary: 新闻核心内容摘要（150-300字）
               - url: 模拟的新闻链接（可以为空字符串）
            3. 只返回JSON数组，不要添加任何解释文字
            """

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }

            try:
                response = requests.post(DEEPSEEK_API_URL, headers=HEADERS, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()

                content = result["choices"][0]["message"]["content"].strip()

                # 清理可能的Markdown代码块标记
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                # 解析JSON
                simulated_news = json.loads(content)

                # 添加额外信息
                for news_item in simulated_news[:needed_count]:
                    news_item["所属行业"] = INDUSTRY_NAME
                    news_item["采集关键词"] = keyword
                    news_item["采集时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    news_item["数据来源"] = "DeepSeek模拟"

                    if "url" not in news_item:
                        news_item["url"] = ""

                    all_news.append(news_item)

                print(f"✅ 补充模拟新闻 {min(needed_count, len(simulated_news))} 条")

            except Exception as e:
                print(f"❌ 补充模拟新闻失败: {e}")

        print(
            f"📊 关键词「{keyword}」总计采集 {min(NEWS_PER_KEYWORD, len(real_articles) + (NEWS_PER_KEYWORD - collected_count))} 条新闻")

    return all_news


def save_to_excel(news_data, filename=None):
    """将新闻数据保存为Excel文件"""
    if not news_data:
        print("⚠️  没有数据可保存")
        return None

    df = pd.DataFrame(news_data)

    # 重命名列，使其更易读
    column_mapping = {
        "title": "标题",
        "publish_time": "发布时间",
        "source": "来源",
        "summary": "核心摘要",
        "url": "详情链接"
    }

    df.rename(columns=column_mapping, inplace=True)

    # 重新排列列顺序
    preferred_order = ["标题", "发布时间", "来源", "核心摘要", "所属行业",
                       "采集关键词", "采集时间", "数据来源", "详情链接"]

    # 只保留存在的列
    ordered_columns = [col for col in preferred_order if col in df.columns]
    df = df[ordered_columns]

    # 生成文件名
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{INDUSTRY_NAME}_新闻数据_{timestamp}.xlsx"

    # 保存到Excel
    df.to_excel(filename, index=False)
    print(f"💾 数据已保存到: {filename}")

    return df, filename


def main():
    """主函数"""
    print(f"🚀 开始采集「{INDUSTRY_NAME}」新闻数据")
    print(f"📅 时间范围: {START_DATE} 至 {END_DATE}")
    print(f"🔑 关键词: {', '.join(KEYWORDS)}")
    print(f"📊 每个关键词采集数量: {NEWS_PER_KEYWORD}条")
    print("=" * 60)

    # 选择数据采集模式
    print("\n请选择数据采集模式:")
    print("1. 纯模拟数据 (使用DeepSeek生成)")
    print("2. 混合模式 (先尝试真实新闻，不足部分用模拟数据补充)")
    print("3. 仅真实新闻 (需要配置NewsAPI密钥)")

    choice = input("请输入选择 (1/2/3, 默认1): ").strip()

    if choice == "3" and (not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWS_API_KEY"):
        print("❌ 选择了仅真实新闻模式但未配置NewsAPI密钥，将使用混合模式")
        choice = "2"

    news_data = []

    if choice == "2":
        print("\n📡 使用混合模式采集数据...")
        news_data = get_hybrid_news_data()
    elif choice == "3":
        print("\n📡 使用仅真实新闻模式...")
        # 这里可以单独实现仅真实新闻的逻辑
        # 为了简化，我们先使用混合模式
        print("⚠️  此模式需要完整实现，暂时使用混合模式")
        news_data = get_hybrid_news_data()
    else:
        print("\n🤖 使用纯模拟数据模式...")
        news_data = generate_structured_news_data()

    # 保存数据
    if news_data:
        df, filename = save_to_excel(news_data)

        # 显示数据统计
        print(f"\n📈 数据统计:")
        print(f"总新闻条数: {len(news_data)}")
        print(f"涉及关键词: {', '.join(set([n.get('采集关键词', '') for n in news_data]))}")

        # 显示前几条数据
        print(f"\n📰 数据预览 (前5条):")
        print(df.head().to_string(index=False))

        # 按关键词统计
        if '采集关键词' in df.columns:
            print(f"\n📊 按关键词统计:")
            keyword_counts = df['采集关键词'].value_counts()
            for keyword, count in keyword_counts.items():
                print(f"  {keyword}: {count}条")
    else:
        print("❌ 未采集到任何数据")


if __name__ == "__main__":
    main()