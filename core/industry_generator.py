# industry_generator.py
import json
import random
from datetime import datetime


class IndustryGenerator:
    """行业数据生成器"""

    def __init__(self, controller):
        self.controller = controller

    def generate_industries(self, industry_names: list[str]) -> list[dict]:
        """生成行业数据"""

        all_industries = []

        for industry_name in industry_names:
            print(f"  生成行业: {industry_name}")

            prompt = f"""
请生成关于{industry_name}行业的详细结构化数据。请确保数据真实、准确、专业，符合金融分析的要求。

要求：
1. 生成一个详细的行业分析数据对象
2. 数据要符合金融行业的专业标准
3. 包括定量和定性数据
4. 数据要具有内在逻辑一致性

请以JSON格式返回，包含以下字段：
1. 行业名称 (字符串)
2. 行业代码 (字符串，2-4个字母)
3. 行业描述 (字符串，详细描述)
4. 产业链位置 (字符串：上游/中游/下游)
5. 增长驱动力 (数组，至少3个)
6. 主要风险 (数组，至少3个)
7. 行业周期 (字符串：导入期/成长期/成熟期/衰退期)
8. 预期增长率 (浮点数，0-1之间)
9. 市盈率区间 (数组，两个浮点数，最小值和最大值)
10. 关键成功因素 (数组，至少3个)
11. 竞争格局 (字符串：垄断/寡头垄断/垄断竞争/完全竞争)
12. 技术壁垒 (字符串：高/中/低)
13. 政策依赖度 (浮点数，0-1之间)
14. 资本密集度 (浮点数，0-1之间)
15. 毛利率典型区间 (数组，两个浮点数，最小值和最大值)
16. 头部企业市场份额 (浮点数，0-1之间)
17. 进出口依赖度 (浮点数，0-1之间)
18. ESG评分 (浮点数，0-100)
19. 创新指数 (浮点数，0-100)
20. 行业热度指数 (浮点数，0-100)

请确保数据符合{industry_name}行业的实际情况。生成的数据应该足够详细，可以用于专业的金融分析。
"""

            system_prompt = """你是专业的金融行业分析师，擅长生成高质量的金融行业数据。
            你生成的数据必须真实、准确、专业，符合金融分析的要求。
            数据要具有内在逻辑一致性，比如高资本密集度的行业通常毛利率较低。
            请用中文生成数据。"""

            response = self.controller.generate_with_llm(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            try:
                # 尝试解析为JSON
                industry_data = json.loads(response)

                # 确保是列表形式
                if isinstance(industry_data, dict):
                    industry_data = [industry_data]

                all_industries.extend(industry_data)

            except json.JSONDecodeError:
                print(f"    ⚠️  {industry_name}数据解析失败，使用模拟数据")
                # 使用模拟数据
                all_industries.append(self._generate_mock_industry(industry_name))

        return all_industries

    def _generate_mock_industry(self, industry_name: str) -> dict:
        """生成模拟行业数据（备选）"""

        # 行业特征模板
        industry_templates = {
            "新能源": {
                "行业代码": "NE",
                "产业链位置": "中游",
                "行业周期": "成长期",
                "预期增长率": 0.15,
                "市盈率区间": [25, 45],
                "毛利率典型区间": [0.15, 0.35],
                "政策依赖度": 0.8,
                "资本密集度": 0.7,
                "技术壁垒": "高",
                "ESG评分": 85
            },
            "医药": {
                "行业代码": "PH",
                "产业链位置": "中游",
                "行业周期": "成熟期",
                "预期增长率": 0.08,
                "市盈率区间": [20, 35],
                "毛利率典型区间": [0.40, 0.70],
                "政策依赖度": 0.9,
                "资本密集度": 0.8,
                "技术壁垒": "高",
                "ESG评分": 75
            },
            "人工智能": {
                "行业代码": "AI",
                "产业链位置": "下游",
                "行业周期": "导入期",
                "预期增长率": 0.25,
                "市盈率区间": [40, 80],
                "毛利率典型区间": [0.50, 0.85],
                "政策依赖度": 0.6,
                "资本密集度": 0.5,
                "技术壁垒": "高",
                "ESG评分": 70
            }
        }

        template = industry_templates.get(industry_name, {
            "行业代码": industry_name[:2].upper(),
            "产业链位置": random.choice(["上游", "中游", "下游"]),
            "行业周期": random.choice(["导入期", "成长期", "成熟期", "衰退期"]),
            "预期增长率": round(random.uniform(0.05, 0.25), 3),
            "市盈率区间": [random.randint(10, 30), random.randint(30, 60)],
            "毛利率典型区间": [round(random.uniform(0.1, 0.3), 2), round(random.uniform(0.3, 0.6), 2)],
            "政策依赖度": round(random.uniform(0.3, 0.9), 2),
            "资本密集度": round(random.uniform(0.4, 0.8), 2),
            "技术壁垒": random.choice(["高", "中", "低"]),
            "ESG评分": random.randint(50, 90)
        })

        # 生成描述和驱动力
        descriptions = {
            "新能源": "新能源汽车、光伏、风电等清洁能源产业，是能源转型的核心方向。",
            "医药": "制药、医疗器械、医疗服务等大健康产业，具有弱周期性和高成长性。",
            "人工智能": "AI算法、算力、应用三位一体的新兴产业，是数字经济的核心引擎。",
            "半导体": "集成电路设计、制造、封测全产业链，是科技自立自强的关键领域。",
            "金融": "银行、保险、证券等金融服务行业，是现代经济的核心。",
            "房地产": "房地产开发、物业管理、房地产服务等，是国民经济的支柱产业。",
            "消费": "食品饮料、家电、零售等消费品行业，受益于消费升级。",
            "周期": "钢铁、煤炭、有色等周期性行业，与经济周期密切相关。"
        }

        growth_drivers = {
            "新能源": ["政策支持", "技术突破", "环保需求", "成本下降", "能源安全"],
            "医药": ["老龄化", "健康意识", "创新药", "医保覆盖", "消费升级"],
            "人工智能": ["数字化转型", "算法突破", "算力提升", "应用场景", "政策支持"]
        }

        risks = {
            "新能源": ["原材料涨价", "技术迭代", "政策变动", "竞争加剧", "产能过剩"],
            "医药": ["集采降价", "研发失败", "监管趋严", "专利到期", "合规风险"],
            "人工智能": ["技术垄断", "数据安全", "伦理问题", "人才短缺", "应用落地难"]
        }

        return {
            "行业名称": industry_name,
            "行业代码": template["行业代码"],
            "行业描述": descriptions.get(industry_name, f"{industry_name}行业，具有重要经济地位。"),
            "产业链位置": template["产业链位置"],
            "增长驱动力": growth_drivers.get(industry_name, ["技术创新", "市场需求", "政策支持"]),
            "主要风险": risks.get(industry_name, ["政策风险", "市场风险", "技术风险"]),
            "行业周期": template["行业周期"],
            "预期增长率": template["预期增长率"],
            "市盈率区间": template["市盈率区间"],
            "关键成功因素": ["技术创新", "成本控制", "市场拓展", "人才储备"],
            "竞争格局": random.choice(["寡头垄断", "垄断竞争", "完全竞争"]),
            "技术壁垒": template["技术壁垒"],
            "政策依赖度": template["政策依赖度"],
            "资本密集度": template["资本密集度"],
            "毛利率典型区间": template["毛利率典型区间"],
            "头部企业市场份额": round(random.uniform(0.2, 0.6), 2),
            "进出口依赖度": round(random.uniform(0.1, 0.5), 2),
            "ESG评分": template["ESG评分"],
            "创新指数": random.randint(60, 95),
            "行业热度指数": random.randint(50, 90)
        }