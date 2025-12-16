# sentiment_analyzer.py
import os
import json
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


class FinancialSentimentAnalyzer:
    """金融舆情分析器"""

    def __init__(self, api_key=None):
        """初始化分析器"""
        self.api_key = st.secrets["DEEPSEEK_API_KEY"]
        self.model = "deepseek-chat"

        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

        print("✅ 舆情分析器初始化成功")
        # self.api_key = st.secrets.get("GITEE_AI_API_KEY", "")
        # if not self.api_key:
        #     raise ValueError("请配置GITEE_AI_API_KEY（本地.env或云端Secrets）")
        #
        # self.client = OpenAI(
        #     api_key=self.api_key,
        #     base_url="https://ai.gitee.com/api/v1"
        # )
        # self.model = "fin-r1"
        # print("✅ fin-r1测试客户端初始化完成")

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
        请严格按照金融投资分析标准，对以下{industry_name}行业舆情进行多维度专业分析，最终输出可直接解析的JSON格式结果（无任何多余文字、注释）：

        **舆情内容：**
        {news_content}

        # 核心分析要求
        ## 1. 舆情属性精准识别（正面/负面/中性）
        - 舆情类型：从「行业政策/技术突破/市场需求/竞争格局/风险事件」中精准匹配（可多选，数组形式）
        - 舆情倾向：利好/利空/中性（需明确）
        - 影响强度：高/中/低（结合量化维度：政策落地力度/技术商业化进度/市场需求规模等）
        - 具体影响：基于舆情类型，量化描述对行业的直接影响（例如「新能源补贴政策落地，预计拉动行业年度销量增长15%-20%」）

        ## 2. 赛道景气度量化评分
        - 景气度评级：高涨/良好/一般/低迷（需与得分强绑定）
        - 景气度得分：0-100分（评分逻辑：政策支撑度30% + 技术成熟度25% + 市场需求25% + 产业链配套20%，需量化拆解）

        ## 3. 资产标的精准匹配与配置建议
        - 关联资产标的：
          - 股票：核心标的代码+名称（数组形式，例如["宁德时代 300750", "隆基绿能 601012"]），需标注匹配逻辑（如「新能源政策利好电池环节龙头」）
          - 债券：核心标的类型+名称（数组形式，例如["新能源产业债AAA级", "光伏企业中期票据"]），需标注匹配逻辑
        - 配置调整建议：
          - 行业配置策略：超配/标配/低配/规避（需结合景气度得分）
          - 标的调整方向：增持/减持/持有/清仓（分股票/债券维度说明）
          - 调整幅度建议：量化区间（例如「新能源股票超配比例提升5%-8%，新能源债券标配维持不变」）
          - 风险收益比：潜在收益空间（量化区间）+ 下行风险（量化区间）+ 核心逻辑（例如「潜在收益20%-30%，下行风险10%以内，核心逻辑为政策红利释放+需求增长」）

        ## 4. 多行业联动与产业链影响（适配分散投资策略）
        - 受益行业：关联受益行业列表（数组形式），标注受益逻辑（例如["储能行业：新能源装机增长带动储能需求"]）
        - 受损行业：关联受损行业列表（数组形式），标注受损逻辑（例如["传统火电行业：新能源替代加速导致装机量下滑"]）
        - 产业链分环节影响（需量化、具体）：
          - 上游：原材料/核心零部件/基础资源的价格变动、供需变化（例如「锂矿：需求增长预计推动价格上涨8%-10%」）
          - 中游：生产制造/加工组装/设备供应的产能利用率、利润率变化（例如「电池制造：产能利用率提升至90%，利润率提升2-3个百分点」）
          - 下游：终端应用/分销渠道/消费市场的需求规模、渗透率变化（例如「新能源汽车终端：政策补贴带动需求增长15%-20%，渗透率提升至35%」）

        ## 5. 多行业并行监测适配（动态调整策略支撑）
        - 跨行业替代/互补关系：列出与{industry_name}行业有替代/互补关系的行业（数组形式），标注对分散投资的影响（例如["光伏行业与风电行业：互补关系，分散配置可降低政策波动风险"]）
        - 风险提示：分行业/标的维度的核心风险点（数组形式，例如["新能源行业：政策退坡风险；宁德时代：原材料价格上涨风险"]）
        - 时间窗口：舆情影响的持续时间（量化，例如「6个月内持续影响，3个月为核心窗口期」）

        # 输出格式强制要求
        1. 仅返回JSON字符串，无任何前置/后置文字、解释、换行；
        2. 所有列表类字段（受益行业、关联资产标的等）均以数组形式返回；
        3. 量化维度需标注具体数值/区间，禁止模糊表述；
        4. 匹配逻辑、调整依据需简洁且符合金融投资逻辑；
        5. JSON字段命名清晰（如下示例框架），层级结构明确：

        {{
          "舆情属性": {{
            "舆情类型": [],
            "舆情倾向": "",
            "影响强度": "",
            "具体影响": ""
          }},
          "景气度分析": {{
            "景气度评级": "",
            "景气度得分": 0,
          }},
          "资产标的与配置": {{
            "关联资产标的": {{
              "股票": [],
              "债券": []
            }},
            "配置调整建议": {{
              "行业配置策略": "",
              "标的调整方向": {{
                "股票": "",
                "债券": ""
              }},
              "调整幅度建议": "",
              "风险收益比": ""
            }}
          }},
          "产业链与跨行业影响": {{
            "受益行业": [],
            "受损行业": [],
            "产业链影响": {{
              "上游": "",
              "中游": "",
              "下游": ""
            }},
            "跨行业关系": []
          }},
          "动态调整支撑": {{
            "风险提示": [],
            "时间窗口": ""
          }}
        }}
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
        # 任务指令：债券发行人/非标融资主体负面舆情风险量化分析
        请基于金融风控标准，分析以下关于**{company_name}**的舆情信息，重点识别债务违约、评级下调等负面风险，量化严重等级并输出可落地的处置方案。输出结果为**纯净JSON格式**，无任何前置、后置文字或注释。

        ## 基础输入信息
        **舆情内容：**
        {news_content}

        **企业基础信息：**
        {company_info_text}

        ## 核心分析维度（严格按以下结构输出）
        ### 1. 负面舆情精准识别（强制枚举风险类型）
        - **风险类型**：从以下枚举值中精准匹配（可多选，数组格式）：债务逾期、担保违约、高管失联/被查、评级下调/展望负面、债券展期/回售违约、非标融资违约、流动性危机、资产查封冻结、重大诉讼仲裁、其他风险
        - **风险事件详情**：精炼描述事件核心要素（时间、地点、涉及金额、相关主体、事件进展），量化表述（例如"2025年12月发行人发生5亿元债券逾期，涉及3家商业银行债权"）
        - **严重等级**：高/中/低（判定标准：高=直接触发违约或丧失偿债能力；中=影响偿债能力但未实质性违约；低=轻微负面，不影响偿债能力）
        - **风险定性**：实质性违约风险/潜在违约风险/舆情扰动风险

        ### 2. 影响范围与传导路径判定
        - **影响范围**：单一主体/关联企业/全行业（需明确关联企业名单，例如"发行人子公司A、担保人B；行业层面仅影响区域城投平台"）
        - **直接影响对象**：明确受影响的债券品种/非标产品（数组格式，例如["25XX债01（代码123XXX）", "XX信托非标融资产品"]）
        - **传导路径分析**：
          - 内部传导：对发行人现金流、融资能力、核心业务的具体影响（量化数据支撑）
          - 外部传导：对关联企业、担保人、上下游供应链、区域金融生态的连锁反应
          - 市场传导：对债券二级市场价格、同行业信用利差的影响预判

        ### 3. 风险量化评估（金融风控视角）
        - **损失预估**：潜在损失金额区间/占发行人净资产比例（例如"潜在损失3-5亿元，占净资产比例8%-12%"）
        - **市场影响程度**：债券价格跌幅预判（例如"预计债券价格下跌15%-20%"）/ 融资成本上升幅度（例如"新增融资成本上浮300-500BP"）

        ### 4. 风险处置建议（可落地、分优先级）
        - **紧急处置等级**：立即处置/近期关注（7日内）/常规监控（30日内）
        - **分场景处置措施**：
          - 持仓机构操作建议：减持比例（例如"减持持仓规模的50%-80%"）/ 止损价位（例如"债券价格跌破80元时全额止损"）/ 持有观望条件
          - 风险对冲策略：适用场景（如信用违约互换CDS）/ 对冲工具选择 / 对冲比例建议
          - 投后管理措施：尽调重点（如核查发行人货币资金真实性）/ 沟通对象（如发行人财务总监、担保人）/ 信息披露跟踪要求
        - **风险缓释手段**：担保人代偿能力核查 / 抵质押物处置可行性 / 政府救助可能性分析（针对城投类主体）

      

        ## 输出格式强制要求
        1. 必须返回标准JSON，字段命名与上述维度严格对应，无嵌套层级冗余；
        2. 所有量化指标需提供具体数值/区间，禁止模糊表述（如"较大影响"需替换为"影响金额5-8亿元"）；
        3. 风险类型、监控指标等列表类字段，统一用数组格式输出；
        4. 分析逻辑需符合债券/非标风控实务，避免理论化表述；
        5. 禁止输出任何JSON以外的内容（包括"以下是分析结果"等过渡语句）。

        ## JSON输出框架（严格遵循，不得修改字段名称）
        {{
          "负面舆情识别": {{
            "风险类型": [],
            "风险事件详情": "",
            "严重等级": "",
            "风险定性": ""
          }},
          "影响范围与传导路径": {{
            "影响范围": "",
            "直接影响对象": [],
            "传导路径分析": {{
              "内部传导": "",
              "外部传导": "",
              "市场传导": ""
            }}
          }},
          "风险量化评估": {{
            "损失预估": "",
            "市场影响程度": ""
          }},
          "风险处置建议": {{
            "紧急处置等级": "",
            "分场景处置措施": {{
              "持仓机构操作建议": "",
              "风险对冲策略": "",
              "投后管理措施": ""
            }},
            "风险缓释手段": ""
          }}
        }}
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

以JSON格式返回。请用中文生成。
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

请确保建议具体、可操作。请用中文生成。
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
                # model="deepseek-chat",
                model=self.model,
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