# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import sys
import os

# 获取项目根目录（frontend的上层目录）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将根目录加入sys.path
sys.path.append(ROOT_DIR)
#
# # 导入分析模块
# from core.industry_analyzer  import IndustryAnalyzer
# from core.company_risk_anlyzer import  CompanyRiskAnalyzer
#
# # 页面配置
# st.set_page_config(
#     page_title="金融智能分析系统",
#     page_icon="📊",
#     layout="wide"
# )
#
#
# # 初始化分析器
# @st.cache_resource
# def init_industry_analyzer():
#     return IndustryAnalyzer()
#
#
# @st.cache_resource
# def init_risk_analyzer():
#     return CompanyRiskAnalyzer()
#
#
# # 加载数据
# @st.cache_data
# def load_industry_data():
#     from config.industry_data import generate_industry_data
#     return generate_industry_data()
#
#
# @st.cache_data
# def load_company_data():
#     from config.company_data import generate_company_data
#     return generate_company_data()
#
#
# # 主应用
# st.title("🤖 金融智能分析系统")
# st.markdown("基于大语言模型的行业景气度与公司风险分析")
#
# # 侧边栏导航
# with st.sidebar:
#     st.header("分析场景")
#     analysis_mode = st.radio(
#         "选择分析场景",
#         ["🏢 行业景气度分析", "🏢 公司风险分析", "📊 对比分析看板"]
#     )
#
#     st.divider()
#     st.header("配置选项")
#
#     # 行业选择
#     if analysis_mode == "🏢 行业景气度分析":
#         industry_options = ["新能源", "医药", "人工智能", "半导体", "金融", "房地产"]
#         selected_industry = st.selectbox("选择行业", industry_options)
#
#         # 自定义政策输入
#         st.subheader("自定义政策分析")
#         custom_policy = st.text_area(
#             "输入关注的政策/新闻",
#             height=100,
#             placeholder="例如：国家出台新能源汽车购置税减免政策延续三年..."
#         )
#
#         analyze_industry_btn = st.button("🚀 分析行业景气度", type="primary", use_container_width=True)
#
#     elif analysis_mode == "🏢 公司风险分析":
#         # 公司选择
#         company_options = ["新能源科技", "医药集团", "AI智能", "半导体制造", "银行股份"]
#         selected_company = st.selectbox("选择公司", company_options)
#
#         # 自定义风险事件
#         st.subheader("自定义风险事件")
#         custom_event = st.text_area(
#             "输入关注的风险事件",
#             height=100,
#             placeholder="例如：公司公告大股东减持5%股份..."
#         )
#
#         analyze_company_btn = st.button("🔍 分析公司风险", type="primary", use_container_width=True)
#
#     else:
#         st.info("查看行业与公司对比分析")
#
# # 主内容区
# if analysis_mode == "🏢 行业景气度分析":
#     st.header(f"📈 {selected_industry}行业景气度分析")
#
#     col1, col2 = st.columns([2, 1])
#
#     with col1:
#         # 显示行业基本信息
#         industry_data = load_industry_data()
#         industry_info = industry_data['industries'].get(selected_industry, {})
#
#         if industry_info:
#             st.subheader("行业概览")
#             st.write(f"**描述**: {industry_info.get('description', '')}")
#
#             # 关键指标卡片
#             metric_cols = st.columns(3)
#             with metric_cols[0]:
#                 st.metric("预期增速", f"{industry_info.get('growth_rate', 0):.1%}")
#             with metric_cols[1]:
#                 st.metric("上游产业", len(industry_info.get('upstream', [])))
#             with metric_cols[2]:
#                 st.metric("下游产业", len(industry_info.get('downstream', [])))
#
#         # 政策新闻
#         st.subheader("近期政策")
#         industry_policies = [p for p in industry_data['policy_news'] if p['industry'] == selected_industry]
#
#         for policy in industry_policies[:3]:
#             emoji = "🟢" if policy['impact'] == 'positive' else "🔴" if policy['impact'] == 'negative' else "🟡"
#             with st.expander(f"{emoji} {policy['title']}"):
#                 st.write(policy['content'])
#                 st.caption(f"来源：{policy['source']} | 日期：{policy['date']}")
#
#     with col2:
#         st.subheader("关联行业")
#         correlations = industry_data['correlations'].get(selected_industry, [])
#
#         if correlations:
#             st.write("紧密关联的行业：")
#             for corr in correlations:
#                 st.markdown(f"- {corr}")
#
#         # 行业热度图（仿真）
#         st.subheader("市场热度")
#         heat_data = {
#             "新能源": 85,
#             "医药": 60,
#             "人工智能": 90,
#             "半导体": 75,
#             "金融": 50,
#             "房地产": 40
#         }
#
#         # 创建雷达图
#         fig = go.Figure(data=go.Scatterpolar(
#             r=[heat_data.get(ind, 0) for ind in ["新能源", "医药", "人工智能", "半导体", "金融", "房地产"]],
#             theta=["新能源", "医药", "人工智能", "半导体", "金融", "房地产"],
#             fill='toself'
#         ))
#
#         fig.update_layout(
#             polar=dict(
#                 radialaxis=dict(
#                     visible=True,
#                     range=[0, 100]
#                 )),
#             showlegend=False,
#             height=300
#         )
#
#         st.plotly_chart(fig, use_container_width=True)
#
#     # 分析按钮触发
#     if analyze_industry_btn:
#         st.divider()
#         st.subheader("🤖 AI智能分析结果")
#
#         with st.spinner(f"正在分析{selected_industry}行业景气度..."):
#             analyzer = init_industry_analyzer()
#             result = analyzer.analyze_industry(selected_industry, custom_policy)
#
#             # 显示分析结果
#             if result:
#                 # 景气度评级卡片
#                 col_a, col_b, col_c = st.columns(3)
#
#                 with col_a:
#                     rating = result.get("景气度评级", "未知")
#                     color = "green" if rating in ["高", "中高"] else "orange" if rating == "中" else "red"
#                     st.metric("景气度评级", rating, delta=rating, delta_color="normal")
#
#                 with col_b:
#                     score = result.get("景气度得分", 0)
#                     st.metric("景气度得分", f"{score}/100")
#
#                 with col_c:
#                     advice = result.get("投资建议", "中性")
#                     st.metric("投资建议", advice)
#
#                 # 详细分析
#                 st.subheader("详细分析")
#
#                 tab1, tab2, tab3, tab4 = st.tabs(["驱动因素", "风险因素", "关联影响", "投资策略"])
#
#                 with tab1:
#                     drivers = result.get("主要驱动因素", [])
#                     if drivers:
#                         for driver in drivers:
#                             st.markdown(f"✅ {driver}")
#                     else:
#                         st.info("暂无驱动因素信息")
#
#                 with tab2:
#                     risks = result.get("主要风险因素", [])
#                     if risks:
#                         for risk in risks:
#                             st.markdown(f"⚠️ {risk}")
#                     else:
#                         st.info("暂无风险因素信息")
#
#                 with tab3:
#                     impacts = result.get("关联行业影响", {})
#                     col_benefit, col_harm = st.columns(2)
#
#                     with col_benefit:
#                         st.write("**受益行业**")
#                         for industry in impacts.get("受益行业", []):
#                             st.markdown(f"📈 {industry}")
#
#                     with col_harm:
#                         st.write("**受损行业**")
#                         for industry in impacts.get("受损行业", []):
#                             st.markdown(f"📉 {industry}")
#
#                 with tab4:
#                     col_rec, col_mon = st.columns(2)
#
#                     with col_rec:
#                         st.write("**投资建议**")
#                         st.markdown(f"**持仓比例**: {result.get('建议持仓比例', 0)}%")
#                         st.markdown(f"**景气预测**: {result.get('景气度预测', '未知')}")
#
#                     with col_mon:
#                         st.write("**监控指标**")
#                         for indicator in result.get("关键监控指标", []):
#                             st.markdown(f"📊 {indicator}")
#
#                 # 显示原始JSON（可折叠）
#                 with st.expander("查看原始分析数据"):
#                     st.json(result)
#
# elif analysis_mode == "🏢 公司风险分析":
#     st.header(f"⚠️ {selected_company}风险分析")
#
#     # 公司基本信息
#     company_data = load_company_data()
#     company_info = company_data['companies'].get(selected_company, {})
#
#     if company_info:
#         col1, col2, col3, col4 = st.columns(4)
#
#         with col1:
#             st.metric("市值", f"{company_info.get('market_cap', 0)}亿元")
#
#         with col2:
#             st.metric("负债率", f"{company_info.get('debt_ratio', 0):.1%}")
#
#         with col3:
#             growth = company_info.get('profit_growth', 0)
#             delta = f"{growth:+.1%}" if growth else None
#             st.metric("利润增长", f"{growth:.1%}", delta=delta)
#
#         with col4:
#             risk_score = company_info.get('risk_score', 0)
#             st.metric("风险评分", f"{risk_score:.1f}/1.0")
#
#     # 风险事件列表
#     st.subheader("近期风险事件")
#     company_events = [e for e in company_data['risk_events'] if e['company'] == selected_company]
#
#     if company_events:
#         for event in company_events[:3]:  # 显示最近3条
#             severity_color = {
#                 "high": "🔴",
#                 "medium": "🟡",
#                 "low": "🟢"
#             }.get(event.get('severity', 'medium'), '⚪')
#
#             with st.expander(f"{severity_color} {event['title']}"):
#                 st.write(event['content'])
#                 st.caption(f"风险类型：{event['risk_type']} | 日期：{event['date']}")
#     else:
#         st.info("近期无重大风险事件")
#
#     # 财务趋势图（仿真）
#     st.subheader("财务趋势")
#     financials = company_data['financials'].get(selected_company, {})
#
#     if financials:
#         # 创建趋势图
#         quarters = ["Q3-2023", "Q4-2023", "Q1-2024", "Q2-2024"]
#
#         fig = go.Figure()
#
#         if 'revenue' in financials:
#             fig.add_trace(go.Scatter(
#                 x=quarters,
#                 y=financials['revenue'],
#                 mode='lines+markers',
#                 name='营收（亿元）',
#                 line=dict(color='blue', width=2)
#             ))
#
#         if 'profit' in financials:
#             fig.add_trace(go.Scatter(
#                 x=quarters,
#                 y=financials['profit'],
#                 mode='lines+markers',
#                 name='净利润（亿元）',
#                 line=dict(color='green', width=2)
#             ))
#
#         fig.update_layout(
#             title="季度财务表现",
#             xaxis_title="季度",
#             yaxis_title="金额（亿元）",
#             height=300
#         )
#
#         st.plotly_chart(fig, use_container_width=True)
#
#     # 分析按钮触发
#     if analyze_company_btn:
#         st.divider()
#         st.subheader("🤖 AI风险分析结果")
#
#         with st.spinner(f"正在分析{selected_company}风险状况..."):
#             analyzer = init_risk_analyzer()
#             result = analyzer.analyze_company_risk(selected_company, custom_event)
#
#             if result:
#                 # 风险等级展示
#                 risk_level = result.get("综合风险等级", "未知")
#                 risk_score = result.get("风险得分", 0)
#
#                 # 创建风险仪表盘
#                 col_a, col_b, col_c = st.columns(3)
#
#                 with col_a:
#                     # 风险等级颜色
#                     color = "red" if risk_level == "高" else "orange" if risk_level == "中" else "green"
#                     st.metric("综合风险等级", risk_level, delta_color="inverse")
#
#                 with col_b:
#                     st.metric("风险得分", f"{risk_score}/100")
#
#                 with col_c:
#                     urgency = result.get("紧急程度", "常规监控")
#                     st.metric("紧急程度", urgency)
#
#                 # 风险矩阵图
#                 st.subheader("风险矩阵分析")
#
#                 # 创建风险矩阵
#                 risk_prob = result.get("风险概率", 50)
#                 risk_impact = result.get("风险影响程度", 50)
#
#                 # 可视化风险矩阵
#                 fig = go.Figure()
#
#                 # 添加区域
#                 fig.add_shape(
#                     type="rect",
#                     x0=0, y0=0, x1=50, y1=50,
#                     fillcolor="green",
#                     opacity=0.1,
#                     line_width=0
#                 )
#
#                 fig.add_shape(
#                     type="rect",
#                     x0=50, y0=0, x1=100, y1=50,
#                     fillcolor="yellow",
#                     opacity=0.1,
#                     line_width=0
#                 )
#
#                 fig.add_shape(
#                     type="rect",
#                     x0=0, y0=50, x1=50, y1=100,
#                     fillcolor="yellow",
#                     opacity=0.1,
#                     line_width=0
#                 )
#
#                 fig.add_shape(
#                     type="rect",
#                     x0=50, y0=50, x1=100, y1=100,
#                     fillcolor="red",
#                     opacity=0.1,
#                     line_width=0
#                 )
#
#                 # 添加风险点
#                 fig.add_trace(go.Scatter(
#                     x=[risk_prob],
#                     y=[risk_impact],
#                     mode='markers+text',
#                     marker=dict(size=20, color='red'),
#                     text=[selected_company],
#                     textposition="top center",
#                     name="当前风险位置"
#                 ))
#
#                 fig.update_layout(
#                     title="风险矩阵（概率 vs 影响）",
#                     xaxis_title="风险发生概率（%）",
#                     yaxis_title="风险影响程度（%）",
#                     xaxis_range=[0, 100],
#                     yaxis_range=[0, 100],
#                     height=400,
#                     showlegend=False
#                 )
#
#                 st.plotly_chart(fig, use_container_width=True)
#
#                 # 详细风险分析
#                 st.subheader("详细风险分析")
#
#                 tab1, tab2, tab3 = st.tabs(["风险类型", "影响分析", "处置建议"])
#
#                 with tab1:
#                     risk_types = result.get("主要风险类型", [])
#                     if risk_types:
#                         for rtype in risk_types:
#                             st.markdown(f"🔍 **{rtype}**")
#                     else:
#                         st.info("暂无风险类型信息")
#
#                     # 风险传导路径
#                     st.write("**风险传导路径**")
#                     st.info(result.get("风险传导路径", "未分析"))
#
#                 with tab2:
#                     col_impact, col_comparison = st.columns(2)
#
#                     with col_impact:
#                         st.write("**潜在影响**")
#                         st.markdown(f"**股价影响**: {result.get('股价潜在影响', '未知')}")
#                         st.markdown(f"**债券评级**: {result.get('债券评级影响', '未知')}")
#
#                     with col_comparison:
#                         st.write("**行业对比**")
#                         st.markdown(f"**同类对比**: {result.get('同类公司风险对比', '未知')}")
#
#                 with tab3:
#                     st.write("**AI处置建议**")
#                     advice = result.get("处置建议", "暂无建议")
#                     st.write(advice)
#
#                 # 显示原始数据
#                 with st.expander("查看原始分析数据"):
#                     st.json(result)
#
# else:
#     # 对比分析看板
#     st.header("📊 对比分析看板")
#
#     industry_data = load_industry_data()
#     company_data = load_company_data()
#
#     # 行业对比
#     st.subheader("行业景气度对比")
#
#     # 创建行业对比数据
#     industry_list = ["新能源", "医药", "人工智能", "半导体"]
#     growth_rates = [industry_data['industries'].get(ind, {}).get('growth_rate', 0) for ind in industry_list]
#     risk_scores = [company_data['companies'].get(f"{ind}科技", {}).get('risk_score', 0) for ind in industry_list]
#
#     # 创建对比图表
#     fig = go.Figure(data=[
#         go.Bar(name='预期增速', x=industry_list, y=growth_rates, yaxis='y', offsetgroup=1),
#         go.Bar(name='风险评分', x=industry_list, y=risk_scores, yaxis='y2', offsetgroup=2)
#     ])
#
#     fig.update_layout(
#         yaxis=dict(title="预期增速"),
#         yaxis2=dict(title="风险评分", overlaying='y', side='right'),
#         barmode='group',
#         height=400
#     )
#
#     st.plotly_chart(fig, use_container_width=True)
#
#     # 风险事件时间线
#     st.subheader("近期风险事件时间线")
#
#     # 获取所有风险事件
#     all_events = company_data['risk_events']
#
#     if all_events:
#         # 按日期排序
#         sorted_events = sorted(all_events, key=lambda x: x['date'], reverse=True)
#
#         # 显示时间线
#         for event in sorted_events[:5]:
#             severity_emoji = {
#                 "high": "🔴",
#                 "medium": "🟡",
#                 "low": "🟢"
#             }.get(event['severity'], '⚪')
#
#             st.markdown(f"**{event['date']}** {severity_emoji} **{event['company']}**")
#             st.markdown(f"`{event['risk_type']}` {event['title']}")
#             st.divider()
#
# # 页脚
# st.markdown("---")
# st.caption("演示系统 | 基于DeepSeek API | 数据为仿真生成 | 仅供学术演示使用")
#
# # 添加帮助信息
# with st.expander("💡 使用说明"):
#     st.markdown("""
#     ## 使用指南
#
#     ### 行业景气度分析
#     1. 选择要分析的行业（如新能源、医药等）
#     2. 可输入自定义政策进行分析
#     3. 点击"分析行业景气度"获取AI分析结果
#     4. 查看景气度评级、驱动因素、风险因素等
#
#     ### 公司风险分析
#     1. 选择要分析的公司
#     2. 可输入自定义风险事件
#     3. 点击"分析公司风险"获取AI分析结果
#     4. 查看风险等级、影响分析、处置建议等
#
#     ### 数据说明
#     - 行业数据：基于公开信息仿真生成
#     - 公司数据：基于公开财报和新闻仿真生成
#     - 分析结果：由DeepSeek大模型生成，仅供参考
#     """)


