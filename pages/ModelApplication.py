import datetime
import io
import os.path
import pickle

import joblib
import scipy
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from streamlit_pills import pills
from modelandmethod.PretreatmentMethod import PretreatmentMethod

import pages_utils
from modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
from modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod

# 原始数据
if "dataSet" not in st.session_state:
    st.session_state["dataSet"] = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
# 已训练模型路径
if "trainedModel" not in st.session_state:
    st.session_state["trainedModel"] = {}

# 数据处理记录上传
if "processedDataRecorder" not in st.session_state:
    st.session_state["processedDataRecorder"] = [
        pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    ]

st.set_page_config(
    layout="wide"
)


# 获取模型
def getModel(modelName):
    modelPathRoot = os.path.join(r'E:\a_python\program\diseaseForecastStreamlit',
                                 'resource',
                                 'modelsResults',
                                 'modelsStructure')
    modelPath = os.path.join(modelPathRoot, modelName + '_structure.pkl')
    print(modelPath)
    if os.path.exists(modelPath):
        # 加载已经训练好的模型
        return joblib.load(modelPath)
    else:
        return None


def onModelApplication(rawData, processedDataRecorderList):
    # =========================特征计算及读取执行方法=========================
    # 读取记录
    featureCalculateDF = processedDataRecorderList[1]
    inputFeature1 = featureCalculateDF["输入特征"].tolist()
    # outputFeature1 = featureCalculateDF["备选特征"].tolist()
    featureCalculateList = featureCalculateDF["特征计算方法"].tolist()
    modelParam1 = featureCalculateDF["方法参数"].tolist()
    print(modelParam1)
    afterHandleData = None
    for indexT, tempMethod in enumerate(featureCalculateList):
        # 使用处理后最新的字段内容
        reservedField = rawData.columns.tolist()
        print('===========检测===========')
        print(rawData)
        print(reservedField)
        tool1 = FeatureCalculationMethod(rawData, reservedField)
        if tempMethod == '降雨日数计算':
            rawData, newColumn = tool1.rainfallDaysAccumulation(
                [inputFeature1[indexT]], modelParam1[indexT].split(','))
        elif tempMethod == '降水累积量计算':

            rawData, newColumn = tool1.precipitationAccumulation(
                [inputFeature1[indexT]], modelParam1[indexT].split(','))

            # result2.to_excel('handled' + str(indexT) + '.xlsx')

        # intersectionCols = pages_utils.getIntersectionCols(
        #     rawData,
        #     afterHandleData
        # )
        #
        # rawData = pd.merge(
        #     afterHandleData,
        #     rawData,
        #     on=intersectionCols,
        #     how="left")
    print(f'=============特征字段计算完成=============')
    # rawData.to_excel(r'E:\a_python\program\diseaseForecastStreamlit\resource\uploadFileDir\featureCalculated.xlsx')
    # =========================特征优选及读取执行方法=========================
    featureOptimalDF = processedDataRecorderList[2]

    inputFeature2 = featureOptimalDF["输入特征"].tolist()
    outputFeature2 = featureOptimalDF["优选特征"].tolist()
    featureOptimalList = featureOptimalDF["特征优选方法"].tolist()
    modelParam2 = featureOptimalDF["方法参数"].tolist()

    print('==========测试列=============')
    print(rawData.columns)
    print(type(rawData.columns))
    tool2 = FeatureOptimizationMethod(rawData, rawData.columns.tolist())
    # 初始化特征优选方法
    for indexT, tempMethod in enumerate(featureOptimalList):
        reservedField = rawData.columns.tolist()
        afterHandleData = None
        # print(tempMethod)
        if tempMethod == 'Pearson相关性分析':
            print('=============Pearson相关性分析检测============')
            print(modelParam2[indexT].split(','))
            rawData, _ = tool2.Pearson(modelParam2[indexT].split(','))
        elif tempMethod == 'Relief-F互相关分析':
            rawData, _ = tool2.ReliefF(
                inputFeature2[0], modelParam2)
        # intersectionCols = pages_utils.getIntersectionCols(
        #     rawData,
        #     afterHandleData
        # )
        #
        # rawData = pd.merge(
        #     afterHandleData,
        #     rawData,
        #     on=intersectionCols,
        #     how="left")
    print(f'=============特征字段优选完成=============')
    # rawData.to_excel(r'E:\a_python\program\diseaseForecastStreamlit\resource\uploadFileDir\featureOptimized.xlsx')

    # =========================提取有效值=========================
    # 使用groupby分组并提取每个分组的第一个非空值
    ultimateFeatures = rawData.groupby(['上级单位', '测报站点', '年']).first().reset_index()
    # ******删除包含缺失值的行******
    df_cleaned = ultimateFeatures.dropna()
    print(f'=============提取有效值=============')
    # df_cleaned.to_excel(r'E:\a_python\program\diseaseForecastStreamlit\resource\uploadFileDir\ultimateFeatures.xlsx')

    # =========================模型构建及读取执行方法=========================
    # df_cleaned = pd.read_excel('ultimateFeatures.xlsx')
    modelDF = processedDataRecorderList[3]

    models = modelDF["模型"].tolist()
    # modelsParam = modelDF["模型参数"].tolist()
    feature = modelDF["特征"].tolist()
    label = modelDF["标签"].tolist()
    # precision = modelDF["评价指标"].tolist()
    # ratio = modelDF["数据集划分比例"].tolist()
    for indexT, (tempModel, tempFeature,
                 tempLabel) in enumerate(zip(models, feature, label)):

        # 模型读取
        model = getModel(tempModel)
        inputDF = df_cleaned[tempFeature.split(',')]
        print('=============测试数据集====')
        print(inputDF)
        # 筛选出省份为'湖南省'和测报站点为'湘阴县'的所有行(不能删除,否则少特征)
        # filtered_df = df_cleaned[(df_cleaned['上级单位'] == province) & (df_cleaned['测报站点'] == station)]
        # 选取包含在 tempFeature 中的列
        # inputDF = filtered_df[tempFeature]
        print(model)
        if '上级单位' and '测报站点' in tempFeature:
            X = pd.get_dummies(inputDF, columns=['上级单位', '测报站点'])
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        # 接下来您可以使用 X_scaled 进行进一步的模型训练和预测
        # model.predict() 方法需要接受和训练时相同的特征列
        predictions = model.predict(X_scaled)
        # 创建一个 DataFrame 包含预测值
        predictions_df = pd.DataFrame(predictions, columns=['Predicted_value'])

        # 合并特征数值和预测值到一个新的 DataFrame
        result_df = pd.concat([df_cleaned, predictions_df], axis=1)
        # 打印包含预测值和特征值的 DataFrame
        result_df.to_excel(
            os.path.join(os.getcwd(),
                         'resource',
                         'modelsResults',
                         'modelsApplicationResult',
                         str(tempModel) + '_applicationPredicts' + '.xlsx'))
        st.toast(f'{tempModel}模型预测完毕', icon='✅')
        print('=========================完成模型应用=========================')


