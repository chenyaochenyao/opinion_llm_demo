# test/test_crawl_functions.py
import sys
import os

# 配置项目路径（关键：让Python识别utils/core/config模块）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# 导入核心采集函数
from core.opinion_crawl import crawl_industry_opinion, crawl_enterprise_opinion,crawl_industry_yuqing
from config.crawl_config import DEBUG_MODE


def test_industry_crawl():
    """测试行业舆情采集函数"""
    print("=" * 50 + "\n开始测试【行业舆情采集函数】\n" + "=" * 50)

    # 测试用例1：新能源行业（通用场景）
    print("\n🔍 测试用例1：采集新能源行业舆情")
    df_energy = crawl_industry_yuqing(industry_name="新能源行业")
    # 验证结果
    assert isinstance(df_energy, pd.DataFrame), "返回值不是DataFrame"
    assert len(df_energy) > 0, "新能源行业未采集到数据"
    assert "所属行业" in df_energy.columns, "缺少所属行业字段"
    assert df_energy["所属行业"].iloc[0] == "新能源行业", "所属行业字段值错误"
    print(f"✅ 测试用例1通过：采集到{len(df_energy)}条新能源行业舆情")

    # 测试用例2：医药行业（含集采关键词）
    print("\n🔍 测试用例2：采集医药行业舆情")
    df_medicine = crawl_industry_opinion(industry_name="医药行业")
    assert len(df_medicine) > 0, "医药行业未采集到数据"
    print(f"✅ 测试用例2通过：采集到{len(df_medicine)}条医药行业舆情")

    # 测试用例3：无效行业（边界场景，验证容错）
    print("\n🔍 测试用例3：采集无效行业（如“不存在的行业”）")
    df_invalid = crawl_industry_opinion(industry_name="不存在的行业")
    assert len(df_invalid) == 0, "无效行业应返回空DataFrame"
    print(f"✅ 测试用例3通过：无效行业返回空数据")

    print("\n🎉 行业舆情采集函数测试全部通过！")


def test_enterprise_crawl():
    """测试企业舆情采集函数"""
    print("=" * 50 + "\n开始测试【企业舆情采集函数】\n" + "=" * 50)

    # 测试用例1：浦发银行（已知企业）
    print("\n🔍 测试用例1：采集浦发银行舆情")
    df_spdb = crawl_enterprise_opinion(enterprise_name="浦发银行")
    # 验证结果
    assert isinstance(df_spdb, pd.DataFrame), "返回值不是DataFrame"
    assert len(df_spdb) > 0, "浦发银行未采集到数据"
    assert "企业名称" in df_spdb.columns, "缺少企业名称字段"
    assert df_spdb["企业名称"].iloc[0] == "浦发银行", "企业名称字段值错误"
    print(f"✅ 测试用例1通过：采集到{len(df_spdb)}条浦发银行舆情")

    # 测试用例2：无效企业（边界场景）
    print("\n🔍 测试用例2：采集无效企业（如“不存在的企业”）")
    df_invalid = crawl_enterprise_opinion(enterprise_name="不存在的企业")
    assert len(df_invalid) == 0, "无效企业应返回空DataFrame"
    print(f"✅ 测试用例2通过：无效企业返回空数据")

    print("\n🎉 企业舆情采集函数测试全部通过！")


if __name__ == "__main__":
    # 导入pandas（避免测试脚本中未导入）
    import pandas as pd

    pd.set_option('display.max_columns', None)  # 显示所有列

    # 执行测试
    try:
        test_industry_crawl()
        test_enterprise_crawl()
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
    except Exception as e:
        print(f"\n❌ 测试异常：{str(e)}")