# app_with_generated_data.py
# import streamlit as st
# import json
# import os
# import pandas as pd
# import plotly.graph_objects as go
#
#
# # 加载生成的数据
# @st.cache_data
# def load_generated_data():
#     """加载生成的数据"""
#     data_dir = r"D:\project\opinion_llm_demo\core\generated_data"
#
#     data = {}
#
#     for filename in ["industries.json", "companies.json", "policies.json", "risk_events.json"]:
#         filepath = os.path.join(data_dir, filename)
#         if os.path.exists(filepath):
#             with open(filepath, "r", encoding="utf-8") as f:
#                 data[filename.replace(".json", "")] = json.load(f)
#         else:
#             st.warning(f"未找到数据文件: {filename}")
#             data[filename.replace(".json", "")] = []
#
#     return data
#
#
# # Streamlit应用
# st.set_page_config(
#     page_title="金融智能分析系统",
#     page_icon="📊",
#     layout="wide"
# )
#
# st.title("🤖 金融智能分析系统")
# st.markdown("> Hi,今天想了解哪些内容呢？")
#
# # 加载数据
# data = load_generated_data()
#
# # 侧边栏
# with st.sidebar:
#     st.header("分析功能")
#     analysis_mode = st.radio(
#         "选择分析模式",
#         ["数据概览", "行业分析", "公司分析", "风险监控", "政策分析"]
#     )
#
#     st.divider()
#     st.header("数据统计")
#
#     if data:
#         st.metric("行业数量", len(data.get("industries", [])))
#         st.metric("公司数量", len(data.get("companies", [])))
#         st.metric("政策数量", len(data.get("policies", [])))
#         st.metric("风险事件", len(data.get("risk_events", [])))
#
# # 主内容
# if not data.get("industries"):
#     st.error("未找到数据，请先生成数据！")
#     if st.button("生成演示数据"):
#         import quick_generator
#
#         quick_generator.quick_generate_data()
#         st.rerun()
# else:
#     if analysis_mode == "数据概览":
#         st.header("📊 数据概览")
#
#         # 行业分布
#         st.subheader("行业分布")
#         industries_df = pd.DataFrame(data["industries"])
#
#         if not industries_df.empty:
#             col1, col2 = st.columns(2)
#
#             with col1:
#                 # 预期增长率
#                 fig1 = go.Figure(data=[
#                     go.Bar(
#                         x=industries_df["行业名称"],
#                         y=industries_df["预期增长率"],
#                         text=[f"{x:.1%}" for x in industries_df["预期增长率"]],
#                         textposition="auto"
#                     )
#                 ])
#                 fig1.update_layout(title="行业预期增长率", height=400)
#                 st.plotly_chart(fig1, use_container_width=True)
#
#             with col2:
#                 # 市盈率区间
#                 fig2 = go.Figure()
#                 for _, row in industries_df.iterrows():
#                     fig2.add_trace(go.Box(
#                         name=row["行业名称"],
#                         q1=[row["市盈率区间"][0]],
#                         median=[(row["市盈率区间"][0] + row["市盈率区间"][1]) / 2],
#                         q3=[row["市盈率区间"][1]],
#                         lowerfence=[row["市盈率区间"][0]],
#                         upperfence=[row["市盈率区间"][1]]
#                     ))
#                 fig2.update_layout(title="行业市盈率区间", height=400)
#                 st.plotly_chart(fig2, use_container_width=True)
#
#         # 公司风险分布
#         st.subheader("公司风险分布")
#         companies_df = pd.DataFrame(data["companies"])
#
#         if not companies_df.empty:
#             # 风险评分分布
#             fig3 = go.Figure(data=[go.Histogram(x=companies_df["风险评分"], nbinsx=20)])
#             fig3.update_layout(
#                 title="公司风险评分分布",
#                 xaxis_title="风险评分",
#                 yaxis_title="公司数量",
#                 height=300
#             )
#             st.plotly_chart(fig3, use_container_width=True)
#
#             # 按行业分组
#             col1, col2 = st.columns(2)
#
#             with col1:
#                 st.dataframe(companies_df[["公司名称", "所属行业", "总市值", "风险评分"]].head(10))
#
#             with col2:
#                 industry_stats = companies_df.groupby("所属行业").agg({
#                     "总市值": "mean",
#                     "风险评分": "mean",
#                     "公司名称": "count"
#                 }).round(2)
#                 industry_stats.columns = ["平均市值(亿元)", "平均风险评分", "公司数量"]
#                 st.dataframe(industry_stats)
#
#     elif analysis_mode == "行业分析":
#         st.header("🏢 行业分析")
#
#         # 选择行业
#         industries = data["industries"]
#         industry_names = [ind["行业名称"] for ind in industries]
#         selected_industry = st.selectbox("选择行业", industry_names)
#
#         if selected_industry:
#             # 获取行业数据
#             industry_data = next((ind for ind in industries if ind["行业名称"] == selected_industry), None)
#
#             if industry_data:
#                 col1, col2 = st.columns([2, 1])
#
#                 with col1:
#                     st.subheader(f"{selected_industry}行业分析")
#
#                     # 关键指标
#                     metrics_cols = st.columns(3)
#                     with metrics_cols[0]:
#                         st.metric("预期增长率", f"{industry_data['预期增长率']:.1%}")
#                     with metrics_cols[1]:
#                         st.metric("行业周期", industry_data.get("行业周期", "未知"))
#                     with metrics_cols[2]:
#                         pe_range = industry_data.get("市盈率区间", [0, 0])
#                         st.metric("市盈率区间", f"{pe_range[0]}-{pe_range[1]}")
#
#                     # 增长驱动力
#                     st.markdown("#### 📈 增长驱动力")
#                     for driver in industry_data.get("增长驱动力", []):
#                         st.markdown(f"✅ {driver}")
#
#                     # 主要风险
#                     st.markdown("#### ⚠️ 主要风险")
#                     for risk in industry_data.get("主要风险", []):
#                         st.markdown(f"🔴 {risk}")
#
#                 with col2:
#                     # 相关公司
#                     st.subheader("相关公司")
#                     related_companies = [c for c in data["companies"] if c["所属行业"] == selected_industry]
#
#                     for company in related_companies[:5]:
#                         with st.expander(company["公司名称"]):
#                             st.markdown(f"**市值**: {company['总市值']}亿元")
#                             st.markdown(f"**风险评分**: {company['风险评分']}/100")
#
#                 # 相关政策
#                 st.subheader("📰 相关政策")
#                 related_policies = [p for p in data["policies"] if selected_industry in p.get("相关行业", [])]
#
#                 for policy in related_policies[:3]:
#                     impact = policy.get("影响类型", "中性")
#                     impact_color = {
#                         "利好": "🟢",
#                         "利空": "🔴",
#                         "中性": "🟡"
#                     }.get(impact, "⚪")
#
#                     with st.expander(f"{impact_color} {policy['标题']}"):
#                         st.write(policy["内容"])
#                         st.caption(f"发布时间: {policy.get('发布时间', '未知')}")
#
#     # 其他分析模式类似实现...
#
# st.markdown("---")
# st.caption("数据由大模型生成，仅供演示使用")


