# industry_data.py
import json
import random


def generate_industry_data():
    """生成行业仿真数据"""
    industries = {
        "新能源": {
            "description": "新能源汽车、光伏、风电等清洁能源产业",
            "upstream": ["锂矿", "稀土", "半导体"],
            "downstream": ["汽车制造", "电网", "储能"],
            "competitors": ["传统能源", "化石燃料"],
            "growth_rate": random.uniform(0.1, 0.25)  # 10-25%增速
        },
        "医药": {
            "description": "制药、医疗器械、医疗服务",
            "upstream": ["化工原料", "生物技术"],
            "downstream": ["医院", "药店", "消费者"],
            "competitors": ["仿制药企", "国际药企"],
            "growth_rate": random.uniform(0.05, 0.15)
        },
        "人工智能": {
            "description": "AI算法、算力、应用",
            "upstream": ["芯片", "云计算"],
            "downstream": ["金融科技", "智能制造", "自动驾驶"],
            "competitors": ["国际AI巨头"],
            "growth_rate": random.uniform(0.2, 0.4)
        }
    }

    # 行业政策新闻
    policy_news = [
        {
            "industry": "新能源",
            "title": "国家能源局：2024年新能源汽车补贴政策延续",
            "content": "国家能源局宣布新能源汽车购置补贴政策将延续至2025年底，补贴标准维持不变。",
            "date": "2024-06-10",
            "impact": "positive",  # positive/negative/neutral
            "impact_score": 0.8,
            "source": "政府公告"
        },
        {
            "industry": "医药",
            "title": "医保局：第七批药品集采平均降价48%",
            "content": "国家医保局开展第七批药品集中采购，涉及61个品种，平均降价48%。",
            "date": "2024-05-20",
            "impact": "negative",
            "impact_score": -0.6,
            "source": "医保局官网"
        }
    ]

    # 行业关联数据
    industry_correlations = {
        "新能源": ["人工智能", "半导体", "电力设备"],
        "医药": ["医疗器械", "医疗服务", "生物科技"],
        "人工智能": ["云计算", "大数据", "半导体"]
    }

    return {
        "industries": industries,
        "policy_news": policy_news,
        "correlations": industry_correlations
    }