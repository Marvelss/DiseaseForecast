import pandas as pd
from sklearn.model_selection import train_test_split
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


# 特征字段
RawDataSetField = pd.DataFrame(
    {
        "数据集": ["气象数据", "植保数据", "气象数据", "植保数据"],
        "字段": ["温度", "峰值", "湿度", "降水"],
        "时间": ['22:10:20', '20:10:20', '21:10:20', '21:10:20'],
    }
)
PreprocessedDataSetField = pd.DataFrame(columns=["数据集", "字段", "大小", "处理方法", "时间", "下载数据集"])

FeatureDataSetField = pd.DataFrame(columns=["数据集", "特征", "大小", "处理方法", "时间", "下载数据集"])
FeatureDataSetField.loc[0] = ["农学数据", "预测峰值", "1*6", "降水累积量计算", '21:10:20', False]
FeatureDataSetField.loc[1] = ["气象数据", "温度", "1*6", "时间(温度)分辨率转换", '21:10:20', False]
FeatureDataSetField.loc[2] = ["气象数据", "降水", "1*6", "降水累积量计算", '21:10:20', False]
FeatureDataSetField.loc[3] = ["植保数据", "预测峰值", "1*6", "生育期", '21:10:20', False]
OptimalFeatureDataSetField = pd.DataFrame(columns=["数据集", "特征", "大小", "处理方法", "时间", "下载数据集"])
OptimalFeatureDataSetField.loc[0] = ["农学数据", "预测峰值", "1*6", "t检验", '21:10:20', False]
ModelSet = pd.DataFrame(columns=["模型", "时间", "下载模型结构、结果和参数值"])
TempDataSetField = [RawDataSetField, PreprocessedDataSetField, FeatureDataSetField, OptimalFeatureDataSetField,
                    ModelSet]
# 特征值
RawDataSet = pd.DataFrame(columns=["上级单位", "测报站点"])
PreprocessedDataSet = pd.DataFrame(columns=["上级单位", "测报站点"])
FeatureDataSet = pd.DataFrame(columns=["上级单位", "测报站点"])
OptimalFeatureDataSet = pd.DataFrame(columns=["上级单位", "测报站点"])
TempDataSet = [RawDataSet, PreprocessedDataSet,
               FeatureDataSet, OptimalFeatureDataSet, ModelSet]
