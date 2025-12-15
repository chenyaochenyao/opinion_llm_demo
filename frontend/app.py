# app.py
import os
import sys

# 获取项目根目录（frontend的上层目录）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将根目录加入sys.path
sys.path.append(ROOT_DIR)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

import os
import time
import random
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import json

from core.sentiment_analyzer import FinancialSentimentAnalyzer
from core.data_integration import DataIntegrator

# 页面配置
st.set_page_config(
    page_title="金融舆情智能分析系统",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
/* 全局样式重置 */
.main > div {
    padding-top: 1rem;
}
.block-container {
    padding: 2rem 3rem;
}

/* 卡片样式优化 */
.metric-card {
    background-color: #f8f9fa;
    border-radius: 12px;
    padding: 1.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 1px solid #e9ecef;
    transition: all 0.3s ease;
}
.metric-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}

/* 产业链卡片样式 */
.chain-card {
    border-radius: 10px;
    padding: 1rem;
    height: 100%;
    transition: all 0.2s ease;
    border: 1px solid #e9ecef;
}
.chain-card:hover {
    box-shadow: 0 3px 9px rgba(0,0,0,0.09);
}

/* 行业列表样式 */
.industry-list {
    padding-left: 1rem;
    line-height: 1.8;
}

/* 标签样式 */
.status-tag {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-right: 0.5rem;
}
.tag-positive {
    background-color: #e8f4f8;
    color: #2d87bb;
}
.tag-negative {
    background-color: #fdf2f8;
    color: #c53030;
}
.tag-neutral {
    background-color: #f5f5f5;
    color: #718096;
}

/* 标题样式 */
.sub-header {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 1.5rem 0 0.8rem 0;
    color: #2d3748;
}

