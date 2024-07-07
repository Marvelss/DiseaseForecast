import random
import shutil

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve
import zipfile
import os


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


# 获取各类数据集字段
def getDataFiled():
    weatherName, plantName, agricultureName = ['无1'], ['无2'], ['无3']
    for i in range(len(TempDataSetField)):
        tempDF = TempDataSetField[i]
        if i == 0:
            if tempDF[tempDF['数据类型'] == '气象数据']['字段'].any():
                weatherName.clear()
                temp = tempDF[tempDF['数据类型'] == '气象数据']['字段'].tolist()[0]
                weatherName = np.concatenate((temp, weatherName))
            if tempDF[tempDF['数据类型'] == '植保数据']['字段'].any():
                plantName.clear()
                temp = tempDF[tempDF['数据类型'] == '植保数据']['字段'].tolist()[0]
                plantName = np.concatenate((temp, plantName))
            if tempDF[tempDF['数据类型'] == '农学数据']['字段'].any():
                agricultureName.clear()
                temp = tempDF[tempDF['数据类型'] == '农学数据']['字段'].tolist()[0]
                agricultureName = np.concatenate((temp, agricultureName))
        elif i == 1:
            if tempDF[tempDF['数据类型'] == '气象数据']['预处理后字段'].any():
                temp = tempDF[tempDF['数据类型'] == '气象数据']['预处理后字段'].tolist()[0]
                weatherName = np.concatenate((temp, weatherName))
            if tempDF[tempDF['数据类型'] == '植保数据']['预处理后字段'].any():
                temp = tempDF[tempDF['数据类型'] == '植保数据']['预处理后字段'].tolist()[0]
                plantName = np.concatenate((temp, plantName))
            if tempDF[tempDF['数据类型'] == '农学数据']['预处理后字段'].any():
                temp = tempDF[tempDF['数据类型'] == '农学数据']['预处理后字段'].tolist()[0]
                agricultureName = np.concatenate((temp, agricultureName))
        elif i == 2:
            if tempDF[tempDF['数据类型'] == '气象数据']['备选特征'].any():
                temp = tempDF[tempDF['数据类型'] == '气象数据']['备选特征'].tolist()[0]
                weatherName = np.concatenate(([temp], weatherName))
            if tempDF[tempDF['数据类型'] == '植保数据']['备选特征'].any():
                temp = tempDF[tempDF['数据类型'] == '植保数据']['备选特征'].tolist()[0]
                plantName = np.concatenate((temp, plantName))
            if tempDF[tempDF['数据类型'] == '农学数据']['备选特征'].any():
                temp = tempDF[tempDF['数据类型'] == '农学数据']['备选特征'].tolist()[0]
                agricultureName = np.concatenate((temp, agricultureName))
        elif i == 3:
            if tempDF[tempDF['数据类型'] == '气象数据']['优选特征'].any():
                temp = tempDF[tempDF['数据类型'] == '气象数据']['优选特征'].tolist()[0]
                weatherName = np.concatenate(([temp], weatherName))
            if tempDF[tempDF['数据类型'] == '植保数据']['优选特征'].any():
                temp = tempDF[tempDF['数据类型'] == '植保数据']['优选特征'].tolist()[0]
                plantName = np.concatenate((temp, plantName))
            if tempDF[tempDF['数据类型'] == '农学数据']['优选特征'].any():
                temp = tempDF[tempDF['数据类型'] == '农学数据']['优选特征'].tolist()[0]
                agricultureName = np.concatenate((temp, agricultureName))
    # print(weatherName, plantName, agricultureName)

    return weatherName, plantName, agricultureName


# 删除文件夹文件
def delete_files_in_folder(folder_path):
    # 遍历文件夹下的所有文件和子文件夹
    for root, dirs, files in os.walk(folder_path):
        # 删除文件
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        # 删除子文件夹
        for dir1 in dirs:
            dir_path = os.path.join(root, dir1)
            # os.rmdir(dir_path)
            shutil.rmtree(dir_path)


# 文件压缩
def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历文件夹下的所有文件和子文件夹
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 将文件添加到压缩包
                zipf.write(str(file_path), arcname=os.path.relpath(str(file_path), start=folder_path))