# main_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os

from core.sentiment_analyzer import FinancialSentimentAnalyzer
from core.data_integration import DataIntegrator

# 页面配置
st.set_page_config(
    page_title="金融舆情智能分析系统",
    page_icon="📈",
    layout="wide"
)

# 标题
st.title("🤖 金融舆情智能分析系统")
st.markdown("Hi,今天想了解些什么呢？")


# 初始化
@st.cache_resource
def init_analyzer():
    """初始化分析器"""
    try:
        return FinancialSentimentAnalyzer()
    except Exception as e:
        st.error(f"分析器初始化失败: {e}")
        return None


# @st.cache_resource
def init_integrator():
    """初始化数据集成器"""
    # print("初始化integrator...")
    return DataIntegrator()


# 侧边栏
with st.sidebar:
    st.header("🎯 分析功能")

    analysis_mode = st.radio(
        "选择分析模式",
        ["行业景气度分析", "公司风险分析", "批量舆情分析", "投资建议生成"],
        index=0
    )

    st.divider()
    st.header("⚙️ 配置")

    # API状态
    if st.secrets["DEEPSEEK_API_KEY"]:
        st.success("✅ API已配置")
    else:
        st.error("❌ 未配置API密钥")

    # 数据统计
    integrator = init_integrator()
    print("test:",len(integrator.industries))
    st.metric("行业数据", len(integrator.industries))
    st.metric("公司数据", len(integrator.companies))
    st.metric("政策舆情", len(integrator.policies))
    st.metric("风险事件", len(integrator.risk_events))

