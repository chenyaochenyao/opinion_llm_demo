# utils/report_utils.py
import time
import json
from collections import Counter
from config.crawl_config import REPORT_TEMPLATE


def generate_yuqing_report(df_result, target_type, target_name):
    """生成结构化舆情报告"""
    # 基础信息
    crawl_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    data_count = len(df_result)

    # 风险统计
    risk_level_list = df_result["最终风险等级"].tolist()
    risk_type_list = df_result["最终风险类型"].tolist()
    total_risk_level = Counter(risk_level_list).most_common(1)[0][0] if risk_level_list else "无风险"
    main_risk_type = Counter(risk_type_list).most_common(1)[0][0] if risk_type_list else "无风险"
    risk_level_dist = ", ".join([f"{k}：{v}条" for k, v in Counter(risk_level_list).items()])

    # 核心摘要（取前3条高风险舆情）
    high_risk_df = df_result[df_result["最终风险等级"] == "高"].head(3)
    summary = ""
    for idx, row in high_risk_df.iterrows():
        semantic = json.loads(row["语义解析结果"].replace("'", '"'))
        summary += f"{idx + 1}. {semantic['核心主体']}：{semantic['事件']}（{row['发布时间']}）\n"
    if not summary:
        summary = "暂无高风险舆情"

    # 关联分析汇总
    relation_analysis = ""
    for idx, row in df_result.head(2).iterrows():
        relation = json.loads(row["关联分析结果"].replace("'", '"'))
        relation_analysis += f"- {relation['关联主体']}：{relation['传导路径']}\n"
    if not relation_analysis:
        relation_analysis = "无明显关联风险"

    # 处置建议汇总
    investment_suggestion = df_result.iloc[0]["处置建议结果"].get("投资场景建议", "无") if data_count > 0 else "无"
    risk_control_suggestion = df_result.iloc[0]["处置建议结果"].get("风控场景建议", "无") if data_count > 0 else "无"

    # 填充模板
    report = REPORT_TEMPLATE.format(
        target_type=target_type,
        target_name=target_name,
        crawl_time=crawl_time,
        data_count=data_count,
        total_risk_level=total_risk_level,
        summary=summary,
        main_risk_type=main_risk_type,
        risk_level_dist=risk_level_dist,
        relation_analysis=relation_analysis,
        investment_suggestion=investment_suggestion,
        risk_control_suggestion=risk_control_suggestion
    )
    return report