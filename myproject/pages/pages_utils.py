import random
import shutil

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
def getDataFiled(dataNum, tempDataSetField):
    tempDF = tempDataSetField
    weatherName, plantName, agricultureName = [], [], []
    fieldName = '字段'
    if dataNum == 0:
        fieldName = '字段'
    elif dataNum == 1:
        fieldName = '预处理后字段'
    elif dataNum == 2:
        fieldName = '备选特征'
    elif dataNum == 3:
        fieldName = '优选特征'
    if tempDF[tempDF['数据类型'] == '气象数据'][fieldName].any():
        array_2d = tempDF[tempDF['数据类型'] == '气象数据'][fieldName].tolist()
        # 原始数据传入的是个数组, 而其他环节只传入上传后的单个字符串, 所以array_2d[0]
        if not isinstance(array_2d[0], list):
            array_2d = [array_2d]
        # 合并二维数组为一维数组并去重
        weatherName = list(set([item for sublist in array_2d for item in sublist]))
    if tempDF[tempDF['数据类型'] == '植保数据'][fieldName].any():
        array_2dP = tempDF[tempDF['数据类型'] == '植保数据'][fieldName].tolist()
        # 原始数据传入的是个数组, 而其他环节只传入上传后的单个字符串, 所以array_2d[0]
        if not isinstance(array_2dP[0], list):
            array_2dP = [array_2dP]
        # 合并二维数组为一维数组并去重
        plantName = list(set([item for sublist in array_2dP for item in sublist]))
    if tempDF[tempDF['数据类型'] == '农学数据'][fieldName].any():
        array_2dA = tempDF[tempDF['数据类型'] == '农学数据'][fieldName].tolist()
        # 原始数据传入的是个数组, 而其他环节只传入上传后的单个字符串, 所以array_2d[0]
        if not isinstance(array_2dA[0], list):
            array_2dA = [array_2dA]
        # 合并二维数组为一维数组并去重
        agricultureName = list(set([item for sublist in array_2dA for item in sublist]))

    # 特征优选界面做单独处理,因为单条记录含多个输出特征
    if dataNum == 3 and not tempDF['优选特征'].empty:
        flagT = True
        for i, row in tempDF.iterrows():
            if isinstance(tempDF['优选特征'][i], float):
                # 只要含有nan就不取
                flagT = False
        expanded_rows = []
        if flagT:
            for i, row in tempDF.iterrows():
                print(row['优选特征'])
                expanded_rows = expanded_rows + row['优选特征'].split(',')
            weatherName, plantName, agricultureName = expanded_rows, expanded_rows, expanded_rows
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


# 特征优选获取数据类型
def getDataType(featureList):
    dataTypeList = []
    for feature in featureList:
        if '-' in feature:
            feature = feature.split('-')[0]
        # 查找值对应的行，并获取对应行的'数据类型'列的值
        for index, row in TempDataSetField[0].iterrows():
            # 判断 '字段' 列中是否包含 feature
            if feature in row['字段']:
                # 获取该行的 '数据类型' 列的值
                data_type = row['数据类型']
                dataTypeList.append(data_type)
                break  # 找到匹配的行后，跳出循环
    return dataTypeList


# 更新左侧目标显示
def updateLeftBars(raw_data_facet):
    # 初始化 leftBars 从 RawDataSetFieldFacet 获取数据
    left_bars = []
    structure = {}

    for i in range(len(raw_data_facet["编号"])):
        root = raw_data_facet["根节点"][i]
        child = raw_data_facet["子节点"][i]
        field = raw_data_facet["字段"][i]  # 获取字段信息
        file_name1 = raw_data_facet["文件名称"][i]
        file_value = f"{file_name1}.{raw_data_facet['数据格式'][i]}"

        if root not in structure:
            structure[root] = {}

        if child not in structure[root]:
            structure[root][child] = {}

        if field not in structure[root][child]:
            structure[root][child][field] = []

        structure[root][child][field].append({"label": file_name1, "value": file_value})

    for root, children in structure.items():
        root_node = {"label": root, "value": root, "children": []}
        for child, fields in children.items():
            child_node = {"label": child, "value": child, "children": []}
            for field, files in fields.items():
                field_node = {"label": field, "value": field, "children": files}
                child_node["children"].append(field_node)
            root_node["children"].append(child_node)
        left_bars.append(root_node)

    return left_bars


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
RawDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
PreprocessedDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
FeatureDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
OptimalFeatureDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
UltimateFeatureDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
TempDataSet = [RawDataSet, PreprocessedDataSet,
               FeatureDataSet, OptimalFeatureDataSet, OptimalFeatureDataSet]

# 面状内容
# 创建字典
RawDataSetFieldFacet = {
    "编号": [], "文件名称": [], "数据类型": [], "数据格式": [], "根节点": [], "子节点": [],
    "字段": [], "传输状态": [], "上传时间": []
}

PreprocessedDataSetFieldFacet = {
    "编号": [], "输入文件": [], "文件名称": [], "数据类型": [],
    "数据格式": [], "根节点": [], "子节点": [], "字段": [],
    "预处理方法": [], "方法参数": [], "时间": [], "处理状态": []
}

FeatureDataSetFieldFacet = {
    "编号": [], "文件名称": [], "数据类型": [], "数据格式": [],
    "根节点": [], "子节点": [], "输入文件": [], "字段": [],
    "特征计算方法": [], "方法参数": [], "时间": [], "处理状态": []
}

OptimalFeatureDataSetFieldFacet = pd.DataFrame(
    columns=["编号", "数据类型", "输入特征", "优选特征", "大小", "特征优选方法", "方法参数", "时间", "处理状态"])

ModelSetFacet = pd.DataFrame(
    columns=["编号", "模型", "模型参数", "特征", "标签", "评价指标", "数据集划分比例", "模型结构", "模型训练结果",
             "时间",
             "处理状态"])

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
# 保留字段(贯穿整个环节)
reservedField = ['经度', '纬度', '年', 'DayOfYear']