# 主内容区
analyzer = init_analyzer()
if not analyzer:
    st.error("请先配置DEEPSEEK_API_KEY环境变量")
    st.stop()

if analysis_mode == "行业景气度分析":
    st.header("🏢 行业景气度分析")

    # 选择行业
    industry_names = [ind["行业名称"] for ind in integrator.industries]
    selected_industry = st.selectbox("选择行业", industry_names)

    # 输入或选择舆情
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("舆情输入")
        news_source = st.radio("舆情来源", ["手动输入", "选择现有政策", "行业新闻"])

        if news_source == "手动输入":
            news_title = st.text_input("舆情标题", "新能源汽车补贴政策延续")
            news_content = st.text_area(
                "舆情内容",
                "财政部宣布新能源汽车购置税减免政策将延续三年，预计将带动新能源汽车销量增长30%以上。",
                height=150
            )
        elif news_source == "选择现有政策":
            industry_policies = [
                p for p in integrator.policies
                if selected_industry in p.get("相关行业", [])
            ]

            if industry_policies:
                policy_options = {p["标题"]: p for p in industry_policies}
                selected_policy_title = st.selectbox(
                    "选择政策",
                    list(policy_options.keys())
                )
                selected_policy = policy_options[selected_policy_title]
                news_title = selected_policy["标题"]
                news_content = selected_policy["内容"]
            else:
                st.warning("该行业暂无政策数据")
                news_title = ""
                news_content = ""
        else:
            # 行业新闻示例
            industry_news = {
                "新能源": {
                    "title": "新能源汽车销量创新高",
                    "content": "2024年1-5月新能源汽车销量同比增长80%，渗透率突破30%。"
                },
                "医药": {
                    "title": "创新药审批加速",
                    "content": "国家药监局加快创新药审批，上半年批准新药数量同比增长50%。"
                },
                "人工智能": {
                    "title": "AI算力需求爆发",
                    "content": "大模型训练带动AI算力需求，相关芯片公司业绩大幅增长。"
                }
            }

            news = industry_news.get(selected_industry, {"title": "", "content": ""})
            news_title = news["title"]
            news_content = news["content"]

    with col2:
        st.subheader("行业概况")
        industry_info = integrator.get_industry_info(selected_industry)
        if industry_info:
            st.metric("预期增长率", f"{industry_info.get('预期增长率', 0):.1%}")
            st.metric("行业周期", industry_info.get('行业周期', '未知'))
            st.metric("技术壁垒", industry_info.get('技术壁垒', '未知'))

    # 分析按钮
    if st.button("🚀 开始分析", type="primary") and news_content:
        with st.spinner("AI分析中..."):
            # 进行分析
            result = analyzer.analyze_industry_sentiment(selected_industry, news_content)

            # 显示结果
            st.success("✅ 分析完成")

            # 结果展示
            st.subheader("📊 分析结果")

            # 关键指标卡片
            col1, col2, col3 = st.columns(3)

            with col1:
                impact = result.get("政策影响分析", {}).get("政策性质", "未知")
                st.metric("政策性质", impact)

            with col2:
                sentiment = result.get("景气度判断", {}).get("景气度评级", "未知")
                st.metric("景气度评级", sentiment)

            with col3:
                score = result.get("景气度判断", {}).get("景气度得分", 0)
                st.metric("景气度得分", f"{score}/100")

            # 详细分析
            tabs = st.tabs(["政策影响", "景气度分析", "投资建议", "监控指标"])

            with tabs[0]:
                policy_impact = result.get("政策影响分析", {})
                st.write("**政策性质:**", policy_impact.get("政策性质", "未知"))
                st.write("**影响程度:**", policy_impact.get("影响程度", "未知"))
                st.write("**具体影响:**", policy_impact.get("具体影响", "未知"))

            with tabs[1]:
                sentiment_analysis = result.get("景气度判断", {})
                st.write("**景气度评级:**", sentiment_analysis.get("景气度评级", "未知"))
                st.write("**景气度得分:**", sentiment_analysis.get("景气度得分", "未知"))
                st.write("**趋势判断:**", sentiment_analysis.get("趋势判断", "未知"))

                # 可视化
                score = sentiment_analysis.get("景气度得分", 50)
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "景气度指数"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}
                        ]
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

            with tabs[2]:
                investment = result.get("投资建议", {})
                st.write("**行业配置:**", investment.get("行业配置", "未知"))
                st.write("**配置比例:**", investment.get("配置比例", "未知"))
                st.write("**关注板块:**", ", ".join(investment.get("关注板块", [])))

            with tabs[3]:
                monitoring = result.get("监控指标", {})
                st.write("**关键指标:**", ", ".join(monitoring.get("关键指标", [])))
                st.write("**风险提示:**", monitoring.get("风险提示", "未知"))
                st.write("**时间窗口:**", monitoring.get("时间窗口", "未知"))

            # 原始数据
            with st.expander("📋 查看原始分析数据"):
                st.json(result)

