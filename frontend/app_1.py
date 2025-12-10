# frontend/app_1.py
import sys
import os

# 获取项目根目录（frontend的上层目录）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将根目录加入sys.path
sys.path.append(ROOT_DIR)
import streamlit as st
import time
import pandas as pd
from utils.stock_utils import stock_code_to_name, validate_stock_code

# from core.opinion_crawl import crawl_industry_opinion, crawl_financer_opinion, text_deduplicate, text_filter
# from core.opinion_risk_identify import run_risk_identify
# from core.opinion_relation_analysis import run_relation_analysis
# from core.opinion_suggestion import run_suggestion_generation
# from utils.report_utils import generate_yuqing_report
# from utils.db_utils import save_to_db, get_db_data

# 页面配置
st.set_page_config(page_title="金融舆情分析系统", layout="wide")
st.title("📊 金融舆情分析系统")

# 侧边栏：输入类型选择
st.sidebar.title("🔍 分析类型选择")
analysis_type = st.sidebar.radio(
    "请选择分析对象类型",
    ["行业舆情", "企业/股票舆情"]
)

# 核心输入区域
if analysis_type == "行业舆情":
    st.subheader("📈 行业舆情分析")
    industry_name = st.text_input("请输入行业名称（如：新能源、医药）", placeholder="新能源行业")
    crawl_btn = st.button("开始采集并分析", type="primary", disabled=not industry_name)

    if crawl_btn:
        with st.spinner("正在采集行业舆情数据..."):
            # 1. 动态生成行业配置并采集
            target_industry = {
                "industry_name": industry_name,
                "industry_keywords": [industry_name.replace("行业", "")],
                "event_keywords": ["补贴", "政策", "风险", "逾期", "集采", "营收"]
            }
            df_industry = crawl_industry_opinion_custom(target_industry)
            df_industry = text_deduplicate(df_industry, key_cols=["标题", "内容"])
            df_industry = text_filter(df_industry, filter_cols=["内容"], keywords=[industry_name.replace("行业", "")])
            save_to_db(df_industry, table_name="yuqing_raw")
            st.success(f"✅ 采集完成！共获取{len(df_industry)}条{industry_name}舆情数据")

        with st.spinner("正在分析舆情数据..."):
            # 2. 调用分析链路
            run_risk_identify()
            run_relation_analysis()
            run_suggestion_generation()
            df_result = get_db_data(table_name="yuqing_final")
            st.success("✅ 舆情分析完成！")

        with st.spinner("正在生成舆情报告..."):
            # 3. 生成报告
            report = generate_opinion_report(df_result, "行业", industry_name)
            st.subheader("📋 行业舆情分析报告")
            st.markdown(report)

            # 4. 报告下载
            st.download_button(
                label="📥 下载报告",
                data=report,
                file_name=f"{industry_name}舆情分析报告_{time.strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

            # 5. 展示详细数据
            st.subheader("📄 详细舆情列表")
            st.dataframe(
                df_result[["标题", "发布时间", "来源", "最终风险类型", "最终风险等级"]],
                use_container_width=True
            )

else:
    st.subheader("🏢 企业/股票舆情分析")
    input_type = st.radio("请选择输入类型", ["股票代码", "企业名称"])
    target_input = st.text_input(
        f"请输入{input_type}（如：600000/万科企业）",
        placeholder="600000 或 万科企业"
    )
    crawl_btn = st.button("开始采集并分析", type="primary", disabled=not target_input)

    if crawl_btn:
        # 1. 解析输入（股票代码→企业名称）
        if input_type == "股票代码":
            if not validate_stock_code(target_input):
                st.error("❌ 股票代码格式错误（需为6位数字，如600000）")
                st.stop()
            financer_name, err = stock_code_to_name(target_input)
            if err:
                st.error(f"❌ {err}")
                st.stop()
        else:
            financer_name = target_input

        with st.spinner(f"正在采集{financer_name}舆情数据..."):
            # 2. 动态生成融资方配置并采集
            target_financer = {
                "financer_name": financer_name,
                "financer_aliases": [financer_name],
                "risk_keywords": ["债务逾期", "评级下调", "资金链", "集采", "营收下滑", "监管"]
            }
            df_financer = crawl_financer_opinion_custom(target_financer)
            df_financer = text_deduplicate(df_financer, key_cols=["标题", "内容"])
            df_financer = text_filter(df_financer, filter_cols=["内容"], keywords=[financer_name])
            save_to_db(df_financer, table_name="yuqing_raw")
            st.success(f"✅ 采集完成！共获取{len(df_financer)}条{financer_name}舆情数据")

        with st.spinner("正在分析舆情数据..."):
            # 3. 调用分析链路
            run_risk_identify()
            run_relation_analysis()
            run_suggestion_generation()
            df_result = get_db_data(table_name="yuqing_final")
            st.success("✅ 舆情分析完成！")

        with st.spinner("正在生成舆情报告..."):
            # 4. 生成报告
            report = generate_opinion_report(df_result, "企业", financer_name)
            st.subheader("📋 企业舆情分析报告")
            st.markdown(report)

            # 5. 报告下载
            st.download_button(
                label="📥 下载报告",
                data=report,
                file_name=f"{financer_name}舆情分析报告_{time.strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

            # 6. 展示详细数据
            st.subheader("📄 详细舆情列表")
            st.dataframe(
                df_result[["标题", "发布时间", "来源", "最终风险类型", "最终风险等级"]],
                use_container_width=True
            )