/* 文本样式优化 */
.stMarkdown p {
    line-height: 1.7;
    color: #4a5568;
}
</style>
""", unsafe_allow_html=True)


def get_status_tag(text, type_category):
    """生成带颜色的状态标签"""
    if type_category == "policy":
        # 政策性质标签
        if text == "利好":
            return f'<span class="status-tag tag-positive">✅ {text}</span>'
        elif text == "利空":
            return f'<span class="status-tag tag-negative">❌ {text}</span>'
        else:
            return f'<span class="status-tag tag-neutral">⚖️ {text}</span>'
    elif type_category == "sentiment":
        # 景气度评级标签
        sentiment_map = {
            "高涨": ("tag-positive", "📈 高涨"),
            "良好": ("tag-positive", "😊 良好"),
            "一般": ("tag-neutral", "📊 一般"),
            "低迷": ("tag-negative", "📉 低迷")
        }
        cls, label = sentiment_map.get(text, ("tag-neutral", f"📋 {text}"))
        return f'<span class="status-tag {cls}">{label}</span>'
    return text


# 标题
st.title("🤖 金融舆情智能分析系统")
st.markdown("Hi,今天想些了解什么呢？")


# 初始化
@st.cache_resource
def init_analyzer():
    """初始化分析器"""
    try:
        return FinancialSentimentAnalyzer()
    except Exception as e:
        st.error(f"分析器初始化失败: {e}")
        return None


@st.cache_resource
def init_integrator():
    """初始化数据集成器"""
    return DataIntegrator(data_dir=r".\core\generated_data")


# 侧边栏
with st.sidebar:
    st.header("🎯 导航")

    # 修改分析模式，增加"数据看板"选项
    analysis_mode = st.radio(
        "选择功能",
        ["数据看板", "行业景气度分析", "公司风险分析"],
        index=0
    )

    st.divider()
    st.header("📊 数据概览")

    # 数据统计（始终显示）
    integrator = init_integrator()

    # 使用容器避免重复渲染
    if 'data_stats' not in st.session_state:
        st.session_state.data_stats = {
            'industries': len(integrator.industries),
            'companies': len(integrator.companies),
            'policies': len(integrator.policies),
            'risk_events': len(integrator.risk_events)
        }

    # 显示统计指标
    col1, col2 = st.columns(2)
    with col1:
        st.metric("行业数据", st.session_state.data_stats['industries'])
        st.metric("政策舆情", st.session_state.data_stats['policies'])
    with col2:
        st.metric("公司数据", st.session_state.data_stats['companies'])
        st.metric("风险事件", st.session_state.data_stats['risk_events'])

    st.divider()
    st.header("⚙️ 系统状态")

    # API状态
    if os.getenv("DEEPSEEK_API_KEY"):
        st.success("✅ API已配置")
    else:
        st.error("❌ 未配置API密钥")
        st.info("请在.env文件中设置DEEPSEEK_API_KEY")

# 主内容区
analyzer = init_analyzer()

# ========== 数据看板页面 ==========
if analysis_mode == "数据看板":
    st.header("📊 数据概览看板")

    # 第一行：KPI指标卡片
    # st.subheader("📈 核心指标")
    #
    # kpi_cols = st.columns(4)
    # with kpi_cols[0]:
    #     # 平均行业增长率
    #     if integrator.industries:
    #         avg_growth = sum(ind.get('预期增长率', 0) for ind in integrator.industries) / len(
    #             integrator.industries) * 100
    #         st.metric(
    #             "平均行业增长率",
    #             f"{avg_growth:.1f}%",
    #             # delta=f"{avg_growth - 10:.1f}%" if avg_growth > 10 else None,
    #             # delta_color="normal" if avg_growth > 10 else "inverse"
    #         )
    #     else:
    #         st.metric("平均行业增长率", "0%")
    #
    # with kpi_cols[1]:
    #     # 高风险公司占比
    #     if integrator.companies:
    #         high_risk = sum(1 for c in integrator.companies if c.get('风险评分', 0) > 70)
    #         ratio = (high_risk / len(integrator.companies)) * 100
    #         st.metric(
    #             "高风险公司占比",
    #             f"{ratio:.1f}%",
    #             delta_color="inverse"
    #         )
    #     else:
    #         st.metric("高风险公司占比", "0%")
    #
    # with kpi_cols[2]:
    #     # 利好政策占比
    #     if integrator.policies:
    #         positive = sum(1 for p in integrator.policies if p.get('影响类型') == '利好')
    #         ratio = (positive / len(integrator.policies)) * 100
    #         st.metric(
    #             "利好政策占比",
    #             f"{ratio:.1f}%",
    #             # delta=f"{ratio - 50:.1f}%" if ratio > 50 else None,
    #             # delta_color="normal" if ratio > 50 else "inverse"
    #         )
    #     else:
    #         st.metric("利好政策占比", "0%")
    #
    # with kpi_cols[3]:
    #     # 高严重风险事件
    #     if integrator.risk_events:
    #         high_severity = sum(1 for r in integrator.risk_events if r.get('严重程度') == '高')
    #         st.metric(
    #             "高严重风险事件",
    #             high_severity,
    #             delta_color="inverse"
    #         )
    #     else:
    #         st.metric("高严重风险事件", 0)

    # 第二行：主要图表
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("🔥 行业热度分布")

        if integrator.industries:
            # 创建行业数据
            industry_data = []
            for industry in integrator.industries:
                industry_data.append({
                    '行业': industry.get('行业名称', '未知'),
                    '预期增长率': industry.get('预期增长率', 0) * 100,
                    '热度分数': industry.get('预期增长率', 0) * 100 + industry.get('创新指数',
                                                                                   50) / 2 if '创新指数' in industry else industry.get(
                        '预期增长率', 0) * 100
                })

            df_industries = pd.DataFrame(industry_data)

            # 创建条形图
            fig = px.bar(
                df_industries.sort_values('热度分数', ascending=True),
                x='热度分数',
                y='行业',
                orientation='h',
                color='热度分数',
                color_continuous_scale='RdYlGn',
                title='行业热度排行'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无行业数据")

    with col2:
        st.subheader("⏰ 近期风险事件")

        if integrator.risk_events:
            # 处理时间数据
            risk_data = []
            for event in integrator.risk_events[:10]:  # 取最近20条
                try:
                    # 尝试解析时间
                    time_str = event.get('事件时间', '')
                    risk_data.append({
                        '时间': time_str[:10] if time_str else '未知',
                        '事件标题': event.get('事件标题', '暂无详细内容'),
                        '事件内容': event.get('事件内容', '暂无详细内容'),
                        '公司': event.get('涉及公司', ['未知'])[0] if isinstance(event.get('涉及公司', []),
                                                                                 list) and event.get(
                            '涉及公司') else '未知',
                        '类型': event.get('风险类型', '未知'),
                        '严重程度': event.get('严重程度', '未知')
                    })
                except:
                    continue

            if risk_data:
                df_risks = pd.DataFrame(risk_data)

                # 创建时间线图表（添加hover交互，字段与原始数据完全一致）
                fig = px.scatter(
                    df_risks,
                    x='时间',
                    y='公司',
                    color='严重程度',
                    size=[10] * len(df_risks),
                    color_discrete_map={'高': 'red', '中': 'orange', '低': 'green'},
                    title='风险事件时间分布',
                    # 1. 指定hover时显示的字段（仅保留原始定义的字段）
                    hover_data={
                        '时间': True,
                        '事件标题': True,
                        '事件内容': False,
                        '类型': True,
                        '严重程度': False,
                        '公司': False  # 隐藏重复的公司字段（y轴已显示）
                    }
                )

                # 2. 自定义hover显示模板（字段与原始数据严格对应）
                fig.update_traces(
                    hovertemplate="""
                            <b>📅 时间</b>: %{x}<br>
                            <b>🏢 公司</b>: %{y}<br>
                            <b>📋 事件标题</b>: %{customdata[0]}<br>
                            <b>⚠️ 风险类型</b>: %{customdata[1]}<br>
                            <b>🔴 严重程度</b>: %{customdata[2]}<br>
                            <extra></extra>
                            """,
                    # customdata字段顺序与原始数据严格对应：事件标题/类型/严重程度/事件内容
                    customdata=df_risks[['事件标题', '类型', '严重程度']].values,
                    hoverlabel=dict(
                        bgcolor="white",  # 透明背景（使用模板内的背景）
                        font=dict(
                            size=10,  # 基础字体大小
                            family="SimHei"  # 中文显示
                        ),
                        bordercolor="rgba(0,0,0,0)",  # 透明边框（使用模板内的边框）
                        align="auto",  # 文本左对齐
                        namelength=0  # 隐藏名称
                    )
                )


                # 3. 调整图表布局
                fig.update_layout(
                    height=350,
                    hovermode='closest',  # 显示最近的数据点hover
                    margin=dict(l=10, r=10, t=40, b=20)
                )

                # 4. 通过CSS实现hover框位置和样式优化（核心）
                # st.markdown("""
                #             <style>
                #             /* 调整hover框大小和位置（显示在鼠标右侧） */
                #             .plotly-hover-label {
                #                 transform: translateX(15px) translateY(-50%) !important;  /* 右移+垂直居中 */
                #                 max-width: 100px !important;                             /* 限制最大宽度 */
                #                 min-width: 50px !important;                             /* 限制最小宽度 */
                #                 box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;        /* 轻微阴影 */
                #                 padding: 0 !important;                                   /* 移除默认padding */
                #                 background: transparent !important;                      /* 透明背景 */
                #                 border: none !important;                                 /* 移除默认边框 */
                #             }
                #             /* 确保hover内容紧凑美观 */
                #             .plotly-hover-label > div {
                #                 font-size: 10px !important;
                #                 line-height: 1.2 !important;
                #                 white-space: normal !important;
                #             }
                #             </style>
                #             """, unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无时间数据")
        else:
            st.info("暂无风险事件数据")

    # 第三行：次要图表
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📊 公司风险分布")

        if integrator.companies:
            # 按风险评分分组
            risk_bins = {'低风险(0-30)': 0, '中风险(31-70)': 0, '高风险(71-100)': 0}
            for company in integrator.companies:
                score = company.get('风险评分', 0)
                if score <= 30:
                    risk_bins['低风险(0-30)'] += 1
                elif score <= 70:
                    risk_bins['中风险(31-70)'] += 1
                else:
                    risk_bins['高风险(71-100)'] += 1

            df_risk_dist = pd.DataFrame({
                '风险等级': list(risk_bins.keys()),
                '公司数量': list(risk_bins.values())
            })

            # 创建饼图
            fig = px.pie(
                df_risk_dist,
                values='公司数量',
                names='风险等级',
                color='风险等级',
                color_discrete_map={
                    '低风险(0-30)': 'green',
                    '中风险(31-70)': 'orange',
                    '高风险(71-100)': 'red'
                },
                title='公司风险等级分布'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无公司数据")

    with col4:
        st.subheader("📰 政策影响分析")

        if integrator.policies:
            # 统计政策影响类型
            impact_counts = {'利好': 0, '利空': 0, '中性': 0}
            for policy in integrator.policies:
                impact = policy.get('影响类型', '中性')
                if impact in impact_counts:
                    impact_counts[impact] += 1

            df_impact = pd.DataFrame({
                '影响类型': list(impact_counts.keys()),
                '数量': list(impact_counts.values())
            })

            # 创建柱状图
            fig = px.bar(
                df_impact,
                x='影响类型',
                y='数量',
                color='影响类型',
                color_discrete_map={'利好': 'green', '利空': 'red', '中性': 'gray'},
                title='政策影响类型分布'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无政策数据")

    # 第四行：数据表格预览
    st.subheader("📋 数据预览")

    tab1, tab2, tab3 = st.tabs(["行业数据", "公司数据", "政策舆情"])

    with tab1:
        if integrator.industries:
            industry_preview = []
            for industry in integrator.industries:
                industry_preview.append({
                    '行业名称': industry.get('行业名称', ''),
                    '预期增长率': f"{industry.get('预期增长率', 0):.1%}",
                    '行业周期': industry.get('行业周期', ''),
                    '市盈率区间': f"{industry.get('市盈率区间', [0, 0])[0]}-{industry.get('市盈率区间', [0, 0])[1]}"
                })
            st.dataframe(pd.DataFrame(industry_preview), use_container_width=True)
        else:
            st.info("暂无行业数据")

    with tab2:
        if integrator.companies:
            company_preview = []
            for company in integrator.companies:
                company_preview.append({
                    '公司名称': company.get('公司名称', ''),
                    '所属行业': company.get('所属行业', ''),
                    '总市值(亿元)': company.get('总市值', 0),
                    '风险评分': company.get('风险评分', 0)
                })
            st.dataframe(pd.DataFrame(company_preview), use_container_width=True)
        else:
            st.info("暂无公司数据")

    with tab3:
        if integrator.policies:
            policy_preview = []
            for policy in integrator.policies:
                policy_preview.append({
                    '标题': policy.get('标题', '')[:50] + '...' if len(policy.get('标题', '')) > 50 else policy.get(
                        '标题', ''),
                    '影响类型': policy.get('影响类型', ''),
                    '发布时间': policy.get('发布时间', '')[:10]
                })
            st.dataframe(pd.DataFrame(policy_preview), use_container_width=True)
        else:
            st.info("暂无政策数据")

    # 系统信息
    st.divider()
    st.caption("📊 数据看板 | 基于仿真数据生成")

# ========== 处理页面切换逻辑 ==========
# 检查是否需要切换页面
if 'switch_to_industry' in st.session_state and st.session_state.switch_to_industry:
    analysis_mode = "行业景气度分析"
    del st.session_state.switch_to_industry
elif 'switch_to_company' in st.session_state and st.session_state.switch_to_company:
    analysis_mode = "公司风险分析"
    del st.session_state.switch_to_company
# elif 'switch_to_batch' in st.session_state and st.session_state.switch_to_batch:
#     analysis_mode = "批量舆情分析"
#     del st.session_state.switch_to_batch
# elif 'switch_to_investment' in st.session_state and st.session_state.switch_to_investment:
#     analysis_mode = "投资建议生成"
#     del st.session_state.switch_to_investment

# 如果不是看板模式，显示原有的分析页面
if analysis_mode != "数据看板":
    if not analyzer:
        st.error("请先配置DEEPSEEK_API_KEY环境变量")
        st.stop()

    if analysis_mode == "行业景气度分析":
        st.header("🏢 行业景气度分析")

        # 选择行业（单独一行，突出显示）
        industry_names = [ind["行业名称"] for ind in integrator.industries]
        selected_industry = st.selectbox("选择行业", industry_names, key="industry_select")

        # ========== 第二行：行业概况（整行展示） ==========
        st.markdown("""
               <h3 style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; color: #1e293b;">
                   <span style="font-size: 1.2rem; color: #4ade80;">📊</span>
                   <span>行业概况</span>
               </h3>
           """, unsafe_allow_html=True)

        # 注入卡片样式（仅保留动效和基础样式，布局由st.columns控制）
        st.markdown("""
           <style>
           /* 卡片基础样式 */
           .indicator-card {
               height: 80px;
               border-radius: 8px;
               padding: 1rem;
               text-align: center;
               display: flex;
               flex-direction: column;
               justify-content: center;
               transition: all 0.3s ease;
               cursor: pointer;
           }
           /* 卡片配色 */
           .card-growth { background-color: #e0f2fe; color: #0369a1; }
           .card-cycle { background-color: #fee2e2; color: #991b1b; }
           .card-barrier { background-color: #dcfce7; color: #166534; }
           .card-pe { background-color: #f3e8ff; color: #7e22ce; }
           /* hover动效 */
           .indicator-card:hover {
               transform: translateY(-3px);
               box-shadow: 0 6px 12px rgba(0,0,0,0.1);
               filter: brightness(1.03);
           }
           /* 折叠面板样式 */
           .custom-expander {
               border: 1px solid #e2e8f0;
               border-radius: 8px;
               margin: 0 !important;
               overflow: hidden;
           }
           .custom-expander .streamlit-expanderHeader {
               font-size: 1rem;
               font-weight: 600;
               color: #1e293b;
               padding: 1rem;
               background-color: #f8fafc;
               border-bottom: none !important;
           }
           .custom-expander .streamlit-expanderHeader:hover {
               background-color: #f1f5f9;
           }
           .custom-expander .streamlit-expanderContent {
               padding: 1rem;
           }
            /* 面板标题图标颜色（匹配示例） */
            .expander-icon-red { color: #ef4444 !important; }
            .expander-icon-blue { color: #3b82f6 !important; }
            .expander-icon-green { color: #22c55e !important; }
            /* 移除Streamlit默认的分割线 */
            .stDivider { display: none !important; }
           </style>
           """, unsafe_allow_html=True)

        # 获取行业数据
        industry_info = integrator.get_industry_info(selected_industry)
        if industry_info:
            # ========== 核心：Streamlit原生with col一行四列写法 ==========
            # 创建4列，gap控制列间距，width强制100%宽度
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="medium")

            # 1. 预期增长率卡片（第一列）
            with col1:
                st.markdown(f"""
                   <div class="indicator-card card-growth">
                       <div style="font-size: 0.9rem; margin-bottom: 0.3rem;">预期增长率</div>
                       <div style="font-size: 1.5rem; font-weight: 700;">{industry_info.get('预期增长率', 0):.1%}</div>
                   </div>
                   """, unsafe_allow_html=True)

            # 2. 行业周期卡片（第二列）
            with col2:
                st.markdown(f"""
                   <div class="indicator-card card-cycle">
                       <div style="font-size: 0.9rem; margin-bottom: 0.3rem;">行业周期</div>
                       <div style="font-size: 1.5rem; font-weight: 700;">{industry_info.get('行业周期', '未知')}</div>
                   </div>
                   """, unsafe_allow_html=True)

            # 3. 技术壁垒卡片（第三列）
            with col3:
                st.markdown(f"""
                   <div class="indicator-card card-barrier">
                       <div style="font-size: 0.9rem; margin-bottom: 0.3rem;">技术壁垒</div>
                       <div style="font-size: 1.5rem; font-weight: 700;">{industry_info.get('技术壁垒', '未知')}</div>
                   </div>
                   """, unsafe_allow_html=True)

            # 4. 市盈率区间卡片（第四列）
            with col4:
                pe_min, pe_max = industry_info.get('市盈率区间', [0, 0])
                st.markdown(f"""
                   <div class="indicator-card card-pe">
                       <div style="font-size: 0.9rem; margin-bottom: 0.3rem;">市盈率区间</div>
                       <div style="font-size: 1.5rem; font-weight: 700;">{pe_min}-{pe_max}</div>
                   </div>
                   """, unsafe_allow_html=True)

            # 2. 折叠面板（匹配示例样式）
            # 增长与风险
            with st.container():
                st.markdown('<div class="custom-expander">', unsafe_allow_html=True)
                expander1 = st.expander("🔴 增长与风险", expanded=False)
                with expander1:
                    col_growth, col_risk = st.columns(2, gap="large")
                    with col_growth:
                        st.write("**增长驱动力**")
                        for driver in industry_info.get("增长驱动力", []):
                            st.write(f"• {driver}")
                    with col_risk:
                        st.write("**主要风险**")
                        for risk in industry_info.get("主要风险", []):
                            st.write(f"• {risk}")
                st.markdown('</div>', unsafe_allow_html=True)

            # 运营特征
            with st.container():
                st.markdown('<div class="custom-expander">', unsafe_allow_html=True)
                expander2 = st.expander("🔵 运营特征", expanded=False)
                with expander2:
                    col_attr1, col_attr2 = st.columns(2, gap="large")
                    with col_attr1:
                        st.write("**竞争格局**：", industry_info.get("竞争格局", "未知"))
                        st.write("**政策依赖度**：", f"{industry_info.get('政策依赖度', 0):.1f}/1.0")
                        st.write("**资本密集度**：", f"{industry_info.get('资本密集度', 0):.1f}/1.0")
                    with col_attr2:
                        margin_min, margin_max = industry_info.get("毛利率典型区间", [0, 0])
                        st.write("**毛利率区间**：", f"{margin_min:.1%}-{margin_max:.1%}")
                        st.write("**头部企业份额**：", f"{industry_info.get('头部企业市场份额', 0):.1%}")
                        st.write("**进出口依赖度**：", f"{industry_info.get('进出口依赖度', 0):.1f}/1.0")
                st.markdown('</div>', unsafe_allow_html=True)

            # 关键要素
            with st.container():
                st.markdown('<div class="custom-expander">', unsafe_allow_html=True)
                expander3 = st.expander("🟢 关键要素", expanded=False)
                with expander3:
                    st.write("**关键成功因素**")
                    for factor in industry_info.get("关键成功因素", []):
                        st.write(f"• {factor}")

                    st.write("**ESG与创新**")
                    st.write(f"• ESG评分：{industry_info.get('ESG评分', 0)}")
                    st.write(f"• 创新指数：{industry_info.get('创新指数', 0)}")
                    st.write(f"• 行业热度：{industry_info.get('行业热度指数', 0)}")
                st.markdown('</div>', unsafe_allow_html=True)

        # ========== 第一行：舆情输入（整行展示） ==========
        st.subheader("📝 舆情输入")
        news_source = st.radio("舆情来源", ["手动输入", "选择现有政策"], horizontal=True)

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

        # 分隔线（视觉区分两行）
        st.markdown("---")

        # 分析按钮
        if st.button("🚀 开始分析", type="primary") and news_content:
            # 记录开始时间
            start_time = datetime.datetime.now()

            # 优化的加载提示
            with st.spinner("""
                    🤖 AI正在深度分析中...预计需要30-60秒：
                """):
                # 模拟进度提示（可选，如果分析过程可以分段的话）
                progress_bar = st.progress(0)
                status_text = st.empty()

                # 模拟分步处理（实际使用时替换为真实分析步骤）
                status_text.text("正在解析政策文本... (1/4)")
                progress_bar.progress(25)
                time.sleep(7)

                status_text.text("正在分析行业关联影响... (2/4)")
                progress_bar.progress(50)
                time.sleep(7)

                status_text.text("正在评估景气度指标... (3/4)")
                progress_bar.progress(75)
                time.sleep(7)

                status_text.text("正在生成投资建议... (4/4)")
                progress_bar.progress(100)

                # 进行实际分析
                result = analyzer.analyze_industry_sentiment(selected_industry, news_content)

                # 记录结束时间
                end_time = datetime.datetime.now()
                analysis_duration = (end_time - start_time).total_seconds()

                # 清除进度提示
                progress_bar.empty()
                status_text.empty()

                # 显示完成提示
                st.success(f"✅ 分析完成！本次分析耗时：{analysis_duration:.1f} 秒")

                st.subheader("📊 核心分析指标", anchor=False)
                col1, col2, col3 = st.columns(3, gap="large")

                with col1:
                    impact = result.get("政策影响分析", {}).get("政策性质", "未知")
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#718096; font-size:0.9rem; margin-bottom:0.5rem">政策性质</div>
                        <div style="font-size:1.4rem; font-weight:600;">{get_status_tag(impact, "policy")}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    sentiment = result.get("景气度判断", {}).get("景气度评级", "未知")
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#718096; font-size:0.9rem; margin-bottom:0.5rem">景气度评级</div>
                        <div style="font-size:1.4rem; font-weight:600;">{get_status_tag(sentiment, "sentiment")}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    score = result.get("景气度判断", {}).get("景气度得分", 0)
                    # 景气度得分添加颜色渐变
                    score_color = "#2d87bb" if score >= 80 else "#ed8936" if score >= 60 else "#c53030"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#718096; font-size:0.9rem; margin-bottom:0.5rem">景气度得分</div>
                        <div style="display: flex; align-items: baseline; gap: 0.3rem;">
        <span style="font-size:1.8rem; font-weight:700; color:{score_color};">{score}</span>
        <span style="color:#a0aec0; font-size:0.8rem;">/ 100</span>
    </div>
                    </div>
                    """, unsafe_allow_html=True)

                # ===================== 详细分析Tabs（优化后） =====================
                tabs = st.tabs(["📋 政策影响", "📈 景气度分析", "💡 投资建议", "🔍 监控指标"])

                with tabs[0]:
                    policy_impact = result.get("政策影响分析", {})

                    # 政策基础信息（优化排版）
                    st.markdown('<div class="sub-header">基础政策信息</div>', unsafe_allow_html=True)
                    policy_col1, policy_col2 = st.columns([1, 3])
                    with policy_col1:
                        st.write("**影响程度:**")
                        # 影响程度添加可视化标识
                        impact_level = policy_impact.get("影响程度", "未知")
                        level_icon = "🔴" if impact_level == "高" else "🟡" if impact_level == "中" else "🟢"
                        st.write(f"{level_icon} {impact_level}")

                    with policy_col2:
                        st.write("**具体影响:**")
                        st.write(policy_impact.get("具体影响", "未知"))

                    # 关联行业影响（优化展示）
                    st.markdown('<div class="sub-header">关联行业影响</div>', unsafe_allow_html=True)
                    related_impact = result.get("关联影响", {})
                    col_benefit, col_harm = st.columns(2, gap="medium")

                    with col_benefit:
                        # 受益行业：绿色色块包裹标题+列表
                        st.markdown("""
                        <div style="background-color: #f0fff4; border: 1px solid #c6f6d5; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                            <div style="display:flex; align-items:center; gap: 0.5rem; margin-bottom: 0.8rem;">
                                <span style="background-color: #22c55e; color: white; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.9rem;">✓</span>
                                <h3 style="margin: 0; color: #166534; font-size: 1rem;">受益行业</h3>
                            </div>
                        """, unsafe_allow_html=True)

                        benefit_industries = related_impact.get("受益行业", [])
                        if benefit_industries:
                            benefit_html = "<ul style='padding-left: 1.2rem; margin: 0; line-height: 1.8; color: #1e40af; list-style: disc;'>"
                            for industry in benefit_industries:
                                benefit_html += f"<li style='margin-bottom: 0.4rem;'>{industry}</li>"
                            benefit_html += "</ul></div>"
                            st.markdown(benefit_html, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="color: #6b7280; padding: 0.5rem 0;">暂无受益行业</div></div>',
                                        unsafe_allow_html=True)

                    with col_harm:
                        # 受损行业：红色色块包裹标题+列表
                        st.markdown("""
                        <div style="background-color: #fff5f5; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                            <div style="display:flex; align-items:center; gap: 0.5rem; margin-bottom: 0.8rem;">
                                <span style="background-color: #ef4444; color: white; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.9rem;">✕</span>
                                <h3 style="margin: 0; color: #991b1b; font-size: 1rem;">受损行业</h3>
                            </div>
                        """, unsafe_allow_html=True)

                        harm_industries = related_impact.get("受损行业", [])
                        if harm_industries:
                            harm_html = "<ul style='padding-left: 1.2rem; margin: 0; line-height: 1.8; color: #991b1b; list-style: disc;'>"
                            for industry in harm_industries:
                                harm_html += f"<li style='margin-bottom: 0.4rem;'>{industry}</li>"
                            harm_html += "</ul></div>"
                            st.markdown(harm_html, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="color: #6b7280; padding: 0.5rem 0;">暂无受损行业</div></div>',
                                        unsafe_allow_html=True)

                    # 产业链影响（优化样式）
                    st.markdown('<div class="sub-header">产业链影响（上中下游）</div>', unsafe_allow_html=True)
                    chain_impact = related_impact.get("产业链影响", {})
                    col_up, col_mid, col_down = st.columns(3, gap="medium")

                    with col_up:
                        st.markdown("""
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            <span style="color:#4299e1; font-size:1rem;">⛰️</span>
                            <strong style="color:#2d3748;">上游影响</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        up_impact = chain_impact.get("上游影响", "暂无")
                        st.markdown(f"""
                            <div class="chain-card" style="background-color:#e8f4f8; color:#2d3748;">
                            {up_impact}
                            </div>
                            """, unsafe_allow_html=True)

                    with col_mid:
                        st.markdown("""
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            <span style="color:#9f7aea; font-size:1rem;">🏭</span>
                            <strong style="color:#2d3748;">中游影响</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        mid_impact = chain_impact.get("中游影响", "暂无")
                        st.markdown(f"""
                            <div class="chain-card" style="background-color:#fdf2f8; color:#2d3748;">
                            {mid_impact}
                            </div>
                            """, unsafe_allow_html=True)

                    with col_down:
                        st.markdown("""
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                            <span style="color:#38b2ac; font-size:1rem;">🛒</span>
                            <strong style="color:#2d3748;">下游影响</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        down_impact = chain_impact.get("下游影响", "暂无")
                        st.markdown(f"""
                            <div class="chain-card" style="background-color:#f5f5f5; color:#2d3748;">
                            {down_impact}
                            </div>
                            """, unsafe_allow_html=True)

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
                    st.markdown('<div class="sub-header">配置策略</div>', unsafe_allow_html=True)

                    # 配置策略卡片
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="color:#718096; font-size:0.9rem;">行业配置</div>
                            <div style="font-size:1.5rem; font-weight:600; color:#22c55e;">{investment.get('行业配置策略', '未知')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="color:#718096; font-size:0.9rem;">配置比例区间</div>
                            <div style="font-size:1rem; font-weight:600;">{investment.get('配置比例区间', '未知')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # 核心关注板块
                    st.markdown('<div class="sub-header">核心关注板块</div>', unsafe_allow_html=True)
                    for plate in investment.get('核心关注板块', []):
                        with st.expander(f"📌 {plate.get('板块名称')}"):
                            st.write(f"{plate.get('核心逻辑')}")

                    # 投资节奏和风险收益
                    # st.markdown('<div class="sub-header">投资节奏与风险收益</div>', unsafe_allow_html=True)
                    # st.write(f"**投资节奏:** {investment.get('投资节奏', '未知')}")
                    st.write(f"**风险收益比:** {investment.get('风险收益比', '未知')}")

                with tabs[3]:
                    monitoring = result.get("监控指标", {})
                    st.write("**关键指标:**", monitoring.get("关键指标", []))
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

        if company_info:
            # ===================== 自定义样式 =====================
            st.markdown("""
                    <style>
                    /* 基础信息卡片 */
                    .basic-info-card {
                        background-color: #f8f9fa;
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-bottom: 1.5rem;
                        border: 1px solid #e2e8f0;
                    }
                    .info-item {
                        display: flex;
                        align-items: center;
                        margin-bottom: 0.8rem;
                        font-size: 0.95rem;
                    }
                    .info-icon {
                        font-size: 1.2rem;
                        margin-right: 0.8rem;
                        color: #4299e1;
                        width: 20px;
                        text-align: center;
                    }
                    /* 风险评分卡片样式 */
                    .risk-score-card {
                        background: linear-gradient(135deg, #fef7fb 0%, #fcf1f7 100%);
                        border-radius: 12px;
                        padding: 2rem;
                        text-align: center;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                        margin-bottom: 1.5rem;
                    }
                    /* 风险等级标签 */
                    .risk-tag {
                        display: inline-block;
                        padding: 0.4rem 1rem;
                        border-radius: 20px;
                        font-size: 0.9rem;
                        font-weight: 600;
                        margin: 0.5rem 0;
                    }
                    .risk-low { background-color: #c6f6d5; color: #22543d; }
                    .risk-medium { background-color: #fef3c7; color: #92400e; }
                    .risk-high { background-color: #fed7d7; color: #742a2a; }
                    /* 指标卡片 */
                    .indicator-card {
                        background-color: #ffffff;
                        border-radius: 8px;
                        padding: 1rem;
                        border-left: 4px solid #e53e3e;
                        margin-bottom: 1rem;
                    }
                    .indicator-card-safe { border-left-color: #48bb78; }
                    .indicator-card-warning { border-left-color: #ed8936; }
                    /* 进度条 */
                    .progress-bar-container {
                        height: 8px;
                        background-color: #e2e8f0;
                        border-radius: 4px;
                        margin: 0.5rem 0;
                        width: 100%;
                    }
                    .progress-bar {
                        height: 100%;
                        border-radius: 4px;
                    }
                    /* 风险详情列表 */
                    .risk-list {
                        list-style: none;
                        padding-left: 0;
                    }
                    .risk-list li {
                        padding: 0.8rem 0;
                        border-bottom: 1px solid #f0f0f0;
                        display: flex;
                        align-items: flex-start;
                    }
                    .risk-list li:before {
                        content: "⚠️";
                        margin-right: 0.8rem;
                        font-size: 1rem;
                    }
                    </style>
                    """, unsafe_allow_html=True)

            # ===================== 1. 公司基本情况（新增核心模块） =====================
            st.subheader("📋 公司基本情况")

            # 分两列展示基本信息
            col1, col2 = st.columns([1, 1])

            with col1:
                # 左侧：核心工商信息
                # st.markdown('<div class="basic-info-card">', unsafe_allow_html=True)
                st.markdown("<h4 style='margin: 0 0 1rem 0; color: #2d3748;'>核心信息</h4>", unsafe_allow_html=True)

                # 基础信息列表
                basic_info_items = [
                    ("🏢", "公司名称", company_info.get("公司名称", "未知")),
                    ("📝", "股票代码", company_info.get("股票代码", "未知")),
                    ("📊", "所属行业", company_info.get("所属行业", "未知")),
                    ("📍", "总部所在地", company_info.get("总部所在地", "未知")),
                    ("📅", "成立年份", company_info.get("成立年份", "未知")),
                    ("🚀", "上市年份", company_info.get("上市年份", "未知")),
                    ("👥", "员工人数",
                     f"{company_info.get('员工人数', 0)} 人" if company_info.get('员工人数') else "未知"),
                    ("📜", "审计意见", company_info.get("审计意见", "未知"))
                ]

                # 渲染基础信息
                for icon, label, value in basic_info_items:
                    st.markdown(f"""
                           <div class="info-item">
                               <span class="info-icon">{icon}</span>
                               <span><strong>{label}：</strong>{value}</span>
                           </div>
                           """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                # 右侧：业务概览 + 核心规模指标
                # st.markdown('<div class="basic-info-card">', unsafe_allow_html=True)
                st.markdown("<h4 style='margin: 0 0 1rem 0; color: #2d3748;'>业务概览</h4>", unsafe_allow_html=True)

                # 主营业务展示
                main_business = company_info.get("主营业务", "暂无")
                st.markdown(f"""
                       <div style="font-size: 0.9rem; line-height: 1.6; color: #4a5568; margin-bottom: 1.2rem;">
                           {main_business}
                       </div>
                       """, unsafe_allow_html=True)

                # 核心规模指标
                st.markdown("<h5 style='margin: 0 0 0.8rem 0; color: #2d3748;'>核心规模</h5>", unsafe_allow_html=True)
                scale_items = [
                    ("💹", "总市值", f"{company_info.get('总市值', 0)} 亿元"),
                    ("💰", "营业收入", f"{company_info.get('营业收入', 0)} 亿元"),
                    ("📈", "净利润", f"{company_info.get('净利润', 0)} 亿元"),
                    ("🔬", "研发投入占比", f"{company_info.get('研发投入占比', 0):.1%}")
                ]

                for icon, label, value in scale_items:
                    st.markdown(f"""
                           <div class="info-item" style="margin-bottom: 0.5rem;">
                               <span class="info-icon">{icon}</span>
                               <span style="font-size: 0.9rem;"><strong>{label}：</strong>{value}</span>
                           </div>
                           """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ===================== 1. 核心风险评分（醒目展示） =====================
            risk_score = company_info.get("风险评分", 50)

            # 判定风险等级
            if risk_score < 40:
                risk_level = "低风险"
                risk_tag_class = "risk-low"
            elif risk_score < 70:
                risk_level = "中风险"
                risk_tag_class = "risk-medium"
            else:
                risk_level = "高风险"
                risk_tag_class = "risk-high"

            # 风险评分卡片
            # st.markdown(f"""
            #     <div class="risk-score-card">
            #         <div style="font-size: 1rem; color: #6b7280;">{company_info['公司名称']}</div>
            #         <div style="font-size: 4rem; font-weight: 700; color: #2d3748; margin: 0.5rem 0;">{risk_score}/100</div>
            #         <div class="risk-tag {risk_tag_class}">{risk_level}</div>
            #         <div style="font-size: 0.9rem; color: #6b7280;">评分越低，风险越小</div>
            #     </div>
            #     """, unsafe_allow_html=True)

            # ===================== 2. 多维度风险指标（一行多列） =====================
            st.subheader("多维度风险指标")
            col1, col2, col3, col4 = st.columns(4)

            # 2.1 财务风险 - 资产负债率
            with col1:
                debt_ratio = company_info.get("资产负债率", 0)
                debt_status = "indicator-card-safe" if debt_ratio < 0.6 else "indicator-card-warning" if debt_ratio < 0.8 else "indicator-card"

                st.markdown(f"""
                    <div class="indicator-card {debt_status}">
                        <div style="font-size: 0.85rem; color: #6b7280;">资产负债率</div>
                        <div style="font-size: 1.8rem; font-weight: 600;">{debt_ratio:.1%}</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: {debt_ratio * 100}%; background-color: {'#48bb78' if debt_ratio < 0.6 else '#ed8936' if debt_ratio < 0.8 else '#e53e3e'};"></div>
                        </div>
                        <div style="font-size: 0.8rem; color: #6b7280;">
                            {'安全' if debt_ratio < 0.6 else '警示' if debt_ratio < 0.8 else '高风险'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 2.2 股权风险 - 质押比例
            with col2:
                pledge_ratio = company_info.get("质押比例", 0)
                pledge_status = "indicator-card-safe" if pledge_ratio < 0.1 else "indicator-card-warning" if pledge_ratio < 0.2 else "indicator-card"

                st.markdown(f"""
                    <div class="indicator-card {pledge_status}">
                        <div style="font-size: 0.85rem; color: #6b7280;">股权质押比例</div>
                        <div style="font-size: 1.8rem; font-weight: 600;">{pledge_ratio:.1%}</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: {pledge_ratio * 100}%; background-color: {'#48bb78' if pledge_ratio < 0.1 else '#ed8936' if pledge_ratio < 0.2 else '#e53e3e'};"></div>
                        </div>
                        <div style="font-size: 0.8rem; color: #6b7280;">
                            {'安全' if pledge_ratio < 0.1 else '警示' if pledge_ratio < 0.2 else '高风险'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 2.3 商誉风险 - 商誉占比
            with col3:
                goodwill_ratio = company_info.get("商誉占总资产比例", 0)
                goodwill_status = "indicator-card-safe" if goodwill_ratio < 0.05 else "indicator-card-warning" if goodwill_ratio < 0.1 else "indicator-card"

                st.markdown(f"""
                    <div class="indicator-card {goodwill_status}">
                        <div style="font-size: 0.85rem; color: #6b7280;">商誉占比</div>
                        <div style="font-size: 1.8rem; font-weight: 600;">{goodwill_ratio:.1%}</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: {goodwill_ratio * 100}%; background-color: {'#48bb78' if goodwill_ratio < 0.05 else '#ed8936' if goodwill_ratio < 0.1 else '#e53e3e'};"></div>
                        </div>
                        <div style="font-size: 0.8rem; color: #6b7280;">
                            {'安全' if goodwill_ratio < 0.05 else '警示' if goodwill_ratio < 0.1 else '高风险'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 2.4 现金流风险
            with col4:
                cashflow = company_info.get("现金流状况", "未知")
                cashflow_status = "indicator-card-safe" if cashflow == "良好" else "indicator-card-warning" if cashflow == "一般" else "indicator-card"
                cashflow_color = "#48bb78" if cashflow == "良好" else "#ed8936" if cashflow == "一般" else "#e53e3e"

                st.markdown(f"""
                    <div class="indicator-card {cashflow_status}">
                        <div style="font-size: 0.85rem; color: #6b7280;">现金流状况</div>
                        <div style="font-size: 1.8rem; font-weight: 600; color: {cashflow_color};">{cashflow}</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: {100 if cashflow == '良好' else 50 if cashflow == '一般' else 20}%; background-color: {cashflow_color};"></div>
                        </div>
                        <div style="font-size: 0.8rem; color: #6b7280;">
                            {'充足' if cashflow == '良好' else '紧张' if cashflow == '紧张' else '未知'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # ===================== 3. 风险构成分析（可视化图表） =====================
            st.subheader("风险构成分析")
            col1, col2 = st.columns(2)

            # 3.1 风险维度占比饼图
            with col1:
                # 构建风险维度数据
                risk_dimensions = {
                    "财务风险": min(risk_score * 0.6, 100) if company_info.get("资产负债率", 0) > 0.7 else max(
                        risk_score * 0.3, 10),
                    "股权风险": min(risk_score * 0.5, 100) if company_info.get("质押比例", 0) > 0.2 else max(
                        risk_score * 0.2, 5),
                    "经营风险": min(risk_score * 0.7, 100) if company_info.get("现金流状况") == "紧张" else max(
                        risk_score * 0.2, 8),
                    "市场风险": min(risk_score * 0.4, 100) if company_info.get("市盈率", 0) > 40 else max(
                        risk_score * 0.1, 5)
                }

                fig_pie = px.pie(
                    values=list(risk_dimensions.values()),
                    names=list(risk_dimensions.keys()),
                    title="风险维度占比",
                    color_discrete_sequence=["#e53e3e", "#ed8936", "#9f7aea", "#38b2ac"]
                )
                fig_pie.update_layout(height=300, title_font_size=14)
                st.plotly_chart(fig_pie, use_container_width=True)

            # 3.2 关键风险指标对比（行业均值）
            with col2:
                # 模拟行业均值（可替换为实际行业数据）
                industry_avg = {
                    "资产负债率": 0.65,
                    "质押比例": 0.15,
                    "毛利率": 0.20,
                    "风险评分": 55
                }

                # 构建对比数据
                compare_data = pd.DataFrame({
                    "指标": ["资产负债率", "质押比例", "毛利率", "风险评分"],
                    "公司值": [
                        company_info.get("资产负债率", 0),
                        company_info.get("质押比例", 0),
                        company_info.get("毛利率", 0),
                        company_info.get("风险评分", 50) / 100
                    ],
                    "行业均值": [
                        industry_avg["资产负债率"],
                        industry_avg["质押比例"],
                        industry_avg["毛利率"],
                        industry_avg["风险评分"] / 100
                    ]
                })

                fig_bar = go.Figure(data=[
                    go.Bar(name='公司值', x=compare_data['指标'], y=compare_data['公司值'], marker_color='#4299e1'),
                    go.Bar(name='行业均值', x=compare_data['指标'], y=compare_data['行业均值'], marker_color='#e2e8f0')
                ])
                fig_bar.update_layout(
                    title="关键指标 vs 行业均值",
                    barmode='group',
                    height=300,
                    title_font_size=14
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # ===================== 4. 主要风险点详情 =====================
            st.subheader("主要风险点详情")

            # 风险详情折叠面板
            with st.expander("📋 详细风险清单", expanded=True):
                st.markdown('<ul class="risk-list">', unsafe_allow_html=True)

                # 1. 财务风险点
                if company_info.get("资产负债率", 0) > 0.7:
                    st.markdown(f"""
                        <li>
                            <div>
                                <strong style="color: #e53e3e;">财务风险：高负债率</strong><br>
                                公司资产负债率达{company_info['资产负债率']:.1%}，高于行业安全阈值(70%)，存在偿债压力和财务费用过高风险。
                            </div>
                        </li>
                        """, unsafe_allow_html=True)

                # 2. 股权风险点
                if company_info.get("质押比例", 0) > 0.2:
                    st.markdown(f"""
                        <li>
                            <div>
                                <strong style="color: #e53e3e;">股权风险：高质押比例</strong><br>
                                公司股权质押比例达{company_info['质押比例']:.1%}，若股价下跌可能引发平仓风险，影响公司控制权稳定。
                            </div>
                        </li>
                        """, unsafe_allow_html=True)

                # 3. 经营风险点
                if company_info.get("现金流状况") == "紧张":
                    st.markdown(f"""
                        <li>
                            <div>
                                <strong style="color: #e53e3e;">经营风险：现金流紧张</strong><br>
                                公司现金流状况紧张，可能影响日常运营、研发投入和项目扩张，需关注应收账款回收情况。
                            </div>
                        </li>
                        """, unsafe_allow_html=True)

                # 4. 其他风险点（来自数据中的主要风险）
                if "主要风险" in company_info and company_info["主要风险"]:
                    for risk in company_info["主要风险"]:
                        st.markdown(f"""
                            <li>
                                <div>
                                    <strong style="color: #ed8936;">经营风险</strong><br>
                                    {risk}
                                </div>
                            </li>
                            """, unsafe_allow_html=True)

                # 5. 审计风险点
                if "审计意见" in company_info and "强调事项段" in company_info["审计意见"]:
                    st.markdown(f"""
                        <li>
                            <div>
                                <strong style="color: #e53e3e;">审计风险：非标意见</strong><br>
                                公司审计意见为"{company_info['审计意见']}"，存在需要关注的特殊事项，需进一步核查。
                            </div>
                        </li>
                        """, unsafe_allow_html=True)

                st.markdown('</ul>', unsafe_allow_html=True)

        else:
            st.warning("未获取到该公司的风险分析数据，请选择其他公司")

        # 公司基本信息
        # if company_info:
        #     col1, col2, col3, col4 = st.columns(4)
        #
        #     with col1:
        #         st.metric("所属行业", company_info.get("所属行业", "未知"))
        #
        #     with col2:
        #         st.metric("总市值", f"{company_info.get('总市值', 0)}亿元")
        #
        #     with col3:
        #         st.metric("负债率", f"{company_info.get('资产负债率', 0):.1%}")
        #
        #     with col4:
        #         risk_score = company_info.get("风险评分", 50)
        #         st.metric("风险评分", f"{risk_score}/100")

        # 输入或选择舆情
        st.subheader("舆情输入")
        risk_source = st.radio("风险来源", ["手动输入", "选择现有风险事件"])

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
                    st.write("**监控指标:**", monitoring.get("监控指标", []))
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

# 页脚（只在非看板模式显示）
if analysis_mode != "数据看板":
    st.divider()
    st.caption("金融舆情智能分析系统 | 基于DeepSeek大模型 | 仅供学术演示使用")