elif analysis_mode == "公司风险分析":
    st.header("⚠️ 公司风险分析")

    # 选择公司
    company_names = [comp["公司名称"] for comp in integrator.companies]
    selected_company = st.selectbox("选择公司", company_names)

    # 获取公司信息
    company_info = integrator.get_company_info(selected_company)

    # 公司基本信息
    if company_info:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("所属行业", company_info.get("所属行业", "未知"))

        with col2:
            st.metric("总市值", f"{company_info.get('总市值', 0)}亿元")

        with col3:
            st.metric("负债率", f"{company_info.get('资产负债率', 0):.1%}")

        with col4:
            risk_score = company_info.get("风险评分", 50)
            st.metric("风险评分", f"{risk_score}/100")

    # 输入或选择舆情
    st.subheader("舆情输入")
    risk_source = st.radio("风险来源", ["手动输入", "选择现有风险事件", "常见风险场景"])

    if risk_source == "手动输入":
        risk_title = st.text_input("风险标题", "公司债务压力加大")
        risk_content = st.text_area(
            "风险内容",
            "公司资产负债率较高，近期有大量债务到期，市场对其偿债能力表示担忧。",
            height=150
        )
    elif risk_source == "选择现有风险事件":
        company_events = [
            e for e in integrator.risk_events
            if selected_company in e.get("涉及公司", [])
        ]

        if company_events:
            event_options = {e["事件标题"]: e for e in company_events}
            selected_event_title = st.selectbox(
                "选择风险事件",
                list(event_options.keys())
            )
            selected_event = event_options[selected_event_title]
            risk_title = selected_event["事件标题"]
            risk_content = selected_event["事件内容"]
        else:
            st.warning("该公司暂无风险事件数据")
            risk_title = ""
            risk_content = ""
    else:
        # 常见风险场景
        risk_scenarios = {
            "财务风险": "公司公告业绩预告不达预期，净利润预计同比下降30%以上。",
            "经营风险": "公司主要产品遭遇市场竞争加剧，市场份额出现下滑。",
            "合规风险": "公司收到监管问询函，要求对相关交易进行说明。",
            "市场风险": "公司所在行业遭遇政策调整，业务模式面临挑战。"
        }

        selected_scenario = st.selectbox("选择风险类型", list(risk_scenarios.keys()))
        risk_title = f"{selected_company}{selected_scenario}事件"
        risk_content = risk_scenarios[selected_scenario]

    # 分析按钮
    if st.button("🔍 分析风险", type="primary") and risk_content:
        with st.spinner("AI风险分析中..."):
            # 进行分析
            result = analyzer.analyze_company_risk(
                selected_company,
                risk_content,
                company_info
            )

            # 显示结果
            st.success("✅ 风险分析完成")

            # 结果展示
            st.subheader("📊 风险分析结果")

            # 关键指标
            col1, col2, col3 = st.columns(3)

            with col1:
                risk_type = result.get("风险识别", {}).get("风险类型", "未知")
                st.metric("风险类型", risk_type)

            with col2:
                severity = result.get("风险识别", {}).get("严重程度", "未知")
                st.metric("严重程度", severity)

            with col3:
                urgency = result.get("处置建议", {}).get("紧急程度", "未知")
                st.metric("紧急程度", urgency)

            # 详细分析
            tabs = st.tabs(["风险识别", "影响评估", "处置建议", "监控预警"])

            with tabs[0]:
                risk_identification = result.get("风险识别", {})
                st.write("**风险类型:**", risk_identification.get("风险类型", "未知"))
                st.write("**风险事件:**", risk_identification.get("风险事件", "未知"))
                st.write("**严重程度:**", risk_identification.get("严重程度", "未知"))

            with tabs[1]:
                impact_assessment = result.get("影响评估", {})
                st.write("**对股价影响:**", impact_assessment.get("对股价影响", "未知"))
                st.write("**对债券评级:**", impact_assessment.get("对债券评级", "未知"))
                st.write("**财务影响:**", impact_assessment.get("财务影响", "未知"))

                # 风险矩阵可视化
                severity_map = {"高": 90, "中": 60, "低": 30}
                impact_map = {"重大负面": 90, "轻微负面": 60, "中性": 30, "轻微正面": 10}

                severity_score = severity_map.get(severity, 50)
                impact_score = impact_map.get(
                    impact_assessment.get("对股价影响", "中性"),
                    50
                )

                fig = go.Figure()

                # 添加风险区域
                fig.add_shape(
                    type="rect",
                    x0=0, y0=0, x1=50, y1=50,
                    fillcolor="green",
                    opacity=0.1,
                    line_width=0
                )
                fig.add_shape(
                    type="rect",
                    x0=50, y0=0, x1=100, y1=50,
                    fillcolor="yellow",
                    opacity=0.1,
                    line_width=0
                )
                fig.add_shape(
                    type="rect",
                    x0=0, y0=50, x1=50, y1=100,
                    fillcolor="yellow",
                    opacity=0.1,
                    line_width=0
                )
                fig.add_shape(
                    type="rect",
                    x0=50, y0=50, x1=100, y1=100,
                    fillcolor="red",
                    opacity=0.1,
                    line_width=0
                )

                # 添加风险点
                fig.add_trace(go.Scatter(
                    x=[severity_score],
                    y=[impact_score],
                    mode='markers+text',
                    marker=dict(size=20, color='red'),
                    text=[selected_company[:4]],
                    textposition="top center",
                    name="风险位置"
                ))

                fig.update_layout(
                    title="风险矩阵（严重程度 vs 影响）",
                    xaxis_title="严重程度",
                    yaxis_title="影响程度",
                    xaxis_range=[0, 100],
                    yaxis_range=[0, 100],
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

            with tabs[2]:
                disposal_suggestions = result.get("处置建议", {})
                st.write("**紧急程度:**", disposal_suggestions.get("紧急程度", "未知"))
                st.write("**具体措施:**", disposal_suggestions.get("具体措施", "未知"))
                st.write("**减仓建议:**", disposal_suggestions.get("减仓建议", "未知"))

                # 操作建议卡片
                if disposal_suggestions.get("具体措施"):
                    st.info("💡 **操作建议:**")
                    measures = disposal_suggestions["具体措施"].split('\n')
                    for measure in measures:
                        if measure.strip():
                            st.markdown(f"- {measure}")

            with tabs[3]:
                monitoring = result.get("预警指标", {})
                st.write("**监控指标:**", ", ".join(monitoring.get("监控指标", [])))
                st.write("**预警信号:**", monitoring.get("预警信号", "未知"))
                st.write("**时间窗口:**", monitoring.get("时间窗口", "未知"))

            # 原始数据
            with st.expander("📋 查看原始分析数据"):
                st.json(result)

elif analysis_mode == "批量舆情分析":
    st.header("📰 批量舆情分析")

    # 准备数据
    news_list = integrator.prepare_news_for_analysis(max_news=5)

    if not news_list:
        st.warning("暂无舆情数据")
        st.stop()

    # 显示待分析舆情
    st.subheader("待分析舆情")

    news_df = pd.DataFrame(news_list)
    st.dataframe(
        news_df[['title', 'related_industry', 'related_company', 'publish_time']],
        use_container_width=True
    )

    # 批量分析按钮
    if st.button("🔍 开始批量分析", type="primary"):
        with st.spinner("批量分析中..."):
            results = analyzer.batch_analyze_news(news_list)

            # 显示结果摘要
            st.success(f"✅ 批量分析完成，共分析 {len(results)} 条舆情")

            # 结果表格
            st.subheader("分析结果摘要")

            summary_data = []
            for result in results:
                summary = {
                    "标题": result.get("新闻标题", "无标题"),
                    "类型": result.get("分析类型", "未知"),
                    "关键结果": "",
                    "建议": ""
                }

                if "景气度评级" in result:
                    summary["关键结果"] = f"景气度: {result['景气度评级']}"
                    summary["建议"] = result.get("投资建议", {}).get("行业配置", "未知")
                elif "严重程度" in result:
                    summary["关键结果"] = f"风险等级: {result['严重程度']}"
                    summary["建议"] = result.get("处置建议", {}).get("紧急程度", "未知")

                summary_data.append(summary)

            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)

            # 详细结果
            st.subheader("详细分析结果")

            for i, result in enumerate(results):
                with st.expander(f"{i + 1}. {result.get('新闻标题', '无标题')}"):
                    if result.get("分析类型") == "行业景气度分析":
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**景气度分析**")
                            sentiment = result.get("景气度判断", {})
                            st.metric("评级", sentiment.get("景气度评级", "未知"))
                            st.metric("得分", sentiment.get("景气度得分", "未知"))

                        with col2:
                            st.write("**投资建议**")
                            investment = result.get("投资建议", {})
                            st.metric("配置", investment.get("行业配置", "未知"))
                            st.metric("比例", investment.get("配置比例", "未知"))

                    else:  # 公司风险分析
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**风险识别**")
                            risk = result.get("风险识别", {})
                            st.metric("类型", risk.get("风险类型", "未知"))
                            st.metric("等级", risk.get("严重程度", "未知"))

                        with col2:
                            st.write("**处置建议**")
                            disposal = result.get("处置建议", {})
                            st.metric("紧急度", disposal.get("紧急程度", "未知"))
                            st.metric("减仓建议", disposal.get("减仓建议", "未知"))

