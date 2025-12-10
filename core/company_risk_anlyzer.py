# company_risk_analyzer.py
import os
from openai import OpenAI



class CompanyRiskAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    def analyze_company_risk(self, company_name, custom_event=None):
        """
        分析公司风险
        Args:
            company_name: 公司名称
            custom_event: 用户输入的特定风险事件（可选）
        """
        # 获取公司信息
        company_info = self._get_company_info(company_name)

        # 构建提示词
        prompt = self._build_risk_prompt(company_info, custom_event)

        # 调用LLM
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是金融风控专家，专门分析公司风险。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        # 解析结果
        result = json.loads(response.choices[0].message.content)

        # 添加处置建议
        result["处置建议"] = self._generate_advice(result)

        return result

    def _build_risk_prompt(self, company_info, custom_event):
        """构建风险分析提示词"""
        base_info = f"""
        公司名称：{company_info['name']}
        所属行业：{company_info['industry']}
        股票代码：{company_info['stock_code']}
        市值：{company_info['market_cap']}亿元
        负债率：{company_info['debt_ratio']:.1%}
        利润增长率：{company_info['profit_growth']:.1%}
        历史风险评分：{company_info['risk_score']:.1f}/1.0
        """

        # 风险事件
        events_text = ""
        if company_info.get('risk_events'):
            events_text = "\n近期风险事件：\n"
            for event in company_info['risk_events'][:5]:  # 取最近5条
                events_text += f"- {event['title']}（{event['date']}）\n"
                events_text += f"  类型：{event['risk_type']}，严重程度：{event['severity']}\n"

        # 财务趋势
        financial_text = ""
        if company_info.get('financial_trend'):
            trend = company_info['financial_trend']
            financial_text = f"""
            财务趋势：
            - 营收：{trend['revenue']}亿元（最近季度）
            - 营收变化：{trend['revenue_change']:.1%}
            - 净利润：{trend['profit']}亿元
            - 债务：{trend['debt']}亿元
            """

        # 自定义事件
        custom_event_text = f"\n用户关注事件：{custom_event}\n" if custom_event else ""

        prompt = f"""
        请基于以下信息，分析{company_info['name']}的公司风险：

        {base_info}{events_text}{financial_text}{custom_event_text}

        请从以下维度分析，并以JSON格式返回：
        1. 综合风险等级（高/中/低）
        2. 风险得分（0-100，越高风险越大）
        3. 主要风险类型（财务风险/经营风险/政策风险/市场风险/其他）
        4. 风险传导路径（风险如何影响公司业务）
        5. 对股价的潜在影响（-30%至+30%）
        6. 对债券评级的影响（上调/维持/下调）
        7. 紧急程度（立即处置/近期关注/常规监控）
        8. 同类公司风险对比（风险是否普遍）
        9. 风险概率（0-100%）
        10. 风险影响程度（0-100%）

        输出示例：
        {{
            "综合风险等级": "中",
            "风险得分": 65,
            "主要风险类型": ["财务风险", "政策风险"],
            "风险传导路径": "政策收紧 → 产品降价 → 利润下降 → 偿债能力减弱",
            "股价潜在影响": "-15%",
            "债券评级影响": "可能下调",
            "紧急程度": "近期关注",
            "同类公司风险对比": "高于行业平均",
            "风险概率": 60,
            "风险影响程度": 75,
            "风险分析依据": "详细分析..."
        }}
        """
        return prompt

    def _generate_advice(self, risk_result):
        """生成处置建议"""
        prompt = f"""
        基于以下风险分析结果，为金融机构提供处置建议：

        {json.dumps(risk_result, ensure_ascii=False)}

        请提供具体的、可操作的处置建议，包括：
        1. 立即行动（24小时内）
        2. 短期策略（1周内）
        3. 中长期调整
        4. 监控指标
        5. 建议减仓比例（如有持仓）

        以风控总监的口吻，用清晰条目回答。
        """

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    def _get_company_info(self, company_name):
        """获取公司信息"""
        from company_data import generate_company_data
        data = generate_company_data()

        # 过滤该公司的风险事件
        company_events = [
            e for e in data['risk_events']
            if e['company'] == company_name
        ]

        # 获取财务趋势
        financial_trend = data['financials'].get(company_name, {})

        company_base = data['companies'].get(company_name, {})

        return {
            "name": company_name,
            "industry": company_base.get('industry', ''),
            "stock_code": company_base.get('stock_code', ''),
            "market_cap": company_base.get('market_cap', 0),
            "debt_ratio": company_base.get('debt_ratio', 0),
            "profit_growth": company_base.get('profit_growth', 0),
            "risk_score": company_base.get('risk_score', 0),
            "risk_events": company_events,
            "financial_trend": financial_trend
        }
