# sentiment_analyzer.py
import os
import json
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class FinancialSentimentAnalyzer:
    """金融舆情分析器"""

    def __init__(self, api_key=None):
        """初始化分析器"""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

        print("✅ 舆情分析器初始化成功")

    def analyze_industry_sentiment(self, industry_name: str, news_content: str) -> Dict:
        """
        分析行业景气度（场景1）

        Args:
            industry_name: 行业名称
            news_content: 舆情内容

        Returns:
            行业景气度分析结果
        """
        prompt = f"""
请分析以下关于{industry_name}行业的舆情信息，并提供专业分析：

**舆情内容：**
{news_content}

请从以下维度进行分析，并以JSON格式返回：

1. **政策影响分析**
   - 政策性质：利好/利空/中性
   - 影响程度：高/中/低
   - 具体影响：对行业的直接影响

2. **景气度判断**
   - 景气度评级：高涨/良好/一般/低迷
   - 景气度得分：0-100分
   - 趋势判断：上升/持平/下降

3. **关联影响**
   - 受益行业：哪些关联行业会受益
   - 受损行业：哪些关联行业会受损
   - 产业链影响：对上下游的影响

4. **投资建议**
   - 行业配置：建议增加/减少/维持
   - 配置比例：建议持仓比例（%）
   - 关注板块：具体关注哪些细分板块

5. **监控指标**
   - 关键指标：需要重点监控的指标
   - 风险提示：主要风险点
   - 时间窗口：影响的持续时间

请确保分析专业、客观，符合金融分析的标准。
"""

        response = self._call_llm(prompt, "你是资深的金融行业分析师")

        # 解析结果
        result = self._parse_json_response(response)

        # 添加基础信息
        result["行业名称"] = industry_name
        result["分析类型"] = "行业景气度分析"
        result["舆情摘要"] = news_content[:200] + "..." if len(news_content) > 200 else news_content

        return result

    def analyze_company_risk(self, company_name: str, news_content: str,
                             company_info: Dict = None) -> Dict:
        """
        分析公司风险（场景2）

        Args:
            company_name: 公司名称
            news_content: 舆情内容
            company_info: 公司基本信息（可选）

        Returns:
            公司风险分析结果
        """
        # 准备公司信息文本
        company_info_text = ""
        if company_info:
            company_info_text = f"""
公司基本信息：
- 所属行业：{company_info.get('所属行业', '未知')}
- 市值：{company_info.get('总市值', '未知')}亿元
- 负债率：{company_info.get('资产负债率', '未知'):.1%}
- 风险评分：{company_info.get('风险评分', '未知')}/100
"""

        prompt = f"""
请分析以下关于{company_name}的舆情信息，评估其风险状况：

**舆情内容：**
{news_content}

{company_info_text}

请从以下维度进行分析，并以JSON格式返回：

1. **风险识别**
   - 风险类型：财务风险/经营风险/合规风险/市场风险/其他
   - 风险事件：具体是什么风险事件
   - 严重程度：高/中/低

2. **影响评估**
   - 对股价影响：重大负面/轻微负面/中性/轻微正面
   - 对债券评级：可能下调/观察名单/维持不变
   - 财务影响：估计影响金额或比例
   - 经营影响：对业务运营的影响

3. **传导路径**
   - 直接影响：事件的直接后果
   - 间接影响：可能引发的连锁反应
   - 行业影响：是否会波及同行业公司

4. **处置建议**
   - 紧急程度：立即处置/近期关注/常规监控
   - 具体措施：建议采取的行动
   - 减仓建议：如有持仓，建议减持比例
   - 对冲策略：风险对冲建议

5. **预警指标**
   - 监控指标：需要重点监控的指标
   - 预警信号：后续可能出现的危险信号
   - 时间窗口：风险爆发的时间预期

请确保分析专业、客观，符合金融风控的标准。
"""

        response = self._call_llm(prompt, "你是经验丰富的金融风控专家")

        # 解析结果
        result = self._parse_json_response(response)

        # 添加基础信息
        result["公司名称"] = company_name
        result["分析类型"] = "公司风险分析"
        result["舆情摘要"] = news_content[:200] + "..." if len(news_content) > 200 else news_content

        if company_info:
            result["公司基本信息"] = {
                "所属行业": company_info.get("所属行业"),
                "市值": company_info.get("总市值"),
                "负债率": company_info.get("资产负债率")
            }

        return result

    def batch_analyze_news(self, news_list: List[Dict]) -> List[Dict]:
        """
        批量分析舆情新闻

        Args:
            news_list: 舆情新闻列表，每个元素包含：
                - title: 标题
                - content: 内容
                - source: 来源
                - publish_time: 发布时间
                - related_industry: 相关行业
                - related_company: 相关公司

        Returns:
            分析结果列表
        """
        results = []

        print(f"开始批量分析 {len(news_list)} 条舆情...")

        for i, news in enumerate(news_list):
            print(f"  分析第 {i + 1} 条: {news.get('title', '无标题')[:50]}...")

            analysis_result = {}

            # 根据新闻类型选择分析方式
            if news.get('related_company'):
                # 公司风险分析
                analysis_result = self.analyze_company_risk(
                    company_name=news['related_company'],
                    news_content=news['content'],
                    company_info=news.get('company_info')
                )
            elif news.get('related_industry'):
                # 行业景气度分析
                analysis_result = self.analyze_industry_sentiment(
                    industry_name=news['related_industry'],
                    news_content=news['content']
                )
            else:
                # 通用分析
                analysis_result = self._general_analysis(news)

            # 添加新闻元数据
            analysis_result["新闻标题"] = news.get('title', '')
            analysis_result["新闻来源"] = news.get('source', '')
            analysis_result["发布时间"] = news.get('publish_time', '')

            results.append(analysis_result)

        print("✅ 批量分析完成")
        return results

    def _general_analysis(self, news: Dict) -> Dict:
        """通用舆情分析"""
        prompt = f"""
请分析以下金融舆情：

标题：{news.get('title', '无标题')}
内容：{news.get('content', '无内容')}

请分析：
1. 舆情性质：正面/负面/中性
2. 影响范围：个体/行业/系统性
3. 紧急程度：高/中/低
4. 关键要点：总结3个关键点
5. 建议行动：简要建议

以JSON格式返回。
"""

        response = self._call_llm(prompt, "你是金融舆情分析师")
        return self._parse_json_response(response)

    def generate_investment_suggestions(self, analysis_results: List[Dict],
                                        portfolio_info: Dict = None) -> Dict:
        """
        生成投资建议（基于多个分析结果）

        Args:
            analysis_results: 多个分析结果
            portfolio_info: 投资组合信息（可选）

        Returns:
            综合投资建议
        """
        # 准备分析摘要
        analysis_summary = ""
        for i, result in enumerate(analysis_results[:5]):  # 最多取5条
            analysis_summary += f"{i + 1}. {result.get('分析类型', '未知')} - "
            if '行业名称' in result:
                analysis_summary += f"行业：{result['行业名称']} - "
            if '公司名称' in result:
                analysis_summary += f"公司：{result['公司名称']} - "
            if '景气度评级' in result:
                analysis_summary += f"景气度：{result['景气度评级']}\n"
            elif '严重程度' in result:
                analysis_summary += f"风险：{result['严重程度']}\n"
            else:
                analysis_summary += "\n"

        prompt = f"""
基于以下舆情分析结果，生成综合投资建议：

**分析结果摘要：**
{analysis_summary}

**当前投资组合：**
{json.dumps(portfolio_info, ensure_ascii=False, indent=2) if portfolio_info else "未提供组合信息"}

请提供以下建议，以JSON格式返回：

1. **整体策略**
   - 市场观点：乐观/谨慎/中性
   - 风险偏好：建议的风险承受水平
   - 仓位建议：建议整体仓位（%）

2. **行业配置建议**
   - 推荐增持的行业及理由
   - 建议减持的行业及理由
   - 建议关注的行业

3. **个股操作建议**
   - 推荐关注的个股（如有）
   - 建议回避的个股（如有）
   - 仓位调整建议

4. **风险控制**
   - 主要风险点
   - 止损建议
   - 对冲策略

5. **监控重点**
   - 需要重点监控的指标
   - 关键时间节点
   - 预警信号

请确保建议具体、可操作。
"""

        response = self._call_llm(prompt, "你是资深投资顾问")
        return self._parse_json_response(response)

    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """调用大模型"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            # 返回模拟数据避免中断
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """API失败时的备选响应"""
        if "行业" in prompt:
            return json.dumps({
                "政策影响分析": {
                    "政策性质": "利好",
                    "影响程度": "中",
                    "具体影响": "政策支持行业发展"
                },
                "景气度判断": {
                    "景气度评级": "良好",
                    "景气度得分": 75,
                    "趋势判断": "上升"
                },
                "投资建议": {
                    "行业配置": "建议增加",
                    "配置比例": "15%",
                    "关注板块": ["新能源汽车", "光伏"]
                }
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "风险识别": {
                    "风险类型": "财务风险",
                    "风险事件": "债务压力",
                    "严重程度": "中"
                },
                "处置建议": {
                    "紧急程度": "近期关注",
                    "具体措施": "加强监控，关注偿债能力变化",
                    "减仓建议": "如有持仓，建议减持5-10%"
                }
            }, ensure_ascii=False)

    def _parse_json_response(self, response: str) -> Dict:
        """解析JSON响应"""
        try:
            import re
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # 尝试直接解析
                return json.loads(response)
        except:
            # 如果解析失败，返回原始文本
            return {"原始响应": response, "解析状态": "失败"}