# 文件压缩
def zip_files(file_paths, output_path):
    # 创建 ZIP 文件并将文件写入其中
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            # 检查每个文件是否存在
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"文件 {file_path} 未找到")
            # 确定要写入的文件相对于其所在目录的相对路径
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname=arcname)


# 天气情景转换为对应数字
def getWeatherNum(situations):
    weatherMap = {
        "高温多雨": 1,
        "高温常雨": 2,
        "高温少雨": 3,
        "常温常雨": 4,
        "常温多雨": 5,
        "常温少雨": 6,
        "低温少雨": 7,
        "低温常雨": 8,
        "低温多雨": 9
    }
    result = [float(weatherMap[weather]) for weather in situations]
    return result


# 其他字段值
RawDataSetField = pd.DataFrame(
    columns=["编号", "数据类型", "文件名称", "字段", "传输状态", "上传时间"])
PreprocessedDataSetField = pd.DataFrame(
    columns=["编号", "数据类型", "输入字段", "预处理后字段", "大小", "预处理方法", "方法参数", '时间', "处理状态"])
FeatureDataSetField = pd.DataFrame(
    columns=["编号", "数据类型", "输入特征", "备选特征", "大小", "特征计算方法", "方法参数", "时间", "处理状态"])
OptimalFeatureDataSetField = pd.DataFrame(
    columns=["编号", "数据类型", "输入特征", "优选特征", "大小", "特征优选方法", "方法参数", "时间", "处理状态"])
ModelSet = pd.DataFrame(
    columns=["编号", "模型", "模型参数", "特征", "标签", "评价指标", "数据集划分比例", "模型结构", "模型训练结果",
             "时间",
             "处理状态"])
TempDataSetField = [RawDataSetField, PreprocessedDataSetField,
                    FeatureDataSetField, OptimalFeatureDataSetField,
                    ModelSet]

# 特征值
RawDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
PreprocessedDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
FeatureDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
OptimalFeatureDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
UltimateFeatureDataSet = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
TempDataSet = [RawDataSet, PreprocessedDataSet,
               FeatureDataSet, OptimalFeatureDataSet, OptimalFeatureDataSet]

# 面状内容


# 创建字典
RawDataSetFieldFacet = {
    "编号": [], "文件名称": [], "数据类型": [], "数据格式": [], "根节点": [], "子节点": [],
    "字段": [], "传输状态": [], "上传时间": []
}

PreprocessedDataSetFieldFacet = {
    "编号": [], "文件名称": [], "数据类型": [], "数据格式": [],
    "根节点": [], "子节点": [],
    "输入字段": [], "预处理后字段": [], "大小": [],
    "预处理方法": [], "方法参数": [], "时间": [], "处理状态": []
}

FeatureDataSetFieldFacet = {
    "编号": [], "数据类型": [], "输入特征": [], "备选特征": [], "大小": [],
    "特征计算方法": [], "方法参数": [], "时间": [], "处理状态": []
}

OptimalFeatureDataSetFieldFacet = {
    "编号": [], "数据类型": [], "输入特征": [], "优选特征": [], "大小": [],
    "特征优选方法": [], "方法参数": [], "时间": [], "处理状态": []
}

ModelSetFacet = {
    "编号": [], "模型": [], "模型参数": [], "特征": [], "标签": [], "评价指标": [],
    "数据集划分比例": [], "模型结构": [], "模型训练结果": [], "时间": [], "处理状态": []
}

# 存储字典列表
TempDataSetFieldFacet = [
    RawDataSetFieldFacet, PreprocessedDataSetFieldFacet,
    FeatureDataSetFieldFacet, OptimalFeatureDataSetFieldFacet, ModelSetFacet]

# 特征值
RawDataSetFacet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
PreprocessedDataSetFacet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
FeatureDataSetFacet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
OptimalFeatureDataSetFacet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
UltimateFeatureDataSetFacet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
TempDataSetFacet = [RawDataSetFacet, PreprocessedDataSetFacet,
                    FeatureDataSetFacet, OptimalFeatureDataSetFacet, OptimalFeatureDataSetFacet]
