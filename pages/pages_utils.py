import random

import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve


# 带有全选的多选框
def multiselect_all(streamlit, box_name, value_list, label, temp_label_visibility):
    checkbox_all = streamlit.checkbox(box_name)
    if checkbox_all:
        selected_options = streamlit.multiselect(
            label,
            value_list, value_list, label_visibility=temp_label_visibility)
    else:
        selected_options = streamlit.multiselect(
            label,
            value_list, label_visibility=temp_label_visibility)
    return selected_options


def plot_metrics(st, metrics_list, model, x_test, y_test, class_names):
    if "Confusion Matrix" in metrics_list:
        st.subheader("Confusion Matrix")
        confusion_matrix(model, x_test, y_test, display_labels=class_names)
        st.pyplot()
    if "ROC Curve" in metrics_list:
        st.subheader("ROC Curve")
        roc_curve(model, x_test, y_test)
        st.pyplot()
    if "Precision-Recall Curve" in metrics_list:
        st.subheader("Precision-Recall Curve")
        precision_recall_curve(model, x_test, y_test)
        st.pyplot()


def getIntersectionCols(df1, df2):
    return list(set(df1.columns) & set(df2.columns))


# 生成长度为16的随机字符串
def generateID():
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(16):
        random_str += base_str[random.randint(0, length)]
    return random_str


# 其他字段值
RawDataSetField = pd.DataFrame(
    columns=["编号", "数据类型", "文件名称", "字段", "传输状态", "上传时间"])
PreprocessedDataSetField = pd.DataFrame(
    columns=["编号", "数据类型", "输入字段", "预处理后字段", "预处理方法", "方法参数", '时间', "下载数据集"])
FeatureDataSetField = pd.DataFrame(
    columns=["编号", "数据类型", "输入特征", "备选特征", "大小", "特征计算方法", "方法参数", "时间", "下载数据集"])
OptimalFeatureDataSetField = pd.DataFrame(
    columns=["编号", "数据类型", "输入特征", "优选特征", "大小", "特征优选方法", "方法参数", "时间", "下载数据集"])
ModelSet = pd.DataFrame(
    columns=["编号", "模型", "模型参数", "评价指标", "数据集划分", "时间", "下载模型结构、结果和参数值"])
TempDataSetField = [RawDataSetField, PreprocessedDataSetField,
                    FeatureDataSetField, OptimalFeatureDataSetField,
                    ModelSet]

# 特征值
RawDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
PreprocessedDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
FeatureDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
OptimalFeatureDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
TempDataSet = [RawDataSet, PreprocessedDataSet,
               FeatureDataSet, OptimalFeatureDataSet, ModelSet]
