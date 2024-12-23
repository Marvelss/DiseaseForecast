"""
@Author : SakuraFox
@Time: 2024-04-09 15:37
@File : WeatherGenerator.py
@Description : 天气情景生成器
"""
import datetime
import os.path

import joblib
import scipy
import streamlit as st
import numpy as np
import pandas as pd
import matlab.engine
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from st_pages import hide_pages
from streamlit_pills import pills

from lib.share import RESOURCE_TEMPLATE_PATH, RESOURCE_PROCESS_PATH, RESOURCE_IMAGES_PATH, RESOURCE_TEMPDIR_PATH, \
    RESOURCE_MODELRESULT_PATH, MATLAB_FILE_PATH
from pages.modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod

from pages import pages_utils

st.set_page_config(
    layout="wide"
)

hide_pages(
    [
        "测试界面",
        "原始数据-面状",
        "数据预处理-面状",
        "特征计算-面状",
        "特征优选-面状",
        "模型构建-面状",
        "基于天气情景生成器的模型评价-面状",
        "建模报告-面状",
        "模型应用-面状",
        "数据下载中心-面状",
    ]
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr2 {display: none;}
    </style>
    """, unsafe_allow_html=True)
st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)

if 'page16' not in st.session_state:
    st.session_state.page16 = 0

# 情景对应异常程度参数表
if 'weatherSituationParams' not in st.session_state:
    st.session_state.weatherSituationParams = {
        '高温多雨': [2.5, 3.0, 90, 95],
        '高温常雨': [2.5, 3.0, 0, 0],
        '高温少雨': [2.5, 3.0, -90, -95],
        '常温常雨': [0.0, 0.0, 0, 0],
        '常温多雨': [0.0, 0.0, 90, 95],
        '常温少雨': [0.0, 0.0, -90, -95],
        '低温少雨': [-2.5, -3.0, -90, -95],
        '低温常雨': [-2.5, -3.0, 0, 0],
        '低温多雨': [-2.5, -3.0, 90, 95]
    }

# 应用原始数据
if "applicationDataSetPoint" not in st.session_state:
    st.session_state.historicalWeatherDataPoint = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
if "predictDFResult" not in st.session_state:
    st.session_state.predictDFResult = None

# 基于天气情景生成器的模型评价,包含xlsx结果路径和指标值
# 模型名称+天气情景:[path,Dev_s]
if 'modelSituationIndexResult' not in st.session_state:
    st.session_state.modelSituationIndexResult = {}

if 'modelReportWeatherInfo' not in st.session_state:
    st.session_state.modelReportWeatherInfo = {
        '经度': None,
        '纬度': None,
        '年限': None,
        '情景': None,
        '模型': None,
    }
st.markdown(
    """
    <style>
    h2 {
        margin-top: -100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.header('多场景作物病虫害快速预测建模系统')

# 显示可视化中文图例
plt.rcParams['font.sans-serif'] = 'SimHei'


# 替换气象数据(以DayOfYear为单位)
def replace_data(df1, df2):
    df1T = df1.copy()
    # 根据条件筛选并替换原始数据表格中的值
    for index, row in df2.iterrows():
        condition = (df1T['经度'] == row['经度']) & (df1T['纬度'] == row['纬度']) & \
                    (df1T['年'] == row['年']) & (df1T['DayOfYear'] == row['DayOfYear'])
        df1T.loc[condition, '降水'] = round(row['降水'], 2)
        df1T.loc[condition, '温度'] = round(row['温度'], 2)
    return df1T


# 替换气象数据(指定时段,年为单位)
# def replace_data2(df1, df2):
#     df1T = df1.copy()
#     df2.columns.tolist()
#     # 根据条件筛选并替换原始数据表格中的值
#     for index, row in df2.iterrows():
#         condition = (df1T['经度'] == row['经度']) & (df1T['纬度'] == row['纬度']) & \
#                     (df1T['年'] == row['年'])
#         df1T.loc[condition, '3月下旬温度'] = round(row['3月下旬温度'], 2)
#         df1T.loc[condition, '4月上旬温度'] = round(row['4月上旬温度'], 2)
#         df1T.loc[condition, '4月中旬温度'] = round(row['4月中旬温度'], 2)
#         df1T.loc[condition, '4月下旬温度'] = round(row['4月下旬温度'], 2)
#         df1T.loc[condition, '5月上旬温度'] = round(row['5月上旬温度'], 2)
#         df1T.loc[condition, '5月中旬温度'] = round(row['5月中旬温度'], 2)
#         df1T.loc[condition, '5月下旬温度'] = round(row['5月下旬温度'], 2)
#         df1T.loc[condition, '6月上旬温度'] = round(row['6月上旬温度'], 2)
#     return df1T


# 计算旬温度
# def getPeriodTemperature(df, year, longitude, latitude):
#     # 定义分段的时间范围
#     result = {}
#     # 定义不同时间段的范围
#     march_late = df[(df['DayOfYear'] >= 79) & (df['DayOfYear'] <= 90)]
#     april_early = df[(df['DayOfYear'] >= 91) & (df['DayOfYear'] <= 100)]
#     april_mid = df[(df['DayOfYear'] >= 101) & (df['DayOfYear'] <= 110)]
#     april_late = df[(df['DayOfYear'] >= 111) & (df['DayOfYear'] <= 120)]
#     may_early = df[(df['DayOfYear'] >= 121) & (df['DayOfYear'] <= 130)]
#     may_mid = df[(df['DayOfYear'] >= 131) & (df['DayOfYear'] <= 140)]
#     may_late = df[(df['DayOfYear'] >= 141) & (df['DayOfYear'] <= 150)]
#     june_early = df[(df['DayOfYear'] >= 151) & (df['DayOfYear'] <= 160)]
#
#     # 加入年、经度、纬度信息
#     result['经度'] = longitude
#     result['纬度'] = latitude
#     result['年'] = year
#
#     # 计算每个时间段的平均温度并存入字典
#     result['3月下旬温度'] = march_late['温度'].mean()
#     result['4月上旬温度'] = april_early['温度'].mean()
#     result['4月中旬温度'] = april_mid['温度'].mean()
#     result['4月下旬温度'] = april_late['温度'].mean()
#     result['5月上旬温度'] = may_early['温度'].mean()
#     result['5月中旬温度'] = may_mid['温度'].mean()
#     result['5月下旬温度'] = may_late['温度'].mean()
#     result['6月上旬温度'] = june_early['温度'].mean()
#
#     return pd.DataFrame([result])


# 获取每个情景多年模拟气象数据
# def getSimulateWeather(weatherSituation, province, station, startYear, periodFlag):
#     modelPathRoot = os.path.join(RESOURCE_PROCESS_PATH,
#                                  'weatherGeneratorOutput')
#
#     fileDirPath = os.path.join(modelPathRoot, weatherSituation)
#     merged_data = None
#     merged_data1 = None
#
#     for fileTemp in os.listdir(fileDirPath):
#         # Get the file name
#         file_name = os.path.join(fileDirPath, fileTemp)
#         yearNum = fileTemp.split('年')[0].split('第')[1]
#         data = pd.read_excel(file_name)
#         # print(yearNum)
#         # startYear = 2011  # 测试
#         data['年'] = int(yearNum) + int(startYear) - 1
#         if merged_data is None:
#             merged_data = data.copy()  # Initialize merged_data with the first file's data
#         # Read the Excel file
#         else:
#             # print(merged_data)
#             # Merge the data using the 'left' method
#             merged_data = pd.merge(merged_data, data, how='outer')
#         # Add additional columns
#         merged_data['经度'] = province
#         merged_data['纬度'] = station
#         # Calculate average temperature
#         merged_data['温度'] = (merged_data['最高温度'] + merged_data['最低温度']) / 2
#         if periodFlag:
#             temp_result = getPeriodTemperature(merged_data, int(yearNum) + int(startYear) - 1, province, station)
#             # 将文件数据与旬温度数据合并
#             if merged_data1 is None:
#                 merged_data1 = temp_result.copy()  # 初始化 merged_data
#             else:
#                 merged_data1 = pd.merge(merged_data1, temp_result, how='outer')
#         else:
#             merged_data1 = merged_data
#     return merged_data1


# 获取模型
def getModel(modelName):
    modelPathRoot = os.path.join(RESOURCE_MODELRESULT_PATH, 'structure')
    modelPath = os.path.join(modelPathRoot, modelName + '_structure.pkl')
    # print(modelPath)
    if os.path.exists(modelPath):
        # 加载已经训练好的模型
        return joblib.load(modelPath)
    else:
        return None


# =======================调用matlab天气情景生成器并保存结果数据=======================
# 调用matlab程序
def onGetWeatherData(year, selectedWeatherScenesList, weatherSituationParams, trainedModelsList):
    with st.spinner('开始生成模拟气象数据'):
        # 情景转换为对应数字
        weatherNumList = pages_utils.getWeatherNum(selectedWeatherScenesList)
        eng = matlab.engine.start_matlab()
        eng.cd(MATLAB_FILE_PATH, nargout=0)
        simulateDataDirRoot = os.path.join(RESOURCE_PROCESS_PATH, 'weatherGeneratorOutput')
        # 清空上一次生成数据
        pages_utils.delete_files_in_folder(simulateDataDirRoot)
        for weatherNum, weatherScene in zip(weatherNumList, selectedWeatherScenesList):
            sceneDataDir = os.path.join(simulateDataDirRoot, weatherScene)
            # 检查文件夹是否存在
            if not os.path.exists(sceneDataDir):
                # 创建文件夹
                os.mkdir(sceneDataDir)
            ParamsTemp = weatherSituationParams[weatherScene]
            sigama, sigama_max, PA, PA_max = (ParamsTemp[0],
                                              ParamsTemp[1],
                                              ParamsTemp[2] * 0.01,
                                              ParamsTemp[3] * 0.01)
            print('天气情景生成器输入参数')
            print(sigama)
            print(sigama_max)
            print(PA)
            print(PA_max)
            eng.myPython('0', 'out', year, weatherNum, sigama, sigama_max, PA, PA_max,
                         nargout=1)
            # matlab返回结果
            # 读取数据
            pathM = os.path.join(MATLAB_FILE_PATH, 'out.mat')
            # 加载结果
            mat = scipy.io.loadmat(pathM)
            data1 = np.array((mat['gP']))
            data2 = np.array(mat['gTmax'])
            data3 = np.array(mat['gTmin'])
            for tempi in range(len(data1)):
                tempPath = os.path.join(sceneDataDir, '第' + str(tempi + 1) + '年.xlsx')
                # 创建DayOfYear列
                day_of_year = range(1, 366)
                # 将数据转换为DataFrame
                my_large_df = pd.DataFrame({
                    'DayOfYear': day_of_year,
                    '降水': data1[tempi].flatten(),
                    '最高温度': data2[tempi].flatten(),
                    '最低温度': data3[tempi].flatten()
                })
                # 替换大于500的异常值为0
                my_large_df['降水'] = my_large_df['降水'].apply(lambda x: 0 if x > 500 else x)
                my_large_df.to_excel(tempPath, index=False)
            st.toast(f'{weatherScene}情景数据准备完毕', icon='✅')

        eng.exit()
        st.session_state.page16 += 1
        st.toast('运行完成,所有数据准备完毕', icon='✅')
        st.write('数据生成完毕,准备运行各环节方法和计算评价指标')
        # =========================替换模拟气象数据=========================
        # 用户输入:经度、纬度、年份范围
        # province = 117.4957
        # station = 30.5089
        # sd, ed = '2010', '2010'
        # ===============================================================


def onRun():
    # 获取精度最优模型
    max_r_index = max(enumerate(pages_utils.TempDataSetField[4]['评价指标'].tolist()), key=lambda x: x[1]['R方'])[0]
    # print(modelsList[max_r_index])

    # for tempModel, featureListTT1 in zip(modelsList, featureListT1):
    model = joblib.load(
        os.path.join(RESOURCE_MODELRESULT_PATH, 'structure',
                     f'{modelsList[max_r_index]}_structure.pkl'))
    # 假设在训练模型时保存了特征名称，可以将它们存储在一个列表中并加载

    predictions = model.predict(predictDF1[featureListT1[max_r_index]])
    print("基于模型气象数据的应用结果:", predictions)
    predictDF1["模型应用结果"] = predictions
    st.session_state.predictDFResult = predictDF1

    # filtered_df = st.session_state.historicalWeatherDataPoint[
    #     (st.session_state.historicalWeatherDataPoint['经度'] == weatherGeneratorProvinceSelected) &
    #     (st.session_state.historicalWeatherDataPoint['纬度'] == weatherGeneratorStationSelected)]
    # resultTempPath = os.path.join(
    #     RESOURCE_MODELRESULT_PATH,
    #     'modelsSimulateWeatherIndexResult',
    #     str(tempModel) + '_' + weatherScenes +
    #     '_applicationPredict' +
    #     '.xlsx')
    # filtered_df.to_excel(resultTempPath, index=False)

    # =========================计算静态偏差指标=========================
    st.toast(f'{modelsList[max_r_index]}模型评测完毕', icon='✅')
    # 计算指标
    # data_B = st.session_state.historicalWeatherDataPoint['实际标签']  # 实际
    # data_A = dataPAData['Predicted_value']  # 预测
    # # 计算两组数据相减的均值之和除以长度
    # mean_diff = ((data_A - data_B).sum()) / len(data_A)
    #
    # # 计算数据 A 的标准差之和除以长度
    # std_dev_B = data_B.std() / len(data_B)
    #
    # # print(f"预测值与实际发生程度之差的均值: {mean_diff}")
    # # print(f"实际发生程度的标准差: {std_dev_B}")
    # # print(f'Dev_s:{round(mean_diff / std_dev_B, 3)}')
    # st.session_state.modelSituationIndexResult[str(tempModel) + '_' + weatherScenes] = [
    #     resultTempPath, round(mean_diff / std_dev_B, 3)]
    # st.toast(f'{weatherScenes}---{tempModel}模型评测完毕\n'
    #          f'Dev_s:{round(mean_diff / std_dev_B, 3)}', icon='✅')


# ==============================界面==============================
st.markdown("##### 历史气象与标签数据上传")
weatherGeneratorProvinceSelected = None
weatherGeneratorStationSelected = None
modelsList = []
featureListT1 = []
# weatherGeneratorProvinceSelected = pages_utils.TempDataSet[4]['经度'].drop_duplicates().tolist()[0]
# weatherGeneratorStationSelected = pages_utils.TempDataSet[4]['纬度'].drop_duplicates().tolist()[0]
# modelsList = pages_utils.TempDataSetField[4]['模型'].tolist()
# featureListT1 = pages_utils.TempDataSetField[4]['特征'].tolist()

# weatherGeneratorInfo, weatherGeneratorInstruction = st.columns(2)
# with weatherGeneratorInfo:
#     st.markdown("###### 选择地区")
#     weatherGeneratorProvinceSelected = st.selectbox(
#         label='province',
#         options=pages_utils.TempDataSet[4]['经度'].drop_duplicates().tolist(),
#         label_visibility='collapsed')
#
#     weatherGeneratorStationSelected = st.selectbox(
#         label='station',
#         options=pages_utils.TempDataSet[4]['纬度'].drop_duplicates().tolist(),
#         label_visibility='collapsed')
#
#     if not len(pages_utils.TempDataSet[4]['经度'].drop_duplicates().tolist()):
#         st.toast('请先完成模型构建,再进行地区与模型选择', icon="⚠️")
st.session_state.modelReportWeatherInfo['经度'] = weatherGeneratorProvinceSelected
st.session_state.modelReportWeatherInfo['纬度'] = weatherGeneratorStationSelected
# with weatherGeneratorInstruction:
#     st.markdown("###### 选择待评价模型")
#     modelsList = pages_utils.multiselect_all(
#         st, '全选-模型',
#         pages_utils.TempDataSetField[4]['模型'].tolist(),
#         'tempModels', 'collapsed')
# st.session_state.modelReportWeatherInfo['模型'] = modelsList
col123, col223 = st.columns(2)
with col123:
    st.markdown("###### 上传历史气象站点数据")
    # 上传历史气象数据
    uploadedHistoricalData = st.file_uploader(
        "上传历史气象站点数据",
        accept_multiple_files=False,
        type=['xlsx', 'xls'],
        help='help',
        label_visibility='collapsed'
    )
    if uploadedHistoricalData:
        bytes_data = uploadedHistoricalData.read()
        st.session_state.historicalWeatherDataPoint = pd.read_excel(bytes_data)

        # S2021011922052305962

with col223:
    warningMInfo = '''
    注意事项:目前只支持单个地区多年数据上传
    '''
    st.markdown("###### 模板下载")
    col2331, col2332 = st.columns([2, 1])
    with col2331:
        st.warning(warningMInfo, icon="⚠️")
    with col2332:
        path2 = os.path.join(
            RESOURCE_TEMPLATE_PATH, '上传历史数据集模板-测试.xlsx')
        with open(path2, "rb") as file:
            st.download_button(
                label="下载历史站点气象数据模板",
                data=file,
                file_name="历史气象数据模板.xlsx",
                mime="application/octet-stream"
            )

st.markdown('---')
st.markdown("##### 天气情景生成器参数设置")
# ==============================时间长度==============================
# 获取年限
yearTemp = list(set(pages_utils.TempDataSet[4]['年'].tolist()))
if yearTemp:
    yearLength = len(yearTemp)
    startYearT = min(yearTemp)
else:
    yearLength = 0
    startYearT = 2024
today = datetime.datetime.now()
jan_1 = datetime.date(startYearT, 1, 1)
dec_31 = datetime.date(startYearT + yearLength, 12, 31)
st.markdown("###### 生成数据长度")
colYear1, colYear2 = st.columns(2)
with colYear1:
    # 检测 :读取标签数据集并提示最小输入年限
    generatedYears = st.date_input(
        "选择起止年月",
        (jan_1, dec_31),
        jan_1,
        dec_31,
        format="YYYY.MM.DD", label_visibility='collapsed'
    )

    # 检测数据长度至少比模型数据多
    year_difference = generatedYears[1].year - generatedYears[0].year
    if year_difference < yearLength:
        st.toast(f'生成数据较短,请延迟至少{yearLength}', icon="⚠️")
    # print(f'生成年份长度:{year_difference}')
    st.session_state.modelReportWeatherInfo['年限'] = year_difference

with colYear2:
    st.warning('注意事项:生成年份需要与模型训练数据集内部年份相对应', icon="⚠️")

st.markdown("###### 生成模拟气象情景")
# ==============================生成气象情景==============================
weatherScenesList = pages_utils.multiselect_all(
    st, '全选',
    [
        '常温常雨', '高温多雨', '高温常雨', '高温少雨',
        '常温多雨', '常温少雨',
        '低温少雨', '低温常雨', '低温多雨'],
    'temp111', 'collapsed')
if not weatherScenesList:
    weatherScenesList = ['常温常雨']

st.session_state.modelReportWeatherInfo['情景'] = weatherScenesList

st.markdown("###### 异常程度设置")
# ==============================异常程度设置==============================
# ********************气温标准差********************
selectedWeather = pills("异常程度设置", weatherScenesList, label_visibility='collapsed')

# 获取天气情景对应异常程度值
anomalyValue = st.session_state.weatherSituationParams.get(selectedWeather)
col1231, col1232 = st.columns(2)
with col1231:
    st.info(
        '标准差气温评价指标和等级:  \n'
        '* 异常偏低:$$\Delta T<-2.0\sigma$$  \n* 明显偏低:$$-2.0\sigma \leq \Delta T<-1.5\sigma$$  \n'
        '* 偏低:$$-1.5\sigma \leq \Delta T<-0.5\sigma$$  \n* 正常(接近常年):$$-0.5\sigma \leq \Delta T\leq 0.5\sigma$$  \n'
        '* 偏高:$$0.5\sigma \leq \Delta T \leq1.5\sigma$$  \n* 明显偏高:$$1.5\sigma \leq \Delta T \leq2.0\sigma$$  \n'
        '* 异常偏高:$$\Delta T>2.0\sigma$$', icon="ℹ️")
with col1232:
    number51 = st.number_input("气温标准差下限", value=anomalyValue[0], max_value=10.0, min_value=-10.0, step=0.1)
    number52 = st.number_input("气温标准差上限", value=anomalyValue[1], max_value=10.0, min_value=-10.0, step=0.1)
# ********************降水量距平百分率********************
col12313, col12323 = st.columns(2)
with col12313:
    st.info('降水量距平百分率干旱等级划分(月尺度):  \n'
            '* 无旱:$$-40<PA$$  \n* 轻旱:$$-60<PA \leq -40$$  \n'
            '* 中旱:$$-80<PA \leq -60$$  \n* 重旱:$$-95<PA \leq -80$$  \n'
            '* 特旱:$$PA \leq -95$$', icon="ℹ️")
with col12323:
    number53 = st.number_input("降水量距平百分率下限(PA)/%", value=anomalyValue[2], max_value=100, min_value=-100,
                               step=5)
    number54 = st.number_input("降水量距平百分率上限(PA)/%", value=anomalyValue[3], max_value=100, min_value=-100,
                               step=5)

# ********************保存异常程度参数********************
# 更新场景对应的值
st.session_state.weatherSituationParams[selectedWeather] = [number51, number52, number53, number54]
# 打印更新后的值
# st.markdown(st.session_state.weatherSituationParams[selectedWeather])


# sigama_temp, sigama_max_temp, PA_temp, PA_max_temp = number51, number53 * 0.01, number52, number54 * 0.01
# st.markdown('---')
# st.markdown("##### 执行记录及特征集选择")
# colPro1, colPro2 = st.columns([0.3, 0.7])
# with colPro1:
#     st.markdown('')
#     st.info('注意:  \n'
#             '1.特征计算  \n将右侧不需要执行的特征计算方法删除  \n'
#             '2.特征优选  \n根据优选特征列保留需要的特征  \n'
#             '3.点击运行程序按钮  \n生成模拟气象数据以进行模型应用得到预测结果', icon="ℹ️")

# with colPro2:
# 预处理
# 特征计算
# pages_utils.TempDataSetField[2] = pd.read_excel(path1)
# pages_utils.TempDataSetField[3] = pd.read_excel(path2)
# tab1, tab2, tab3 = st.tabs(["特征计算", "特征优选", "预处理"])
# with tab1:
#     featureCalculationLog = st.data_editor(
#         pages_utils.TempDataSetField[2],
#         height=190, width=900, num_rows="dynamic",
#         column_order=["输入特征", "特征计算方法", "备选特征", "数据类型", '时间'])
# with tab2:
#     # 特征优选(只取最优特征)
#     featureOptimalLog = st.data_editor(
#         pages_utils.TempDataSetField[3], height=190, width=900, num_rows="dynamic",
#         column_order=["优选特征", "特征优选方法", "数据类型", '时间'])
# with tab3:
#     pass

interval_col1, interval_col2 = st.columns([6, 1])
with interval_col2:
    btn = st.button('获取模拟气象数据', on_click=onGetWeatherData,
                    args=[float(year_difference), weatherScenesList, st.session_state.weatherSituationParams,
                          modelsList])
    if btn:
        zipPath = os.path.join(RESOURCE_TEMPDIR_PATH, '基于天气情景生成器的模拟数据.zip')
        # 压缩生成的xlsx数据
        pathEE = os.path.join(RESOURCE_PROCESS_PATH, 'weatherGeneratorOutput')
        pages_utils.zip_folder(pathEE, zipPath)
        with open(zipPath, "rb") as file:
            st.download_button(
                label="下载模拟生成的气象数据",
                data=file,
                file_name="基于天气情景生成器的模拟数据.zip",
                mime="application/zip",
            )
# =======================预测评价结果及数据下载=======================
st.markdown('---')
st.markdown("##### 上传特征与标签数据")

col12331, col22332 = st.columns(2)
with col12331:
    st.markdown("###### 上传特征数据")
    # 上传特征数据
    uploadedActualLabelData = st.file_uploader(
        "上传特征数据",
        accept_multiple_files=False,
        type=['xlsx', 'xls'],
        help='help',
        label_visibility='collapsed'
    )
    if uploadedActualLabelData:
        bytes_data = uploadedActualLabelData.read()
        predictDF1 = pd.read_excel(bytes_data)

with col22332:
    st.markdown("###### 上传实际标签数据")
    # 上传实际数据
    uploadedActualLabelData1 = st.file_uploader(
        "上传标签数据",
        accept_multiple_files=False,
        type=['xlsx', 'xls'],
        help='help',
        label_visibility='collapsed'
    )
    if uploadedActualLabelData1:
        bytes_data1 = uploadedActualLabelData.read()
        predictDF11 = pd.read_excel(bytes_data1)
    # warningMInfo = '''
    # 注意事项:根据上传的原始数据集字段填入数据
    # '''
    # # st.markdown("&nbsp;", unsafe_allow_html=True)
    # col233131, col233232 = st.columns([2, 1])
    # with col233131:
    #     st.warning(warningMInfo, icon="⚠️")
    # with col233232:
    #     # 根据模型构建最终数据集制作实际标签模板
    #     path2 = os.path.join(
    #         RESOURCE_TEMPLATE_PATH, '上传实际标签数据.xlsx')
    #
    #     dataTemplate = pages_utils.TempDataSet[4]
    #
    #     filteredTemplate = dataTemplate[
    #         (dataTemplate['经度'] == weatherGeneratorProvinceSelected) &
    #         (dataTemplate['纬度'] == weatherGeneratorStationSelected)]
    #
    #     # 只保留特定列，并加入实际标签列
    #     if 'DayOfYear' in filteredTemplate.columns.tolist():
    #         tempList = ['经度', '纬度', '年', 'DayOfYear']
    #     else:
    #         tempList = ['经度', '纬度', '年']
    #     filteredTemplate = filteredTemplate[tempList]
    #     filteredTemplate['实际标签'] = None  # 添加新的一列
    #
    #     filteredTemplate.to_excel(path2, index=False)
    #
    #     with open(path2, "rb") as file:
    #         st.download_button(
    #             label="下载数据集模板",
    #             data=file,
    #             file_name="下载实际标签数据模板.xlsx",
    #             mime="application/octet-stream"
    #         )

interval_col1, interval_col2 = st.columns([6, 1])
with interval_col2:
    btn = st.button('开始模型评估', on_click=onRun)

# 左侧表格,右侧可视化
# =======================预测评价结果及数据下载=======================
st.markdown('---')
st.markdown("##### 模型应用与评估结果可视化")
aaa = st.empty()
with aaa:
    st.table(st.session_state.predictDFResult)
# predictions = None
# if predictions:
#     st.table(predictDF1)
# st.markdown('###### 模型预测结果可视化')
#
# st.markdown('###### 评价指标结果可视化')
# with st.popover("效果图预览"):
#     img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'weatherGeneratorEvaluateResult2.jpg'))
#     st.image(img)
#     co3, co4 = st.columns(2)
#     with co3:
#         st.metric("Dev_S", "0.0799")
#     with co4:
#         st.metric("Dev_S", "0.0899")
# ==============================准备下载数据==============================
# if btn:


colIndex1, colIndex2, colIndex3 = st.columns(3)

# with st.container(height=700):
items = list(st.session_state.modelSituationIndexResult.items())
for i, (metric_name, metric_value) in enumerate(items):
    path = os.path.join(
        RESOURCE_MODELRESULT_PATH,
        'modelsSimulateWeatherIndexResult',
        metric_name +
        '_applicationPredict' +
        '.xlsx')
    modelNameT = metric_name.split('_')[0]
    weatherNameT = metric_name.split('_')[1]
    if i % 3 == 0:
        with colIndex1:
            df = pd.read_excel(path)
            if '病害发生程度' in df.columns.tolist():
                # Plotting
                fig, ax = plt.subplots(figsize=(10, 6))

                # 绘制 0 和 1 两类的散点图
                for label in [0, 1]:
                    subset = df[df['Predicted_value'] == label]  # 筛选数据
                    if label == 0:
                        labelStr = '不发生'
                        color = 'b'  # 蓝色表示 "不发生"
                    else:
                        labelStr = '发生'
                        color = 'r'  # 红色表示 "发生"

                    # 绘制散点图
                    ax.scatter(subset['年'], subset['Predicted_value'], label=f'病害{labelStr}', s=100, alpha=0.6,
                               color=color)

                # 添加标题和标签
                plt.title(f'基于{modelNameT}建模方法{weatherNameT}情景下预测病害发生情况')
                plt.xlabel('年')
                plt.ylabel('病害发生情况')
                # Set x-ticks to be integers
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                # 添加图例
                plt.legend()
                st.pyplot(plt)
            else:
                # Plotting
                fig, ax = plt.subplots(figsize=(10, 6))

                plt.plot(df['年'], df['峰值'], label='实际病害峰值', marker='o', color='blue')
                plt.plot(df['年'], df['Predicted_value'], label='预测病害峰值', marker='x', color='red')

                # 添加标题和标签
                plt.title(f'{weatherNameT}情景下实际与预测病害峰值对比图')
                plt.xlabel('年')
                plt.ylabel('病害峰值')
                # 设置 X 轴刻度为整数
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                # 添加图例
                plt.legend()
                st.pyplot(plt)
                st.metric(f'{metric_name}-Dev_S:', metric_value[1])
    elif i % 3 == 1:
        with colIndex2:
            df = pd.read_excel(path)
            if '病害发生程度' in df.columns.tolist():
                # Plotting
                fig, ax = plt.subplots(figsize=(10, 6))

                # 绘制 0 和 1 两类的散点图
                for label in [0, 1]:
                    subset = df[df['Predicted_value'] == label]  # 筛选数据
                    if label == 0:
                        labelStr = '不发生'
                        color = 'b'  # 蓝色表示 "不发生"
                    else:
                        labelStr = '发生'
                        color = 'r'  # 红色表示 "发生"

                    # 绘制散点图
                    ax.scatter(subset['年'], subset['Predicted_value'], label=f'病害{labelStr}', s=100, alpha=0.6,
                               color=color)

                # 添加标题和标签
                plt.title(f'基于{modelNameT}建模方法{weatherNameT}情景下预测病害发生情况')
                plt.xlabel('年')
                plt.ylabel('病害发生情况')
                # Set x-ticks to be integers
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                # 添加图例
                plt.legend()
                st.pyplot(plt)
            else:
                # Plotting
                fig, ax = plt.subplots(figsize=(10, 6))

                plt.plot(df['年'], df['峰值'], label='实际病害峰值', marker='o', color='blue')
                plt.plot(df['年'], df['Predicted_value'], label='预测病害峰值', marker='x', color='red')

                # 添加标题和标签
                plt.title(f'{weatherNameT}情景下实际与预测病害峰值对比图')
                plt.xlabel('年')
                plt.ylabel('病害峰值')
                # 设置 X 轴刻度为整数
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                # 添加图例
                plt.legend()
                st.pyplot(plt)
                st.metric(f'{metric_name}-Dev_S:', metric_value[1])
    else:
        with colIndex3:
            df = pd.read_excel(path)
            if '病害发生程度' in df.columns.tolist():
                # Plotting
                fig, ax = plt.subplots(figsize=(10, 6))

                # 绘制 0 和 1 两类的散点图
                for label in [0, 1]:
                    subset = df[df['Predicted_value'] == label]  # 筛选数据
                    if label == 0:
                        labelStr = '不发生'
                        color = 'b'  # 蓝色表示 "不发生"
                    else:
                        labelStr = '发生'
                        color = 'r'  # 红色表示 "发生"

                    # 绘制散点图
                    ax.scatter(subset['年'], subset['Predicted_value'], label=f'病害{labelStr}', s=100, alpha=0.6,
                               color=color)

                # 添加标题和标签
                plt.title(f'基于{modelNameT}建模方法{weatherNameT}情景下预测病害发生情况')
                plt.xlabel('年')
                plt.ylabel('病害发生情况')
                # Set x-ticks to be integers
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                # 添加图例
                plt.legend()
                st.pyplot(plt)
            else:
                # Plotting
                fig, ax = plt.subplots(figsize=(10, 6))

                plt.plot(df['年'], df['峰值'], label='实际病害峰值', marker='o', color='blue')
                plt.plot(df['年'], df['Predicted_value'], label='预测病害峰值', marker='x', color='red')

                # 添加标题和标签
                plt.title(f'{weatherNameT}情景下实际与预测病害峰值对比图')
                plt.xlabel('年')
                plt.ylabel('病害峰值')
                # 设置 X 轴刻度为整数
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                # 添加图例
                plt.legend()
                st.pyplot(plt)
                st.metric(f'{metric_name}-Dev_S:', metric_value[1])
