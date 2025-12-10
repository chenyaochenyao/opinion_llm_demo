# risk_event_generator.py
import json
import random
from datetime import datetime, timedelta


class RiskEventGenerator:
    """风险事件生成器"""

    def __init__(self, controller):
        self.controller = controller

    def generate_risk_events(self, companies_data: list[dict],
                             events_per_company: int = 3) -> list[dict]:
        """生成风险事件数据"""

        all_events = []

        for company in companies_data:
            company_name = company["公司名称"]
            print(f"  为{company_name}生成风险事件...")

            # 生成该公司的风险事件
            company_events = self._generate_events_for_company(
                company,
                events_per_company
            )

            all_events.extend(company_events)

        return all_events

    def _generate_events_for_company(self, company: dict, count: int) -> list[dict]:
        """为特定公司生成风险事件"""

        company_name = company["公司名称"]
        industry = company["所属行业"]

        prompt = f"""
请为上市公司{company_name}生成{count}条风险事件数据。这些风险事件将用于金融风险监控。

公司背景信息：
{json.dumps(company, ensure_ascii=False, indent=2)}

要求：
1. 生成{count}条不同的风险事件
2. 风险类型要多样（财务风险、经营风险、合规风险等）
3. 严重程度要有差异（高、中、低）
4. 事件内容要具体、真实、专业
5. 事件时间应该在最近一年内
6. 风险事件要符合该公司的实际情况

每条风险事件请包含以下字段：
1. 事件标题 (字符串，简洁描述)
2. 事件内容 (字符串，详细描述，100-300字)
3. 事件时间 (字符串，格式：YYYY-MM-DD HH:MM:SS)
4. 涉及公司 (数组，至少包含{company_name})
5. 风险类型 (字符串：财务风险/经营风险/合规风险/市场风险/操作风险/战略风险/声誉风险)
6. 严重程度 (字符串：高/中/低)
7. 影响范围 (字符串：公司层面/行业层面/市场层面)
8. 是否已公开 (布尔值)
9. 信息来源 (字符串：公司公告、监管文件、媒体报道、市场传闻)
10. 关键词 (数组，至少3个关键词)
11. 处置状态 (字符串：未处置/处置中/已处置)
12. 对股价的潜在影响 (字符串：重大负面/轻微负面/中性/轻微正面)
13. 对债券评级的影响 (字符串：可能下调/观察名单/维持不变)
14. 紧急程度 (字符串：立即处置/近期关注/常规监控)
15. 相关金额 (浮点数，单位：亿元，如涉及)

请确保：
- 高风险事件的内容要严重
- 低风险事件的内容要轻微
- 事件描述要具体，有细节
- 事件时间要合理分布在最近一年内
- 风险类型要与事件内容匹配

请以JSON数组格式返回。
"""

        system_prompt = """你是专业的金融风控分析师，擅长生成真实、合理、专业的风险事件数据。
        你生成的风险事件要符合上市公司的实际情况和风险特征。
        事件内容要具体、专业，有足够的信息量用于风险分析。
        请用中文生成数据。"""

        response = self.controller.generate_with_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        try:
            events_data = json.loads(response)

            # 处理数据格式
            if isinstance(events_data, dict):
                for key, value in events_data.items():
                    if isinstance(value, list):
                        events = value
                        break
                else:
                    events = [events_data]
            else:
                events = events_data

            # 处理每条事件
            processed_events = []
            for i, event in enumerate(events):
                event = self._enrich_event_data(event, company, i)
                processed_events.append(event)

            # 确保数量正确
            if len(processed_events) < count:
                for i in range(count - len(processed_events)):
                    event = self._generate_mock_event(company, len(processed_events) + i + 1)
                    processed_events.append(event)

            return processed_events

        except json.JSONDecodeError:
            print(f"    ⚠️  {company_name}风险事件解析失败，使用模拟数据")
            return [self._generate_mock_event(company, i + 1) for i in range(count)]

    def _enrich_event_data(self, event: dict, company: dict, index: int) -> dict:
        """丰富风险事件数据，确保字段完整"""

        company_name = company["公司名称"]

        # 设置默认值
        defaults = {
            "事件标题": event.get("事件标题", f"{company_name}风险事件{index + 1}"),
            "事件内容": event.get("事件内容", f"{company_name}发生风险事件。"),
            "事件时间": event.get("事件时间", self._random_datetime()),
            "涉及公司": event.get("涉及公司", [company_name]),
            "风险类型": event.get("风险类型", random.choice(["财务风险", "经营风险", "合规风险"])),
            "严重程度": event.get("严重程度", random.choice(["高", "中", "低"])),
            "影响范围": event.get("影响范围", random.choice(["公司层面", "行业层面"])),
            "是否已公开": event.get("是否已公开", random.choice([True, False])),
            "信息来源": event.get("信息来源", random.choice(["公司公告", "媒体报道", "监管文件"])),
            "关键词": event.get("关键词", [company_name, "风险", "事件"]),
            "处置状态": event.get("处置状态", random.choice(["未处置", "处置中", "已处置"])),
            "对股价的潜在影响": event.get("对股价的潜在影响", random.choice(["轻微负面", "中性", "重大负面"])),
            "对债券评级的影响": event.get("对债券评级的影响", random.choice(["可能下调", "观察名单", "维持不变"])),
            "紧急程度": event.get("紧急程度", random.choice(["立即处置", "近期关注", "常规监控"])),
            "相关金额": event.get("相关金额", round(random.uniform(0.1, 10.0), 2) if random.random() > 0.5 else None)
        }

        # 应用默认值
        for key, default in defaults.items():
            if key not in event or event[key] is None:
                if callable(default):
                    event[key] = default()
                else:
                    event[key] = default

        # 确保涉及公司包含当前公司
        if company_name not in event["涉及公司"]:
            event["涉及公司"].append(company_name)

        # 根据严重程度调整其他字段
        severity = event["严重程度"]
        if severity == "高":
            event["对股价的潜在影响"] = "重大负面"
            event["对债券评级的影响"] = "可能下调"
            event["紧急程度"] = "立即处置"
        elif severity == "中":
            event["对股价的潜在影响"] = random.choice(["轻微负面", "中性"])
            event["对债券评级的影响"] = "观察名单"
            event["紧急程度"] = "近期关注"

        return event

    def _generate_mock_event(self, company: dict, index: int) -> dict:
        """生成模拟风险事件数据（备选）"""

        company_name = company["公司名称"]
        industry = company["所属行业"]

        # 根据公司特征生成事件
        risk_events = []

        # 如果负债率高，增加财务风险
        if company.get("资产负债率", 0.5) > 0.6:
            risk_events.append({
                "title": "债务压力加大，偿债能力受关注",
                "content": f"{company_name}资产负债率较高，市场对其偿债能力表示关注。",
                "risk_type": "财务风险",
                "severity": "中"
            })

        # 如果质押比例高，增加股权风险
        if company.get("质押比例", 0) > 0.2:
            risk_events.append({
                "title": "大股东质押比例较高",
                "content": f"{company_name}大股东质押股份比例较高，存在平仓风险。",
                "risk_type": "财务风险",
                "severity": "中"
            })

        # 行业特定风险
        industry_risks = {
            "新能源": [
                {"title": "原材料价格大幅上涨", "content": "锂电池原材料价格大幅上涨，压缩公司利润空间。",
                 "risk_type": "经营风险", "severity": "中"},
                {"title": "技术路线面临变革", "content": "行业技术路线可能发生重大变革，公司现有技术面临淘汰风险。",
                 "risk_type": "战略风险", "severity": "高"}
            ],
            "医药": [
                {"title": "核心产品集采未中标", "content": "公司核心产品在国家药品集采中未中标，影响未来收入。",
                 "risk_type": "政策风险", "severity": "高"},
                {"title": "新药研发进展不及预期", "content": "公司在研新药临床试验进展不及预期，可能影响上市时间。",
                 "risk_type": "研发风险", "severity": "中"}
            ],
            "人工智能": [
                {"title": "关键技术人才流失", "content": "公司关键技术人才离职，可能影响技术研发进度。",
                 "risk_type": "经营风险", "severity": "中"},
                {"title": "算法合规风险", "content": "公司AI算法可能面临数据安全和算法合规风险。",
                 "risk_type": "合规风险", "severity": "中"}
            ]
        }

        # 添加行业风险
        industry_risk_list = industry_risks.get(industry, [])
        risk_events.extend(industry_risk_list)

        # 通用风险
        generic_risks = [
            {"title": "重大合同纠纷", "content": f"{company_name}与合作伙伴发生重大合同纠纷。", "risk_type": "经营风险",
             "severity": "中"},
            {"title": "监管问询函", "content": f"{company_name}收到交易所监管问询函。", "risk_type": "合规风险",
             "severity": "低"},
            {"title": "业绩预告不达预期", "content": f"{company_name}发布业绩预告，业绩不达市场预期。",
             "risk_type": "财务风险", "severity": "中"}
        ]

        risk_events.extend(generic_risks)

        # 选择事件
        if index <= len(risk_events):
            template = risk_events[index - 1]
        else:
            template = {
                "title": f"{company_name}风险事件",
                "content": f"{company_name}发生风险事件，具体情况正在核实中。",
                "risk_type": random.choice(["财务风险", "经营风险", "合规风险"]),
                "severity": random.choice(["高", "中", "低"])
            }

        # 确定其他字段
        severity = template["severity"]

        if severity == "高":
            stock_impact = "重大负面"
            bond_impact = "可能下调"
            urgency = "立即处置"
        elif severity == "中":
            stock_impact = random.choice(["轻微负面", "中性"])
            bond_impact = "观察名单"
            urgency = "近期关注"
        else:
            stock_impact = "轻微负面"
            bond_impact = "维持不变"
            urgency = "常规监控"

        return {
            "事件标题": template["title"],
            "事件内容": template["content"],
            "事件时间": self._random_datetime(),
            "涉及公司": [company_name],
            "风险类型": template["risk_type"],
            "严重程度": severity,
            "影响范围": random.choice(["公司层面", "行业层面"]),
            "是否已公开": random.choice([True, False]),
            "信息来源": random.choice(["公司公告", "媒体报道", "监管文件"]),
            "关键词": [company_name, template["risk_type"], severity],
            "处置状态": random.choice(["未处置", "处置中", "已处置"]),
            "对股价的潜在影响": stock_impact,
            "对债券评级的影响": bond_impact,
            "紧急程度": urgency,
            "相关金额": round(random.uniform(0.5, 5.0), 2) if random.random() > 0.5 else None
        }

    def _random_datetime(self) -> str:
        """生成随机时间（最近一年内）"""
        end = datetime.now()
        start = end - timedelta(days=365)
        random_time = start + timedelta(
            seconds=random.randint(0, int((end - start).total_seconds()))
        )
        return random_time.strftime("%Y-%m-%d %H:%M:%S")