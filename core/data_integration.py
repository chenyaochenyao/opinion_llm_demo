# data_integration.py
import json
import os
from typing import Dict, List
import streamlit as st
import sys
import os

# 获取项目根目录（frontend的上层目录）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将根目录加入sys.path
sys.path.append(ROOT_DIR)

class DataIntegrator:
    """数据集成器"""

    def __init__(self, data_dir=r".\generated_data"):
        self.data_dir = data_dir
        # 加载数据
        self.industries = self._load_data("industries.json")
        self.companies = self._load_data("companies.json")
        self.policies = self._load_data("policies.json")
        self.risk_events = self._load_data("risk_events.json")
        # print(self.industries)
        # print("ok1")

    def _load_data(self, filename: str):
        """加载数据文件"""
        filepath = os.path.join(self.data_dir, filename)
        # print("ok2")
        print(filepath)
        print(os.path.exists(filepath))
        if os.path.exists(filepath):
            # print("ok3")
            with open(filepath, "r", encoding="utf-8") as f:
                # print("ok4")
                return json.load(f)

        return []

    def prepare_news_for_analysis(self, max_news: int = 10) -> List[Dict]:
        """准备舆情数据用于分析"""
        news_list = []

        # 1. 从政策数据准备行业舆情
        for policy in self.policies[:max_news // 2]:
            news = {
                "title": policy.get("标题", "政策新闻"),
                "content": policy.get("内容", ""),
                "source": policy.get("新闻来源", ""),
                "publish_time": policy.get("发布时间", ""),
                "related_industry": policy.get("相关行业", [""])[0] if policy.get("相关行业") else "",
                "related_company": "",
                "news_type": "policy"
            }
            news_list.append(news)

        # 2. 从风险事件准备公司舆情
        for event in self.risk_events[:max_news // 2]:
            company_name = event.get("涉及公司", [""])[0] if event.get("涉及公司") else ""

            # 查找公司信息
            company_info = None
            for company in self.companies:
                if company.get("公司名称") == company_name:
                    company_info = company
                    break

            news = {
                "title": event.get("事件标题", "风险事件"),
                "content": event.get("事件内容", ""),
                "source": event.get("信息来源", ""),
                "publish_time": event.get("事件时间", ""),
                "related_industry": company_info.get("所属行业", "") if company_info else "",
                "related_company": company_name,
                "company_info": company_info,
                "news_type": "risk_event"
            }
            news_list.append(news)

        return news_list

    def get_company_info(self, company_name: str) -> Dict:
        """获取公司信息"""
        for company in self.companies:
            if company.get("公司名称") == company_name:
                return company
        return {}

    def get_industry_info(self, industry_name: str) -> Dict:
        """获取行业信息"""
        for industry in self.industries:
            if industry.get("行业名称") == industry_name:
                return industry
        return {}



# ---------------------- 测试代码 ----------------------
# if __name__ == "__main__":
#     current_dir = os.getcwd()
#     print(f"当前工作目录: {current_dir}")
#     # 1. 实例化数据集成器
#     integrator = DataIntegrator()
#
#     # 2. 测试数据加载是否成功
#     print("=== 数据加载测试 ===")
#     print(f"行业数据条数: {len(integrator.industries)}")
#     print(f"公司数据条数: {len(integrator.companies)}")
#     print(f"政策数据条数: {len(integrator.policies)}")
#     print(f"风险事件数据条数: {len(integrator.risk_events)}")

    # # 3. 测试prepare_news_for_analysis方法
    # print("\n=== 舆情数据准备测试 ===")
    # news_data = integrator.prepare_news_for_analysis(max_news=8)
    # print(f"生成的舆情数据条数: {len(news_data)}")
    # # 打印第一条政策舆情和第一条风险事件舆情
    # if news_data:
    #     print("第一条政策舆情:")
    #     print(json.dumps(news_data[0], ensure_ascii=False, indent=2))
    #     if len(news_data) > 1:
    #         print("\n第一条风险事件舆情:")
    #         print(json.dumps(news_data[1], ensure_ascii=False, indent=2))
    #
    # # 4. 测试get_company_info方法
    # print("\n=== 公司信息获取测试 ===")
    # # 取第一个公司名称（若有）
    # if integrator.companies:
    #     test_company = integrator.companies[0].get("公司名称")
    #     company_info = integrator.get_company_info(test_company)
    #     print(f"公司[{test_company}]的信息:")
    #     print(json.dumps(company_info, ensure_ascii=False, indent=2))
    # else:
    #     print("无公司数据可测试")
    #
    # # 5. 测试get_industry_info方法
    # print("\n=== 行业信息获取测试 ===")
    # # 取第一个行业名称（若有）
    # if integrator.industries:
    #     test_industry = integrator.industries[0].get("行业名称")
    #     industry_info = integrator.get_industry_info(test_industry)
    #     print(f"行业[{test_industry}]的信息:")
    #     print(json.dumps(industry_info, ensure_ascii=False, indent=2))
    # else:
    #     print("无行业数据可测试")


# pass