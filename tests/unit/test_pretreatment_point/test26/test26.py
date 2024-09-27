"""
@Author : SakuraFox
@Time: 2024-09-06 9:56
@File : test26.py
@Description : 检测异常值-四分位点
"""
import pandas as pd


def detect_outliers_iqr(data, column):
    # 计算四分位数
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1

    # 定义异常值范围
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # print(lower_bound)
    # print(upper_bound)
    # 检测异常值
    lower_outliers = data[data[column] < lower_bound]
    upper_outliers = data[data[column] > upper_bound]
    # print(min(lower_outliers[column].tolist()))
    # print(max(upper_outliers[column].tolist()))
    return lower_bound, upper_bound, len(lower_outliers), len(upper_outliers)


df = pd.read_excel('苹果斑点落叶病-气象数据.xlsx')
# 示例调用
outliers = detect_outliers_iqr(df, '3月上旬湿度')