# =======================可视化结果=======================
print('---')
col2, col3 = st.columns(2)
with col2:
    st.markdown("##### 输入原始数据")
    uploaded_dataSet = st.file_uploader(
        "输入原始字段",
        accept_multiple_files=False,
        label_visibility='collapsed')

with col3:
    st.markdown("##### 加载模型")
    uploaded_model = st.file_uploader("加载模型", label_visibility='collapsed')

if uploaded_dataSet:
    bytes_data = uploaded_dataSet.read()
    dataTemp = pd.read_excel(bytes_data)
    # 获取两个DataFrame列名的交集
    intersection_cols = pages_utils.getIntersectionCols(
        dataTemp, st.session_state["dataSet"]
    )
    # 合并数据
    st.session_state["dataSet"] = pd.merge(
        dataTemp, st.session_state["dataSet"],
        on=intersection_cols, how="outer")

if uploaded_model:
    modelPath = os.path.join(
        os.getcwd(),
        'resource',
        'uploadFileDir',
        uploaded_model.name)
    # 模型文件保存到本地
    with open(modelPath, 'wb') as f:
        f.write(uploaded_model.read())
    st.session_state["trainedModel"][uploaded_model.name.split('_')[0]] = modelPath
    st.markdown(st.session_state["trainedModel"])
st.markdown('---')
col1112, col1113 = st.columns([0.6, 0.4])
with col1112:
    st.markdown("##### 数据展示")
    st.data_editor(
        st.session_state["dataSet"],
        height=550, width=1500)
