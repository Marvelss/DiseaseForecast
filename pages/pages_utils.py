import pandas as pd


# 带有全选的多选框
def multiselect_all(streamlit, value_list, label, temp_label_visibility):
    checkbox_all = streamlit.checkbox("全选")
    if checkbox_all:
        selected_options = streamlit.multiselect(
            label,
            value_list, value_list, label_visibility=temp_label_visibility)
    else:
        selected_options = streamlit.multiselect(
            label,
            value_list, label_visibility=temp_label_visibility)
    return selected_options


RawDataSet = pd.DataFrame(
    {
        "选择字段": [True, False, False],
        "数据集": ["气象数据", "植保数据", "农学数据"],
        "字段": ["温度", "生育期", "预测峰值"],
        "时间": ['22:10:20', '20:10:20', '21:10:20'],
    }
)
PreprocessedDataSet = pd.DataFrame(columns=["选择字段", "数据集", "字段", "大小", "处理方法", "时间", "下载数据集"])
PreprocessedDataSet.loc[0] = [True, "气象数据", "降雨日数", "1*3", "时间分辨率转换", '22:10:20', True]
# PreprocessedDataSet.loc[1] = ["植保数据", "基于活动积温的生育期", "1*6", "降雨日数计算", '20:10:20']
# PreprocessedDataSet.loc[2] = ["农学数据", "预测峰值", "1*6", "降水累积量计算", '21:10:20']
FeatureDataSet = pd.DataFrame(columns=["选择字段", "数据集", "特征", "大小", "处理方法", "时间", "下载数据集"])
FeatureDataSet.loc[0] = [True, "农学数据", "预测峰值", "1*6", "降水累积量计算", '21:10:20', False]
ModelSet = pd.DataFrame(columns=["模型", "时间", "下载模型结构、结果和参数值"])
