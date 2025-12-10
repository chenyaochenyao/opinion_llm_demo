# industry_analyzer.py
import os
from openai import OpenAI
import json

import os
from openai import OpenAI



class IndustryAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    def analyze_industry(self, industry_name, custom_policy=None):
        """
        分析行业景气度
        Args:
            industry_name: 行业名称
            custom_policy: 用户输入的政策文本（可选）
        """
        # 获取行业基础信息
        industry_info = self._get_industry_info(industry_name)

        # 构建分析提示词
        prompt = self._build_industry_prompt(industry_info, custom_policy)

        # 调用LLM
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是金融行业分析师，专门分析行业景气度。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        # 解析结果
        result = json.loads(response.choices[0].message.content)
        return result

    def _build_industry_prompt(self, industry_info, custom_policy):
        """构建行业分析提示词"""
        base_info = f"""
        行业名称：{industry_info['name']}
        行业描述：{industry_info['description']}
        上游产业：{', '.join(industry_info.get('upstream', []))}
        下游产业：{', '.join(industry_info.get('downstream', []))}
        竞争对手：{', '.join(industry_info.get('competitors', []))}
        历史增速：{industry_info.get('growth_rate', 0):.1%}
        """

        # 添加政策信息
        policy_text = ""
        if industry_info.get('policies'):
            policy_text = "\n近期政策：\n"
            for policy in industry_info['policies'][:3]:  # 取最近3条
                policy_text += f"- {policy['title']}（{policy['date']}）\n"

        # 自定义政策
        custom_policy_text = f"\n用户关注政策：{custom_policy}\n" if custom_policy else ""

        prompt = f"""
        请基于以下信息，分析{industry_info['name']}行业的景气度：

        {base_info}{policy_text}{custom_policy_text}

        请从以下维度分析，并以JSON格式返回：
        1. 景气度评级（高/中/低）
        2. 景气度得分（0-100分）
        3. 主要驱动因素（政策、技术、需求等）
        4. 主要风险因素（政策、竞争、技术等）
        5. 关联行业影响（哪些行业会受益/受损）
        6. 投资建议（强烈推荐/推荐/中性/谨慎/回避）
        7. 建议持仓比例（0-100%）
        8. 关键监控指标
        9. 3个月景气度预测（上升/持平/下降）

        输出示例：
        {{
            "景气度评级": "高",
            "景气度得分": 85,
            "主要驱动因素": ["政策支持", "技术突破", "需求增长"],
            "主要风险因素": ["原材料价格上涨", "政策变动", "竞争加剧"],
            "关联行业影响": {
        "受益行业": ["锂矿", "充电桩"],
                "受损行业": ["传统燃油车"]
            },
            "投资建议": "推荐",
            "建议持仓比例": 15,
            "关键监控指标": ["补贴政策", "锂电池价格", "渗透率"],
            "景气度预测": "上升",
            "分析依据": "详细分析理由..."
        }}
        """
        return prompt

    def _get_industry_info(self, industry_name):
        """获取行业信息（从数据库或仿真）"""
        # 这里从之前的数据生成函数获取
        from config.industry_data import generate_industry_data
        data = generate_industry_data()

        # 过滤该行业的政策新闻
        industry_policies = [
            p for p in data['policy_news']
            if p['industry'] == industry_name
        ]

        return {
            "name": industry_name,
            "description": data['industries'].get(industry_name, {}).get('description', ''),
            "upstream": data['industries'].get(industry_name, {}).get('upstream', []),
            "downstream": data['industries'].get(industry_name, {}).get('downstream', []),
            "competitors": data['industries'].get(industry_name, {}).get('competitors', []),
            "growth_rate": data['industries'].get(industry_name, {}).get('growth_rate', 0),
            "policies": industry_policies,
            "correlations": data['correlations'].get(industry_name, [])
        }