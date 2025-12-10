# company_data.py
def generate_company_data():
    """生成公司风险数据"""
    companies = {
        "新能源科技": {
            "industry": "新能源",
            "stock_code": "300750",
            "market_cap": 800,  # 亿元
            "debt_ratio": 0.45,
            "profit_growth": 0.25,
            "risk_score": 0.3  # 0-1，越高风险越大
        },
        "医药集团": {
            "industry": "医药",
            "stock_code": "600276",
            "market_cap": 300,
            "debt_ratio": 0.35,
            "profit_growth": 0.12,
            "risk_score": 0.5
        },
        "AI智能": {
            "industry": "人工智能",
            "stock_code": "002230",
            "market_cap": 150,
            "debt_ratio": 0.28,
            "profit_growth": 0.35,
            "risk_score": 0.4
        }
    }

    # 公司风险事件
    risk_events = [
        {
            "company": "新能源科技",
            "title": "新能源科技：大股东质押股份比例达30%",
            "content": "公司公告显示，控股股东累计质押公司股份比例已达30%，接近预警线。",
            "date": "2024-06-15",
            "risk_type": "股权质押风险",
            "severity": "medium",
            "source": "公司公告"
        },
        {
            "company": "医药集团",
            "title": "医药集团核心产品遭集采落标",
            "content": "在第七批药品集中采购中，公司核心产品未中标，预计影响年收入约20亿元。",
            "date": "2024-05-25",
            "risk_type": "政策风险",
            "severity": "high",
            "source": "行业新闻"
        },
        {
            "company": "AI智能",
            "title": "AI智能：被美国列入实体清单",
            "content": "美国商务部将公司列入实体清单，限制获取美国技术和产品。",
            "date": "2024-06-01",
            "risk_type": "地缘政治风险",
            "severity": "high",
            "source": "国际新闻"
        }
    ]

    # 财务数据时间序列（简化）
    financial_trends = {
        "新能源科技": {
            "revenue": [100, 120, 150, 180],  # 过去4个季度营收（亿）
            "profit": [15, 18, 22, 25],
            "debt": [200, 220, 240, 250]
        }
    }

    return {
        "companies": companies,
        "risk_events": risk_events,
        "financials": financial_trends
    }