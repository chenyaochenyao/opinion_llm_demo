# financial_series_generator.py
import json
import random
import numpy as np
from datetime import datetime, timedelta


class FinancialSeriesGenerator:
    """财务时间序列生成器"""

    def __init__(self, controller):
        self.controller = controller

    def generate_financials(self, companies_data: list[dict]) -> dict:
        """生成财务时间序列数据"""

        all_financials = {}

        for company in companies_data:
            company_name = company["公司名称"]
            print(f"  为{company_name}生成财务时间序列...")

            # 生成该公司的财务时间序列
            company_financials = self._generate_financials_for_company(company)

            if company_financials:
                all_financials[company_name] = company_financials

        return all_financials

    def _generate_financials_for_company(self, company: dict) -> dict:
        """为特定公司生成财务时间序列"""

        company_name = company["公司名称"]

        # 生成季度数据（过去8个季度）
        quarters = []
        current_date = datetime.now()

        for i in range(8):
            quarter_date = current_date - timedelta(days=90 * (i + 1))
            # 计算季度数 (1-4)
            quarter_num = (quarter_date.month - 1) // 3 + 1
            quarters.append(f"{quarter_date.year}-Q{quarter_num}")

        quarters.reverse()  # 从最早到最近

        # 基础财务数据
        base_revenue = company.get("营业收入", 100)
        base_net_profit = company.get("净利润", 10)
        base_gross_margin = company.get("毛利率", 0.3)
        base_debt_ratio = company.get("资产负债率", 0.5)

        # 生成趋势数据
        revenue_trend = self._generate_trend(base_revenue, volatility=0.1, trend=0.02)
        net_profit_trend = self._generate_trend(base_net_profit, volatility=0.15, trend=0.03)
        gross_margin_trend = self._generate_trend(base_gross_margin, volatility=0.05, trend=0.0, min_val=0.1,
                                                  max_val=0.7)
        debt_ratio_trend = self._generate_trend(base_debt_ratio, volatility=0.03, trend=0.005, min_val=0.2, max_val=0.8)

        # 计算衍生指标
        operating_cash_flow = [rev * random.uniform(0.1, 0.3) for rev in revenue_trend]
        total_assets = [rev / random.uniform(0.5, 1.5) for rev in revenue_trend]
        total_liabilities = [assets * dr for assets, dr in zip(total_assets, debt_ratio_trend)]
        equity = [assets - liab for assets, liab in zip(total_assets, total_liabilities)]
        roe = [profit / e if e > 0 else 0 for profit, e in zip(net_profit_trend, equity)]

        # 生成季度数据点
        quarterly_data = []

        for i, quarter in enumerate(quarters):
            # 添加一些季度性波动
            q_seasonal = 1.0 + 0.05 * np.sin(i * np.pi / 2)  # 季度性波动

            data_point = {
                "季度": quarter,
                "营业收入": round(revenue_trend[i] * q_seasonal * random.uniform(0.95, 1.05), 2),
                "净利润": round(net_profit_trend[i] * q_seasonal * random.uniform(0.9, 1.1), 2),
                "毛利率": round(gross_margin_trend[i] * random.uniform(0.98, 1.02), 4),
                "净利率": round(net_profit_trend[i] / revenue_trend[i] if revenue_trend[i] > 0 else 0, 4),
                "资产负债率": round(debt_ratio_trend[i] * random.uniform(0.99, 1.01), 4),
                "经营活动现金流量净额": round(operating_cash_flow[i] * random.uniform(0.9, 1.1), 2),
                "总资产": round(total_assets[i] * random.uniform(0.95, 1.05), 2),
                "总负债": round(total_liabilities[i] * random.uniform(0.95, 1.05), 2),
                "净资产": round(equity[i] * random.uniform(0.95, 1.05), 2),
                "ROE": round(roe[i] if roe[i] > 0 else 0, 4),
                "研发费用": round(revenue_trend[i] * company.get("研发投入占比", 0.05) * random.uniform(0.9, 1.1), 2),
                "销售费用率": round(random.uniform(0.05, 0.15), 4),
                "管理费用率": round(random.uniform(0.03, 0.08), 4)
            }

            quarterly_data.append(data_point)

        # 生成日度股价数据（简化版）
        daily_prices = self._generate_daily_prices(company)

        # 生成月度指标
        monthly_indicators = self._generate_monthly_indicators(company)

        return {
            "公司名称": company_name,
            "股票代码": company.get("股票代码", "000000"),
            "季度财务数据": quarterly_data,
            "日度股价数据": daily_prices,
            "月度市场指标": monthly_indicators,
            "关键财务比率": {
                "最新市盈率": company.get("市盈率", 20),
                "最新市净率": company.get("市净率", 2.5),
                "股息率": round(random.uniform(0.01, 0.04), 4),
                "PEG比率": round(random.uniform(0.8, 1.5), 2)
            }
        }

    def _generate_trend(self, base_value: float, volatility: float = 0.1,
                        trend: float = 0.0, min_val: float = None,
                        max_val: float = None) -> list[float]:
        """生成趋势数据"""

        values = [base_value]

        for i in range(7):
            # 随机波动 + 趋势
            new_value = values[-1] * (1 + random.uniform(-volatility, volatility) + trend)

            # 限制范围
            if min_val is not None:
                new_value = max(new_value, min_val)
            if max_val is not None:
                new_value = min(new_value, max_val)

            values.append(new_value)

        return values

    def _generate_daily_prices(self, company: dict, days: int = 60) -> list[dict]:
        """生成日度股价数据"""

        base_price = company.get("总市值", 100) / 10  # 简化股价计算
        volatility = 0.02  # 日波动率

        prices = []
        current_date = datetime.now() - timedelta(days=days)

        price = base_price

        for i in range(days):
            # 随机游走
            price_change = price * random.uniform(-volatility, volatility)
            price += price_change

            # 确保价格为正
            price = max(price, 0.1)

            date_str = (current_date + timedelta(days=i)).strftime("%Y-%m-%d")

            price_data = {
                "日期": date_str,
                "开盘价": round(price * random.uniform(0.99, 1.01), 2),
                "收盘价": round(price, 2),
                "最高价": round(price * random.uniform(1.0, 1.03), 2),
                "最低价": round(price * random.uniform(0.97, 1.0), 2),
                "成交量": random.randint(1000000, 5000000),
                "成交额": round(random.uniform(1000, 5000), 2)
            }

            prices.append(price_data)

        return prices

    def _generate_monthly_indicators(self, company: dict, months: int = 12) -> list[dict]:
        """生成月度市场指标"""

        indicators = []
        current_date = datetime.now() - timedelta(days=30 * months)

        for i in range(months):
            date_str = (current_date + timedelta(days=30 * i)).strftime("%Y-%m")

            indicator_data = {
                "月份": date_str,
                "机构调研次数": random.randint(0, 10),
                "券商研报数量": random.randint(0, 5),
                "北向资金持股比例变化": round(random.uniform(-0.01, 0.01), 4),
                "融资买入额": round(random.uniform(100, 1000), 2),
                "融券卖出额": round(random.uniform(50, 500), 2),
                "股东户数": random.randint(10000, 100000),
                "股权质押比例": round(company.get("质押比例", 0.1) * random.uniform(0.9, 1.1), 4)
            }

            indicators.append(indicator_data)

        return indicators