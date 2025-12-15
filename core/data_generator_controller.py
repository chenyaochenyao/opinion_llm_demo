# data_generator_controller.py
import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

import httpx
from httpx import HTTPTransport
from openai import OpenAI
from dotenv import load_dotenv



class DataGeneratorController:
    """数据生成控制器"""

    def __init__(self, api_key=None):
        # 优先使用传入的 api_key，否则从环境变量读取
        self.api_key = api_key
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 输出目录
        self.output_dir = "generated_data"
        os.makedirs(self.output_dir, exist_ok=True)

        # 生成规则配置
        self.config = {
            "industries": ["新能源", "医药", "人工智能", "半导体", "金融", "房地产", "消费", "周期"],
            "company_count_per_industry": 3,
            "policy_count_per_industry": 5,
            "risk_event_count_per_company": 3,
            "time_range_days": 365,
            "output_dir": "generated_data"
        }

        # 确保输出目录存在
        os.makedirs(self.config["output_dir"], exist_ok=True)

    def generate_all_data(self):
        """生成所有数据"""
        print("开始生成仿真金融数据...")

        try:
            # 1. 生成行业数据
            print("步骤1/5: 生成行业基础数据...")
            industries_data = self.generate_industries_data()
            self.save_data(industries_data, "industries.json")

            # 2. 生成政策新闻数据
            print("步骤2/5: 生成政策新闻数据...")
            policies_data = self.generate_policies_data(industries_data)
            self.save_data(policies_data, "policies.json")

            # 3. 生成公司数据
            print("步骤3/5: 生成公司数据...")
            companies_data = self.generate_companies_data(industries_data)
            self.save_data(companies_data, "companies.json")

            # 4. 生成风险事件数据
            print("步骤4/5: 生成风险事件数据...")
            risk_events_data = self.generate_risk_events_data(companies_data)
            self.save_data(risk_events_data, "risk_events.json")

            # 5. 生成财务时间序列数据
            print("步骤5/5: 生成财务时间序列数据...")
            financials_data = self.generate_financials_data(companies_data)
            self.save_data(financials_data, "financials.json")

            print("✅ 数据生成完成！")
            # self.print_statistics(industries_data, companies_data, policies_data)

            return True

        except Exception as e:
            print(f"❌ 数据生成失败: {e}")
            return False

    def generate_with_llm(self, prompt: str, system_prompt: str = None,
                          temperature: float = 0.3,
                          response_format: dict = None) -> str:
        """调用大模型生成数据"""

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature,
                response_format=response_format,
                max_tokens=4000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"LLM调用失败: {e}")
            # 返回模拟数据避免中断
            return self._get_fallback_data(prompt)

    def _get_fallback_data(self, prompt: str) -> str:
        """LLM调用失败时的备选数据"""
        if "行业" in prompt:
            return json.dumps([
                {
                    "行业名称": "新能源",
                    "行业代码": "NE",
                    "描述": "新能源汽车、光伏、风电等清洁能源产业",
                    "产业链位置": "中游",
                    "增长驱动力": ["政策支持", "技术突破", "环保需求"],
                    "主要风险": ["原材料涨价", "竞争加剧", "技术迭代"],
                    "行业周期": "成长期",
                    "预期增长率": 0.15,
                    "市盈率区间": [20, 40],
                    "关键成功因素": ["技术创新", "成本控制", "政策获取"]
                }
            ], ensure_ascii=False, indent=2)
        else:
            return "[]"

    def save_data(self, data: Any, filename: str):
        """保存数据到文件"""
        filepath = os.path.join(self.config["output_dir"], filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  保存到: {filepath}")

    def print_statistics(self, industries_data, companies_data, policies_data):
        """打印生成数据统计"""
        print("\n📊 生成数据统计:")
        print(f"  行业数量: {len(industries_data)}")
        print(f"  公司数量: {len(companies_data)}")
        print(f"  政策新闻: {len(policies_data)}")

        # 按行业统计公司
        industry_counts = {}
        for company in companies_data:
            industry = company.get("所属行业", "未知")
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        print(f"\n  各行业公司分布:")
        for industry, count in industry_counts.items():
            print(f"    {industry}: {count}家")