else:  # 投资建议生成
    st.header("💰 投资建议生成")

    # 准备分析结果
    news_list = integrator.prepare_news_for_analysis(max_news=3)
    analysis_results = analyzer.batch_analyze_news(news_list)

    if not analysis_results:
        st.warning("请先进行舆情分析")
        st.stop()

    # 投资组合配置
    st.subheader("投资组合配置")

    col1, col2 = st.columns(2)

    with col1:
        total_amount = st.number_input("投资总额（万元）", value=100.0, min_value=10.0)
        risk_tolerance = st.select_slider(
            "风险承受能力",
            options=["保守", "稳健", "平衡", "积极", "激进"],
            value="平衡"
        )

    with col2:
        investment_horizon = st.selectbox(
            "投资期限",
            ["短期（<1年）", "中期（1-3年）", "长期（>3年）"]
        )
        current_holdings = st.text_area(
            "当前持仓（可选）",
            "新能源行业: 30%\n医药行业: 20%\n现金: 50%",
            height=100
        )

    # 生成建议按钮
    if st.button("📈 生成投资建议", type="primary"):
        with st.spinner("生成投资建议中..."):
            # 准备投资组合信息
            portfolio_info = {
                "投资总额": total_amount,
                "风险承受能力": risk_tolerance,
                "投资期限": investment_horizon,
                "当前持仓": current_holdings
            }

            # 生成投资建议
            suggestions = analyzer.generate_investment_suggestions(
                analysis_results,
                portfolio_info
            )

            # 显示建议
            st.success("✅ 投资建议生成完成")

            # 整体策略
            st.subheader("📋 整体投资策略")

            overall_strategy = suggestions.get("整体策略", {})
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("市场观点", overall_strategy.get("市场观点", "未知"))

            with col2:
                st.metric("风险偏好", overall_strategy.get("风险偏好", "未知"))

            with col3:
                position = overall_strategy.get("仓位建议", "未知")
                st.metric("建议仓位", position)

            # 行业配置
            st.subheader("🏢 行业配置建议")

            industry_suggestions = suggestions.get("行业配置建议", {})

            col1, col2 = st.columns(2)

            with col1:
                st.write("**推荐增持行业**")
                increase = industry_suggestions.get("推荐增持的行业", [])
                for industry in increase[:3]:
                    st.success(f"📈 {industry}")

            with col2:
                st.write("**建议减持行业**")
                decrease = industry_suggestions.get("建议减持的行业", [])
                for industry in decrease[:3]:
                    st.error(f"📉 {industry}")

            # 个股建议
            st.subheader("📊 个股操作建议")

            stock_suggestions = suggestions.get("个股操作建议", {})

            if stock_suggestions.get("推荐关注的个股"):
                st.write("**推荐关注个股:**")
                for stock in stock_suggestions["推荐关注的个股"][:5]:
                    st.info(f"🔍 {stock}")

            if stock_suggestions.get("建议回避的个股"):
                st.write("**建议回避个股:**")
                for stock in stock_suggestions["建议回避的个股"][:5]:
                    st.warning(f"⚠️ {stock}")

            # 风险控制
            st.subheader("🛡️ 风险控制建议")

            risk_control = suggestions.get("风险控制", {})

            with st.expander("查看风险控制详情"):
                st.write("**主要风险点:**", risk_control.get("主要风险点", "未知"))
                st.write("**止损建议:**", risk_control.get("止损建议", "未知"))
                st.write("**对冲策略:**", risk_control.get("对冲策略", "未知"))

            # 监控重点
            st.subheader("👁️ 监控重点")

            monitoring = suggestions.get("监控重点", {})

            monitoring_cols = st.columns(3)

            with monitoring_cols[0]:
                st.write("**重点指标**")
                indicators = monitoring.get("需要重点监控的指标", [])
                for indicator in indicators[:3]:
                    st.markdown(f"- 📊 {indicator}")

            with monitoring_cols[1]:
                st.write("**时间节点**")
                timelines = monitoring.get("关键时间节点", [])
                for timeline in timelines[:3]:
                    st.markdown(f"- ⏰ {timeline}")

            with monitoring_cols[2]:
                st.write("**预警信号**")
                warnings = monitoring.get("预警信号", [])
                for warning in warnings[:3]:
                    st.markdown(f"🚨 {warning}")

            # 原始建议数据
            with st.expander("📋 查看完整建议数据"):
                st.json(suggestions)

# 页脚
st.divider()
st.caption("金融舆情智能分析系统 | 基于DeepSeek大模型 | 仅供学术演示使用")