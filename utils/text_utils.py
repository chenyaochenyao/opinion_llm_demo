# utils/text_utils.py
import pandas as pd
import hashlib

# utils/text_utils.py
import pandas as pd
import hashlib


def text_deduplicate(df, key_cols=["标题", "内容"]):
    """
    基于文本指纹去重（彻底修复空DF+多列赋值问题）
    :param df: 待去重的DataFrame
    :param key_cols: 用于生成指纹的列（默认：标题+内容）
    :return: 去重后的DataFrame
    """
    # 1. 空DataFrame直接返回（核心：避免后续操作报错）
    if df.empty:
        return df.copy()

    # 2. 校验key_cols是否存在（避免列名错误）
    missing_cols = [col for col in key_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺失用于生成指纹的列：{missing_cols}")

    # 3. 逐行生成文本指纹（确保返回单列Series）
    def generate_fingerprint(row):
        """单行列值拼接→MD5指纹（处理空值）"""
        # 拼接指定列的文本，空值替换为空字符串
        text = "|".join([
            str(row[col]).strip() if pd.notna(row[col]) else ""
            for col in key_cols
        ])
        # 生成MD5指纹（空文本返回固定值）
        return hashlib.md5(text.encode("utf-8")).hexdigest() if text else "empty_fingerprint"

    # 4. 正确赋值：apply(axis=1)返回单列Series
    df = df.copy()  # 避免修改原DF
    df["text_fingerprint"] = df.apply(generate_fingerprint, axis=1)

    # 5. 去重+删除临时列
    df_dedup = df.drop_duplicates(subset=["text_fingerprint"], keep="first")
    df_dedup = df_dedup.drop(columns=["text_fingerprint"])

    return df_dedup


def text_filter(df, filter_cols=["内容"], keywords=None):
    """
    过滤包含指定关键词的文本（新增空值/列校验）
    :param df: 待过滤的DataFrame
    :param filter_cols: 过滤列（默认：内容）
    :param keywords: 过滤关键词列表
    :return: 过滤后的DataFrame
    """
    # 1. 空值/空DF直接返回
    if df.empty or (keywords is None) or len(keywords) == 0:
        return df.copy()

    # 2. 校验过滤列
    missing_cols = [col for col in filter_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺失过滤列：{missing_cols}")

    # 3. 生成过滤正则（忽略大小写）
    filter_regex = "|".join([kw.strip() for kw in keywords])
    if not filter_regex:
        return df.copy()

    # 4. 逐行判断是否包含关键词（处理空值）
    df = df.copy()
    df["is_filtered"] = df[filter_cols].apply(
        lambda x: x.astype(str).str.contains(
            filter_regex,
            regex=True,
            na=False,
            case=False  # 忽略大小写
        ).any(),
        axis=1
    )

    # 5. 过滤+删除临时列
    df_filtered = df[df["is_filtered"]].drop(columns=["is_filtered"])
    return df_filtered