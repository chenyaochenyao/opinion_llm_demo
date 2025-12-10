# policy_generator.py
import json
import random
from datetime import datetime, timedelta


class PolicyGenerator:
    """政策新闻生成器"""

    def __init__(self, controller):
        self.controller = controller

    def generate_policies(self, industries_data: list[dict],
                          policies_per_industry: int = 5) -> list[dict]:
        """生成政策新闻数据"""

        all_policies = []

        for industry in industries_data:
            industry_name = industry["行业名称"]
            print(f"  为{industry_name}行业生成政策新闻...")

            # 生成该行业的政策新闻
            industry_policies = self._generate_policies_for_industry(
                industry,
                policies_per_industry
            )

            all_policies.extend(industry_policies)

        return all_policies

    def _generate_policies_for_industry(self, industry: dict, count: int) -> list[dict]:
        """为特定行业生成政策新闻"""

        industry_name = industry["行业名称"]

        # 政策类型和影响
        policy_types = ["财政政策", "货币政策", "产业政策", "监管政策", "税收政策", "环保政策"]
        impact_types = ["利好", "利空", "中性"]

        prompt = f"""
请为{industry_name}行业生成{count}条政策新闻数据。这些政策新闻将用于金融舆情分析。

行业背景：
{json.dumps(industry, ensure_ascii=False, indent=2)}

要求：
1. 生成{count}条不同的政策新闻
2. 每条新闻都要有具体的内容、发布时间、影响程度
3. 政策类型要多样（财政、货币、产业、监管等）
4. 影响程度要有差异（利好、利空、中性）
5. 新闻内容要真实、具体、专业
6. 发布时间应该在最近一年内

每条政策新闻请包含以下字段：
1. 标题 (字符串，新闻标题)
2. 内容 (字符串，详细新闻内容，100-300字)
3. 发布时间 (字符串，格式：YYYY-MM-DD HH:MM:SS)
4. 影响类型 (字符串：利好/利空/中性)
5. 影响程度 (浮点数，0-1之间，1表示影响最大)
6. 政策类型 (字符串：财政政策/货币政策/产业政策/监管政策/税收政策/环保政策/其他)
7. 发布机构 (字符串，如：国务院、发改委、证监会等)
8. 相关行业 (数组，至少包含{industry_name})
9. 相关公司 (数组，可以为空)
10. 关键词 (数组，至少3个关键词)
11. 政策时效性 (字符串：长期/中期/短期)
12. 实施范围 (字符串：全国/区域/试点)
13. 预期效果 (字符串，简要描述)
14. 市场反应预测 (字符串：积极/中性/消极)
15. 新闻来源 (字符串：政府官网、财经媒体、行业网站等)

请确保：
- 利好政策的内容要积极正面
- 利空政策的内容要谨慎负面
- 中性政策的内容要客观平衡
- 发布时间要合理分布在最近一年内
- 影响程度要与政策重要性相匹配

请以JSON数组格式返回。
"""

        system_prompt = """你是专业的金融政策分析师，擅长生成真实、合理、专业的政策新闻数据。
        你生成的政策新闻要符合中国的政策环境和行业实际情况。
        新闻内容要具体、专业，有足够的信息量用于分析。
        请用中文生成数据。"""

        response = self.controller.generate_with_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        try:
            policies_data = json.loads(response)

            # 处理数据格式
            if isinstance(policies_data, dict):
                for key, value in policies_data.items():
                    if isinstance(value, list):
                        policies = value
                        break
                else:
                    policies = [policies_data]
            else:
                policies = policies_data

            # 处理每条政策
            processed_policies = []
            for i, policy in enumerate(policies):
                policy = self._enrich_policy_data(policy, industry, i)
                processed_policies.append(policy)

            # 确保数量正确
            if len(processed_policies) < count:
                for i in range(count - len(processed_policies)):
                    policy = self._generate_mock_policy(industry, len(processed_policies) + i + 1)
                    processed_policies.append(policy)

            return processed_policies

        except json.JSONDecodeError:
            print(f"    ⚠️  {industry_name}政策新闻解析失败，使用模拟数据")
            return [self._generate_mock_policy(industry, i + 1) for i in range(count)]

    def _enrich_policy_data(self, policy: dict, industry: dict, index: int) -> dict:
        """丰富政策数据，确保字段完整"""

        industry_name = industry["行业名称"]

        # 设置默认值
        defaults = {
            "标题": policy.get("标题", f"{industry_name}行业新政策{index + 1}"),
            "内容": policy.get("内容", f"关于{industry_name}行业的最新政策动向。"),
            "发布时间": policy.get("发布时间", self._random_datetime()),
            "影响类型": policy.get("影响类型", random.choice(["利好", "利空", "中性"])),
            "影响程度": policy.get("影响程度", round(random.uniform(0.3, 0.9), 2)),
            "政策类型": policy.get("政策类型", random.choice(["产业政策", "监管政策", "财政政策"])),
            "发布机构": policy.get("发布机构", random.choice(["国务院", "发改委", "证监会", "工信部"])),
            "相关行业": policy.get("相关行业", [industry_name]),
            "相关公司": policy.get("相关公司", []),
            "关键词": policy.get("关键词", [industry_name, "政策", "监管"]),
            "政策时效性": policy.get("政策时效性", random.choice(["长期", "中期", "短期"])),
            "实施范围": policy.get("实施范围", random.choice(["全国", "试点", "重点区域"])),
            "预期效果": policy.get("预期效果", "促进行业健康发展"),
            "市场反应预测": policy.get("市场反应预测", random.choice(["积极", "中性", "消极"])),
            "新闻来源": policy.get("新闻来源", random.choice(["政府官网", "财经媒体", "行业网站"]))
        }

        # 应用默认值
        for key, default in defaults.items():
            if key not in policy or policy[key] is None:
                if callable(default):
                    policy[key] = default()
                else:
                    policy[key] = default

        # 确保相关行业包含当前行业
        if industry_name not in policy["相关行业"]:
            policy["相关行业"].append(industry_name)

        # 确保影响程度合理
        if policy["影响类型"] == "利好":
            policy["影响程度"] = abs(policy["影响程度"])
        elif policy["影响类型"] == "利空":
            policy["影响程度"] = -abs(policy["影响程度"])
        else:
            policy["影响程度"] = 0

        return policy

    def _generate_mock_policy(self, industry: dict, index: int) -> dict:
        """生成模拟政策新闻数据（备选）"""

        industry_name = industry["行业名称"]

        # 政策模板
        policy_templates = {
            "新能源": [
                {
                    "title": "新能源汽车购置税减免政策延续",
                    "content": "财政部宣布新能源汽车购置税减免政策将延续三年，预计将带动新能源汽车销量增长。",
                    "impact": "利好",
                    "impact_score": 0.8,
                    "agency": "财政部"
                },
                {
                    "title": "光伏发电补贴退坡机制明确",
                    "content": "国家能源局明确光伏发电补贴退坡机制，新建项目补贴强度逐步降低。",
                    "impact": "利空",
                    "impact_score": -0.6,
                    "agency": "国家能源局"
                }
            ],
            "医药": [
                {
                    "title": "创新药审批绿色通道建立",
                    "content": "国家药监局建立创新药审批绿色通道，加快具有临床价值的创新药上市。",
                    "impact": "利好",
                    "impact_score": 0.7,
                    "agency": "国家药监局"
                },
                {
                    "title": "药品集中采购范围扩大",
                    "content": "国家医保局宣布第七批药品集中采购范围扩大，涉及品种增加至61个。",
                    "impact": "利空",
                    "impact_score": -0.7,
                    "agency": "国家医保局"
                }
            ],
            "人工智能": [
                {
                    "title": "人工智能产业发展行动计划发布",
                    "content": "工信部发布人工智能产业发展行动计划，提出到2025年形成完善的人工智能产业生态。",
                    "impact": "利好",
                    "impact_score": 0.9,
                    "agency": "工信部"
                },
                {
                    "title": "算法推荐服务管理规定出台",
                    "content": "网信办出台算法推荐服务管理规定，要求算法服务提供者加强合规管理。",
                    "impact": "中性",
                    "impact_score": -0.3,
                    "agency": "网信办"
                }
            ]
        }

        templates = policy_templates.get(industry_name, [])

        if index <= len(templates):
            template = templates[index - 1]
        else:
            template = {
                "title": f"{industry_name}行业政策调整",
                "content": f"相关部门对{industry_name}行业政策进行调整。",
                "impact": random.choice(["利好", "利空", "中性"]),
                "impact_score": round(random.uniform(-0.8, 0.8), 2),
                "agency": random.choice(["国务院", "发改委", "证监会", "工信部"])
            }

        # 确定影响程度
        impact_type = template["impact"]
        impact_score = template["impact_score"]

        if impact_type == "利好":
            impact_degree = abs(impact_score)
        elif impact_type == "利空":
            impact_degree = -abs(impact_score)
        else:
            impact_degree = 0

        return {
            "标题": template["title"],
            "内容": template["content"],
            "发布时间": self._random_datetime(),
            "影响类型": impact_type,
            "影响程度": impact_degree,
            "政策类型": random.choice(["产业政策", "监管政策", "财政政策"]),
            "发布机构": template["agency"],
            "相关行业": [industry_name],
            "相关公司": [],
            "关键词": [industry_name, "政策", impact_type],
            "政策时效性": random.choice(["长期", "中期", "短期"]),
            "实施范围": random.choice(["全国", "试点"]),
            "预期效果": "促进行业规范发展",
            "市场反应预测": random.choice(["积极", "中性", "消极"]),
            "新闻来源": random.choice(["政府官网", "财经媒体", "行业网站"])
        }

    def _random_datetime(self) -> str:
        """生成随机时间（最近一年内）"""
        end = datetime.now()
        start = end - timedelta(days=365)
        random_time = start + timedelta(
            seconds=random.randint(0, int((end - start).total_seconds()))
        )
        return random_time.strftime("%Y-%m-%d %H:%M:%S")