with col1113:
    st.markdown("##### 各环节处理方法")
    st.info("注意:\n上传内容可直接从各环节导出", icon="ℹ️️")
    selectedTemplate = pills("选择数据处理步骤",
                             ['数据预处理',
                              '特征计算', '特征优选', '模型'])
    uploaded_files = st.file_uploader(
        "选择数据处理步骤",
        accept_multiple_files=False,
        label_visibility='collapsed',
        type=['xlsx', 'csv', 'txt', 'xls'],
        help='help')
    # 数据上传
    if uploaded_files:
        bytes_data = uploaded_files.read()
        dataFrameTemp = pd.read_excel(bytes_data)
        if selectedTemplate == '数据预处理':
            st.session_state["processedDataRecorder"].insert(0, dataFrameTemp)
        elif selectedTemplate == '特征计算':
            st.session_state["processedDataRecorder"].insert(1, dataFrameTemp)
        elif selectedTemplate == '特征优选':
            st.session_state["processedDataRecorder"].insert(2, dataFrameTemp)
        elif selectedTemplate == '模型':
            st.session_state["processedDataRecorder"].insert(3, dataFrameTemp)

    tab1, tab2, tab3, tab4 = st.tabs(["数据预处理", "特征计算", "特征优选", '模型'])
    with tab1:
        st.session_state["processedDataRecorder"][0] = st.data_editor(
            st.session_state["processedDataRecorder"][0],
            height=220, width=800, num_rows="dynamic",
            column_order=['编号', '输入字段', '预处理后字段', "方法参数", '预处理方法'])
    with tab2:
        st.session_state["processedDataRecorder"][1] = st.data_editor(
            st.session_state["processedDataRecorder"][1],
            height=220, width=800, num_rows="dynamic",
            column_order=['编号', '输入特征', '备选特征', "方法参数", '特征计算方法'])
        # temperature_data = simulate_temperature_data()
    with tab3:
        st.session_state["processedDataRecorder"][2] = st.data_editor(
            st.session_state["processedDataRecorder"][2],
            height=220, width=800, num_rows="dynamic",
            column_order=['编号', '输入特征', '优选特征', "方法参数", '特征优选方法'])
    with tab4:
        st.session_state["processedDataRecorder"][3] = st.data_editor(
            st.session_state["processedDataRecorder"][3],
            height=220, width=800, num_rows="dynamic",
            column_order=['编号', '模型', '特征', '标签', "评价指标", "数据集划分比例"])
    interval_col34, interval_col33 = st.columns([2.8, 1])
    # btn33 = interval_col33.button('运行')
    st.markdown(st.session_state["processedDataRecorder"][0])
    with interval_col33:
        btn11 = st.button('运行')
        if btn11:
            onModelApplication(
                st.session_state["dataSet"],
                st.session_state["processedDataRecorder"])
        # @st.experimental_dialog("准备模型训练", width='large')
        # def vote():
        #     beforeDF = st.session_state["dataSet"]
        #     # isExtract = st.checkbox('提取有效值')
        #     # # 分组并提取每个分组的第一个非空值
        #     # result = beforeDF.groupby(['上级单位', '测报站点', '年']).first().reset_index()
        #     # # ******删除包含缺失值的行******
        #     # df_cleaned = result.dropna()
        #     # if isExtract:
        #     #     a = st.data_editor(df_cleaned, num_rows="dynamic", width=700, height=300)
        #     #     pages_utils.TempDataSet[4] = df_cleaned
        #     # else:
        #     #     b = st.data_editor(beforeDF, num_rows="dynamic", width=700, height=300)
        #     #     pages_utils.TempDataSet[4] = beforeDF
        #     # 选择后变化
        #     if st.button("Submit"):
        #         if isExtract:
        #             print('开始')
        #             onModelApplication(st.session_state["dataSet"])
        #         st.rerun()
        #
        #
        # if st.button("准备模型应用"):
        #     vote()

        st.markdown('---')
        st.markdown("##### 可视化结果")
        # if btn33:
        #     chart_data = pd.DataFrame(np.cumsum(np.random.randint(0, 2, size=(365, 1))), columns=["病株率(%)"])
        #     st.line_chart(chart_data)
