import tushare as ts

pro = ts.pro_api("2a81c5e44a8c2e6195c557690878c3c5fa5f2cf30cce8e17c3e6d505")

# 调用新闻接口（示例：获取新浪财经指定时间段新闻）
df = pro.news(
    src='sina',
    start_date='2018-11-21 09:00:00',
    end_date='2018-11-22 10:10:00'
)
print("✅ Tushare接口调用成功！")
print("数据预览：")
print(df[["title", "datetime", "src"]].head())