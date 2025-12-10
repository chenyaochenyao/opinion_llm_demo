# main_data_generator.py
import os
import sys
from datetime import datetime
from data_generator_controller import DataGeneratorController
from industry_generator import IndustryGenerator
from company_generator import CompanyGenerator
from policy_generator import PolicyGenerator
from risk_event_generator import RiskEventGenerator
from financial_series_generator import FinancialSeriesGenerator


class MainDataGenerator:
    """主数据生成程序"""

    def __init__(self, api_key=None):
        self.controller = DataGeneratorController(api_key)
        self.industry_gen = IndustryGenerator(self.controller)
        self.company_gen = CompanyGenerator(self.controller)
        self.policy_gen = PolicyGenerator(self.controller)
        self.risk_gen = RiskEventGenerator(self.controller)
        self.financial_gen = FinancialSeriesGenerator(self.controller)

    def run(self):
        """运行数据生成"""

        print("=" * 60)
        print("金融数据智能生成系统")
        print("=" * 60)

        # 配置
        industries = ["新能源", "医药", "人工智能", "半导体", "金融"]
        companies_per_industry = 3
        policies_per_industry = 5
        events_per_company = 3

        print(f"生成配置:")
        print(f"  行业: {len(industries)}个")
        print(f"  每行业公司数: {companies_per_industry}")
        print(f"  每行业政策数: {policies_per_industry}")
        print(f"  每公司风险事件数: {events_per_company}")
        print()

        # 1. 生成行业数据
        print("生成行业数据...")
        industries_data = self.industry_gen.generate_industries(industries)
        self.controller.save_data(industries_data, "industries.json")
        print(f"  已生成行业: {[ind['行业名称'] for ind in industries_data]}")

        # 2. 生成政策数据
        print("\n生成政策新闻数据...")
        policies_data = self.policy_gen.generate_policies(
            industries_data,
            policies_per_industry
        )
        self.controller.save_data(policies_data, "policies.json")
        print(f"  已生成政策新闻: {len(policies_data)}条")

        # 3. 生成公司数据
        print("\n生成公司数据...")
        companies_data = self.company_gen.generate_companies(
            industries_data,
            companies_per_industry
        )
        self.controller.save_data(companies_data, "companies.json")
        print(f"  已生成公司: {len(companies_data)}家")

        # 4. 生成风险事件数据
        print("\n生成风险事件数据...")
        risk_events_data = self.risk_gen.generate_risk_events(
            companies_data,
            events_per_company
        )
        self.controller.save_data(risk_events_data, "risk_events.json")
        print(f"  已生成风险事件: {len(risk_events_data)}条")

        # 5. 生成财务时间序列数据
        print("\n生成财务时间序列数据...")
        financials_data = self.financial_gen.generate_financials(companies_data)
        self.controller.save_data(financials_data, "financials.json")
        print(f"  已生成财务数据: {len(financials_data)}家公司")

        # 生成数据索引
        self._generate_index(industries_data, companies_data, policies_data, risk_events_data)

        print("\n" + "=" * 60)
        print("数据生成完成！")
        print("=" * 60)

        # 打印统计
        self._print_statistics(
            industries_data,
            companies_data,
            policies_data,
            risk_events_data
        )

    def _generate_index(self, industries_data, companies_data, policies_data, risk_events_data):
        """生成数据索引文件"""

        index_data = {
            "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "数据总量": {
                "行业": len(industries_data),
                "公司": len(companies_data),
                "政策新闻": len(policies_data),
                "风险事件": len(risk_events_data)
            },
            "行业列表": [ind["行业名称"] for ind in industries_data],
            "公司列表": [comp["公司名称"] for comp in companies_data],
            "数据文件": {
                "industries.json": "行业基础数据",
                "companies.json": "公司数据",
                "policies.json": "政策新闻数据",
                "risk_events.json": "风险事件数据",
                "financials.json": "财务时间序列数据"
            }
        }

        self.controller.save_data(index_data, "data_index.json")

    def _print_statistics(self, industries_data, companies_data, policies_data, risk_events_data):
        """打印统计信息"""

        print("\n📊 数据统计:")
        print(f"  行业数量: {len(industries_data)}")
        print(f"  公司数量: {len(companies_data)}")
        print(f"  政策新闻: {len(policies_data)}")
        print(f"  风险事件: {len(risk_events_data)}")

        # 公司行业分布
        industry_counts = {}
        for company in companies_data:
            industry = company.get("所属行业", "未知")
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        print(f"\n  公司行业分布:")
        for industry, count in sorted(industry_counts.items()):
            print(f"    {industry}: {count}家")

        # 政策影响分布
        policy_impacts = {}
        for policy in policies_data:
            impact = policy.get("影响类型", "未知")
            policy_impacts[impact] = policy_impacts.get(impact, 0) + 1

        print(f"\n  政策影响分布:")
        for impact, count in sorted(policy_impacts.items()):
            print(f"    {impact}: {count}条")

        # 风险严重程度分布
        risk_severities = {}
        for risk in risk_events_data:
            severity = risk.get("严重程度", "未知")
            risk_severities[severity] = risk_severities.get(severity, 0) + 1

        print(f"\n  风险严重程度分布:")
        for severity, count in sorted(risk_severities.items()):
            print(f"    {severity}: {count}条")

        # 数据文件大小
        data_dir = self.controller.config["output_dir"]
        print(f"\n  数据文件大小:")
        for filename in ["industries.json", "companies.json", "policies.json",
                         "risk_events.json", "financials.json", "data_index.json"]:
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                print(f"    {filename}: {size_kb:.1f} KB")


if __name__ == "__main__":
    # 从环境变量获取API密钥
    import os
    from dotenv import load_dotenv

    env_file_path = r"D:\project\opinion_llm_demo\.env"
    # if not os.path.exists(env_file_path):
    #     print(f"❌ 错误：.env 文件不存在，路径：{env_file_path}")
    # else:
    #     print(f"✅ .env 文件存在，路径：{env_file_path}")
        # 2. 加载文件并检查加载结果
    load_result = load_dotenv(dotenv_path=env_file_path, encoding='utf-8')
    # if load_result:
    #     print("✅ .env 文件加载成功")
    # else:
    #     print("❌ .env 文件加载失败（文件为空/格式错误）")

    # 3. 打印所有加载的环境变量，排查是否有目标键
    # print("\n加载的环境变量列表：")
    # for key, value in os.environ.items():
    #     if "DEEPSEEK" in key:
    #         print(f"  {key} = {value}")

    api_key = os.getenv("DEEPSEEK_API_KEY")
    # print(api_key)

    if not api_key:
        print("⚠️  未设置DEEPSEEK_API_KEY环境变量")
        print("请在.env文件中设置，或直接输入API密钥:")
        api_key = input("API密钥: ").strip()

    if not api_key or api_key == "your_api_key_here":
        print("⚠️  未提供有效的API密钥，将使用模拟数据模式")
        api_key = None

    # 运行数据生成
    generator = MainDataGenerator(api_key)
    generator.run()