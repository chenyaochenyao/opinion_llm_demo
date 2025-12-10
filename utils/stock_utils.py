# utils/stock_utils.py
import tushare as ts
from config.crawl_config import TUSHARE_TOKEN, STOCK_CODE_PREFIX

ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()


def stock_code_to_name(stock_code):
    """股票代码→企业名称解析"""
    try:
        # 补全6位代码（如输入"600000"→"600000.SH"）
        if len(stock_code) == 6:
            if stock_code.startswith(("60", "68")):
                code = f"{stock_code}.SH"
            elif stock_code.startswith(("00", "30")):
                code = f"{stock_code}.SZ"
            else:
                return None, "股票代码格式错误"
        else:
            return None, "股票代码需为6位数字"

        # 调用Tushare接口
        df = pro.stock_basic(ts_code=code)
        if len(df) == 0:
            return None, "未查询到该股票信息"
        return df.iloc[0]["name"], None
    except Exception as e:
        return None, f"解析失败：{str(e)}"


def validate_stock_code(stock_code):
    """验证股票代码格式"""
    if not stock_code.isdigit() or len(stock_code) != 6:
        return False
    if stock_code[:2] not in STOCK_CODE_PREFIX.keys():
        return False
    return True