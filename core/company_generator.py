# company_generator.py
import json
import random
from datetime import datetime, timedelta


class CompanyGenerator:
    """公司数据生成器"""

    def __init__(self, controller):
        self.controller = controller

    def generate_companies(self, industries_data: list[dict], companies_per_industry: int = 3) -> list[dict]:
        """生成公司数据"""

        all_companies = []

        for industry in industries_data:
            industry_name = industry["行业名称"]
            print(f"  为{industry_name}行业生成公司数据...")

            # 生成该行业的公司
            industry_companies = self._generate_companies_for_industry(
                industry,
                companies_per_industry
            )

            all_companies.extend(industry_companies)

        return all_companies

    def _generate_companies_for_industry(self, industry: dict, count: int) -> list[dict]:
        """为特定行业生成公司数据"""

        industry_name = industry["行业名称"]

        prompt = f"""
请为{industry_name}行业生成{count}家上市公司的详细数据。这些数据将用于金融分析和风险监控。

行业背景：
{json.dumps(industry, ensure_ascii=False, indent=2)}

要求：
1. 生成{count}家不同的公司数据
2. 公司数据要符合该行业的特征
3. 包括财务数据、业务数据、治理数据
4. 数据要真实、合理，有内在逻辑
5. 公司之间要有差异性（规模、盈利能力、风险水平等）

每家公司请包含以下字段：
1. 公司名称 (字符串，格式：行业+业务+公司性质，如"新能源电池股份有限公司")
2. 股票代码 (字符串，6位数字，以行业代码开头)
3. 所属行业 (字符串)
4. 总市值 (浮点数，单位：亿元)
5. 流通市值 (浮点数，单位：亿元)
6. 营业收入 (浮点数，单位：亿元，最近年报)
7. 净利润 (浮点数，单位：亿元，最近年报)
8. 资产负债率 (浮点数，0-1之间)
9. 毛利率 (浮点数，0-1之间)
10. 净利率 (浮点数，0-1之间)
11. ROE (净资产收益率，浮点数，0-1之间)
12. 市盈率 (浮点数)
13. 市净率 (浮点数)
14. 主营业务 (字符串，详细描述)
15. 核心竞争力 (数组，至少3个)
16. 主要风险 (数组，至少3个)
17. 股权结构 (对象：实际控制人比例、机构持股比例、散户比例，总和为1)
18. 机构持股比例 (浮点数，0-1之间)
19. 融资融券余额 (浮点数，单位：亿元)
20. 北向资金持股比例 (浮点数，0-1之间)
21. 质押比例 (浮点数，0-1之间)
22. 商誉占总资产比例 (浮点数，0-1之间)
23. 现金流状况 (字符串：充裕/良好/紧张/很差)
24. 研发投入占比 (浮点数，0-1之间)
25. 员工人数 (整数)
26. 成立年份 (整数)
27. 上市年份 (整数)
28. 总部所在地 (字符串)
29. 审计意见 (字符串：标准无保留意见/带强调事项段的无保留意见/保留意见/无法表示意见/否定意见)
30. 风险评分 (整数，0-100，越高风险越大)

请确保数据合理，比如：
- 高增长行业公司市盈率较高
- 高负债公司现金流可能紧张
- 高研发投入的公司可能在成长期

请以JSON数组格式返回。
"""

        system_prompt = """你是专业的金融数据分析师，擅长生成真实、合理、专业的上市公司数据。
        你生成的数据要符合会计准则和行业实际情况。
        数据之间要有合理的关联性，比如高负债率的公司风险评分应该较高。
        请用中文生成数据。"""

        response = self.controller.generate_with_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        try:
            companies_data = json.loads(response)

            # 如果是字典且包含列表
            if isinstance(companies_data, dict):
                # 寻找包含列表的键
                for key, value in companies_data.items():
                    if isinstance(value, list):
                        companies = value
                        break
                else:
                    companies = [companies_data]
            else:
                companies = companies_data

            # 确保数量正确
            if len(companies) < count:
                # 补充生成
                additional_count = count - len(companies)
                for i in range(additional_count):
                    companies.append(self._generate_mock_company(industry, i + len(companies) + 1))

            # 处理每个公司数据
            processed_companies = []
            for i, company in enumerate(companies):
                # 确保必要字段存在
                company = self._enrich_company_data(company, industry, i + 1)
                processed_companies.append(company)

            return processed_companies

        except json.JSONDecodeError:
            print(f"    ⚠️  {industry_name}公司数据解析失败，使用模拟数据")
            return [self._generate_mock_company(industry, i + 1) for i in range(count)]

    def _enrich_company_data(self, company: dict, industry: dict, index: int) -> dict:
        """丰富公司数据，确保字段完整"""

        industry_name = industry["行业名称"]
        industry_code = industry.get("行业代码", "00")

        # 设置默认值
        defaults = {
            "公司名称": company.get("公司名称", f"{industry_name}公司{index}"),
            "股票代码": company.get("股票代码", f"{industry_code}{index:04d}"),
            "所属行业": industry_name,
            "总市值": company.get("总市值", round(random.uniform(50, 500), 2)),
            "流通市值": company.get("流通市值", lambda c: c.get("总市值", 100) * random.uniform(0.6, 0.9)),
            "营业收入": company.get("营业收入", round(random.uniform(10, 200), 2)),
            "净利润": company.get("净利润", lambda c: c.get("营业收入", 100) * random.uniform(0.05, 0.2)),
            "资产负债率": company.get("资产负债率", round(random.uniform(0.3, 0.7), 3)),
            "毛利率": company.get("毛利率", round(random.uniform(0.15, 0.45), 3)),
            "净利率": company.get("净利率", lambda c: c.get("毛利率", 0.3) * random.uniform(0.4, 0.7)),
            "ROE": company.get("ROE", round(random.uniform(0.08, 0.2), 3)),
            "市盈率": company.get("市盈率", round(random.uniform(15, 40), 2)),
            "市净率": company.get("市净率", round(random.uniform(1.5, 4.5), 2)),
            "风险评分": company.get("风险评分", random.randint(30, 70))
        }

        # 应用默认值
        for key, default in defaults.items():
            if key not in company or company[key] is None:
                if callable(default):
                    company[key] = default(company)
                else:
                    company[key] = default

        # 计算衍生字段
        if "流通市值" not in company:
            company["流通市值"] = round(company["总市值"] * random.uniform(0.6, 0.9), 2)

        if "净利润" not in company and "营业收入" in company and "净利率" in company:
            company["净利润"] = round(company["营业收入"] * company["净利率"], 2)

        # 确保股权结构
        if "股权结构" not in company:
            company["股权结构"] = {
                "实际控制人比例": round(random.uniform(0.2, 0.4), 3),
                "机构持股比例": round(random.uniform(0.3, 0.6), 3),
                "散户比例": round(random.uniform(0.1, 0.3), 3)
            }

        # 确保数值范围合理
        company["资产负债率"] = min(max(company["资产负债率"], 0.1), 0.9)
        company["毛利率"] = min(max(company["毛利率"], 0.05), 0.8)
        company["净利率"] = min(max(company["净利率"], 0.02), 0.4)
        company["风险评分"] = min(max(company["风险评分"], 0), 100)

        return company

    def _generate_mock_company(self, industry: dict, index: int) -> dict:
        """生成模拟公司数据（备选）"""

        industry_name = industry["行业名称"]
        industry_code = industry.get("行业代码", "00")

        # 行业特定的参数
        industry_params = {
            "新能源": {
                "市值_range": (80, 500),
                "毛利率_range": (0.15, 0.35),
                "研发投入_range": (0.03, 0.08)
            },
            "医药": {
                "市值_range": (100, 300),
                "毛利率_range": (0.40, 0.70),
                "研发投入_range": (0.05, 0.12)
            },
            "人工智能": {
                "市值_range": (50, 200),
                "毛利率_range": (0.50, 0.85),
                "研发投入_range": (0.08, 0.20)
            }
        }

        params = industry_params.get(industry_name, {
            "市值_range": (50, 300),
            "毛利率_range": (0.20, 0.50),
            "研发投入_range": (0.02, 0.06)
        })

        # 生成公司名称
        company_types = ["科技", "股份", "集团", "控股", "发展", "实业"]
        business_areas = {
            "新能源": ["电池", "光伏", "风电", "储能", "新能源汽车"],
            "医药": ["制药", "生物", "医疗器械", "医疗服务", "医药商业"],
            "人工智能": ["智能", "数据", "算法", "算力", "应用"]
        }

        business = random.choice(business_areas.get(industry_name, ["科技", "发展", "实业"]))
        company_type = random.choice(company_types)

        # 财务数据
        revenue = round(random.uniform(10, 200), 2)
        gross_margin = round(random.uniform(*params["毛利率_range"]), 3)
        net_margin = round(gross_margin * random.uniform(0.4, 0.7), 3)
        net_profit = round(revenue * net_margin, 2)
        market_cap = round(random.uniform(*params["市值_range"]), 2)
        debt_ratio = round(random.uniform(0.3, 0.65), 3)

        # 计算风险评分（基于多个因素）
        risk_score = 0
        risk_score += debt_ratio * 30  # 负债率贡献
        risk_score += (1 - gross_margin) * 20  # 低毛利率贡献
        risk_score += random.randint(10, 30)  # 随机风险
        risk_score = min(int(risk_score), 100)

        return {
            "公司名称": f"{industry_name}{business}{company_type}",
            "股票代码": f"{industry_code}{index:04d}",
            "所属行业": industry_name,
            "总市值": market_cap,
            "流通市值": round(market_cap * random.uniform(0.6, 0.9), 2),
            "营业收入": revenue,
            "净利润": net_profit,
            "资产负债率": debt_ratio,
            "毛利率": gross_margin,
            "净利率": net_margin,
            "ROE": round(random.uniform(0.08, 0.25), 3),
            "市盈率": round(random.uniform(15, 40), 2),
            "市净率": round(random.uniform(1.2, 4.0), 2),
            "主营业务": f"{industry_name}{business}的研发、生产和销售",
            "核心竞争力": ["技术领先", "成本优势", "客户资源", "品牌效应"],
            "主要风险": ["政策变动", "竞争加剧", "原材料涨价", "技术迭代"],
            "股权结构": {
                "实际控制人比例": round(random.uniform(0.2, 0.4), 3),
                "机构持股比例": round(random.uniform(0.3, 0.6), 3),
                "散户比例": round(random.uniform(0.1, 0.3), 3)
            },
            "机构持股比例": round(random.uniform(0.3, 0.6), 3),
            "融资融券余额": round(random.uniform(1, 10), 2),
            "北向资金持股比例": round(random.uniform(0.02, 0.1), 3),
            "质押比例": round(random.uniform(0, 0.3), 3),
            "商誉占总资产比例": round(random.uniform(0, 0.2), 3),
            "现金流状况": random.choice(["充裕", "良好", "紧张", "很差"]),
            "研发投入占比": round(random.uniform(*params["研发投入_range"]), 3),
            "员工人数": random.randint(500, 10000),
            "成立年份": random.randint(1990, 2010),
            "上市年份": random.randint(2010, 2020),
            "总部所在地": random.choice(["北京", "上海", "深圳", "杭州", "广州"]),
            "审计意见": random.choice(["标准无保留意见", "带强调事项段的无保留意见", "保留意见"]),
            "风险评分": risk_score
        }