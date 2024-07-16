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
from PIL import Image
from sklearn.preprocessing import StandardScaler
from st_pages import hide_pages
from streamlit_pills import pills
from modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
from modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod

import pages_utils

st.set_page_config(
    layout="wide"
)
if st.session_state.isPlanarInterface:
    hide_pages(
        [
            "测试界面",
            "原始数据",
            "数据预处理",
            "特征计算",
            "特征优选",
        ]
    )
else:
    hide_pages(
        [
            "测试界面",
            "原始数据-面状",
            "数据预处理-面状",
            "特征计算-面状",
            "特征优选-面状",
        ]
    )
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
if "applicationDataSet" not in st.session_state:
    st.session_state.historicalWeatherData = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])

# 基于天气情景生成器的模型评价,包含xlsx结果路径和指标值
# 模型名称+天气情景:[path,Dev_s]
if 'modelSituationIndexResult' not in st.session_state:
    st.session_state.modelSituationIndexResult = {}


# 函数替换数据
def replace_data(df1, df2):
    # df1.to_excel('测试1.xlsx')
    # df2.to_excel('测试2.xlsx')
    df1T = df1.copy()
    # 根据条件筛选并替换原始数据表格中的值
    for index, row in df2.iterrows():
        condition = (df1T['上级单位'] == row['上级单位']) & (df1T['测报站点'] == row['测报站点']) & \
                    (df1T['年'] == row['年']) & (df1T['DayOfYear'] == row['DayOfYear'])
        df1T.loc[condition, '降水'] = round(row['降水'], 2)
        df1T.loc[condition, '温度'] = round(row['温度'], 2)
    return df1T


# 获取每个情景多年模拟气象数据
def getSimulateWeather(weatherSituation, province, station, startYear):
    modelPathRoot = os.path.join(os.getcwd(),
                                 'resource',
                                 'weatherGeneratorOutput')

    fileDirPath = os.path.join(modelPathRoot, weatherSituation)
    merged_data = None
    for fileTemp in os.listdir(fileDirPath):
        # Get the file name
        file_name = os.path.join(fileDirPath, fileTemp)
        yearNum = fileTemp.split('年')[0].split('第')[1]
        data = pd.read_excel(file_name)
        # print(yearNum)
        # startYear = 2011  # 测试
        data['年'] = int(yearNum) + int(startYear)
        if merged_data is None:
            merged_data = data.copy()  # Initialize merged_data with the first file's data
        # Read the Excel file
        else:
            # print(merged_data)
            # Merge the data using the 'left' method
            merged_data = pd.merge(merged_data, data, how='outer')
        # Add additional columns
        merged_data['上级单位'] = province
        merged_data['测报站点'] = station
        # Calculate average temperature
        merged_data['温度'] = (merged_data['最高温度'] + merged_data['最低温度']) / 2
    return merged_data


# 获取模型
def getModel(modelName):
    modelPathRoot = os.path.join(r'E:\a_python\program\diseaseForecastStreamlit',
                                 'resource',
                                 'modelsResults',
                                 'modelsStructure')
    modelPath = os.path.join(modelPathRoot, modelName + '_structure.pkl')
    # print(modelPath)
    if os.path.exists(modelPath):
        # 加载已经训练好的模型
        return joblib.load(modelPath)
    else:
        return None


# =======================调用matlab天气情景生成器并保存结果数据=======================
# 调用matlab程序
def onRun(year, selectedWeatherScenesList, weatherSituationParams, trainedModelsList):
    with st.spinner('开始生成模拟气象数据'):
        # 情景转换为对应数字
        weatherNumList = pages_utils.getWeatherNum(selectedWeatherScenesList)
        eng = matlab.engine.start_matlab()
        eng.cd(r'E:\a_python\program\testForMatlab\weather_generation', nargout=0)
        simulateDataDirRoot = r'E:\a_python\program\diseaseForecastStreamlit\resource\weatherGeneratorOutput'
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
            result = eng.myPython('0', 'out', year, weatherNum, sigama, sigama_max, PA, PA_max,
                                  nargout=1)
            # matlab返回结果
            # print(result)
            # 读取数据
            pathM = r'E:\a_python\program\testForMatlab\weather_generation\out.mat'
            # 加载结果
            mat = scipy.io.loadmat(pathM)
            data1 = np.array((mat['gP']))
            data2 = np.array(mat['gTmax'])
            data3 = np.array(mat['gTmin'])
            for i in range(len(data1)):
                tempPath = os.path.join(sceneDataDir, '第' + str(i + 1) + '年.xlsx')
                # 创建DayOfYear列
                day_of_year = range(1, 366)
                # 将数据转换为DataFrame
                my_large_df = pd.DataFrame({
                    'DayOfYear': day_of_year,
                    '降水': data1[i].flatten(),
                    '最高温度': data2[i].flatten(),
                    '最低温度': data3[i].flatten()
                })
                my_large_df.to_excel(tempPath, index=False)
            st.toast(f'{weatherScene}情景数据准备完毕', icon='✅')

        eng.exit()
        st.session_state.page16 += 1
        st.toast('运行完成,所有数据准备完毕', icon='✅')
        st.write('数据生成完毕,准备运行各环节方法和计算评价指标')
        # =========================替换模拟气象数据=========================
        # 用户输入:上级单位、测报站点、年份范围
        # province = '湖南省'
        # station = '湘阴县'
        # sd, ed = '2010', '2010'

        # 调用天气情景生成器,获取数据
        # 根据上级单位、测报站点、年份范围替换原始数据
        for weatherScenes in selectedWeatherScenesList:
            # 多个情景遍历, 这里目前用一个
            df3T = getSimulateWeather(
                weatherScenes,
                weatherGeneratorProvinceSelected,
                weatherGeneratorStationSelected,
                generatedYears[0].year)
            # df3T.to_excel(weatherScenes + '_' + 'weatherSimulate.xlsx', index=False)
            rawData = replace_data(pages_utils.TempDataSet[0], df3T)
            # print('=========================替换后数据=========================')
            # rawData.to_excel(weatherScenes + '_' + 'weatherReplaced.xlsx', index=False)
            # =========================特征计算及读取执行方法=========================
            # 读取记录
            featureCalculateDF = pages_utils.TempDataSetField[2]
            # featureCalculateDF = pd.read_excel(
            #     r'E:\a_python\program\diseaseForecastStreamlit\resource\预测病害峰值 - 测试模型应用\特征计算记录.xlsx')
            inputFeature1 = featureCalculateDF["输入特征"].tolist()
            # outputFeature1 = featureCalculateDF["备选特征"].tolist()
            featureCalculateList = featureCalculateDF["特征计算方法"].tolist()
            modelParam1 = featureCalculateDF["方法参数"].tolist()
            # print(modelParam1)
            for indexT, tempMethod in enumerate(featureCalculateList):
                # 使用处理后最新的字段内容
                reservedField = rawData.columns.tolist()
                # print('===========检测===========')
                # print(rawData)
                # print(reservedField)
                tool1 = FeatureCalculationMethod(rawData, reservedField)
                if tempMethod == '降雨日数计算':
                    rawData, newColumn = tool1.rainfallDaysAccumulation(
                        [inputFeature1[indexT]], modelParam1[indexT])
                    # 若自定义上传excel此处需要modelParam1[indexT].split(','),下方特征计算和模型同理
                elif tempMethod == '降水累积量计算':

                    rawData, newColumn = tool1.precipitationAccumulation(
                        [inputFeature1[indexT]], modelParam1[indexT])

            print(f'=============特征字段计算完成=============')
            # rawData.to_excel(r'E:\a_python\program\diseaseForecastStreamlit\resource\uploadFileDir\featureCalculated.xlsx')
            # =========================特征优选及读取执行方法=========================
            featureOptimalDF = pages_utils.TempDataSetField[3]
            # featureOptimalDF = pd.read_excel(
            #     r'E:\a_python\program\diseaseForecastStreamlit\resource\预测病害峰值 - 测试模型应用\特征优选记录.xlsx')

            inputFeature2 = featureOptimalDF["输入特征"].tolist()
            # outputFeature2 = featureOptimalDF["优选特征"].tolist()
            featureOptimalList = featureOptimalDF["特征优选方法"].tolist()
            modelParam2 = featureOptimalDF["方法参数"].tolist()

            # print('==========测试列=============')
            # print(rawData.columns)
            # print(type(rawData.columns))
            tool2 = FeatureOptimizationMethod(rawData, rawData.columns.tolist())
            # 初始化特征优选方法
            for indexT, tempMethod in enumerate(featureOptimalList):
                if tempMethod == 'Pearson相关性分析':
                    # print('=============Pearson相关性分析检测============')
                    # print(modelParam2[indexT].split(','))
                    rawData, _ = tool2.Pearson(modelParam2[indexT])
                elif tempMethod == 'Relief-F互相关分析':
                    rawData, _ = tool2.ReliefF(
                        modelParam2[indexT])

            print(f'=============特征字段优选完成=============')
            # rawData.to_excel(r'E:\a_python\program\diseaseForecastStreamlit\resource\uploadFileDir\featureOptimized.xlsx')

            # =========================提取有效值=========================
            # 使用groupby分组并提取每个分组的第一个非空值
            ultimateFeatures = rawData.groupby(['上级单位', '测报站点', '年']).first().reset_index()
            # ******删除包含缺失值的行******
            df_cleaned = ultimateFeatures.dropna()

            print('=============提取有效值=============')
            # df_cleaned.to_excel(r'E:\a_python\program\diseaseForecastStreamlit\resource\uploadFileDir\ultimateFeatures.xlsx')

            # =========================模型构建及读取执行方法=========================
            modelDF = pages_utils.TempDataSetField[4]
            # modelDF = pd.read_excel(
            #     r'E:\a_python\program\diseaseForecastStreamlit\resource\预测病害峰值 - 测试模型应用\最后-模型记录.xlsx')

            models = modelDF["模型"].tolist()
            # modelsParam = modelDF["模型参数"].tolist()
            feature = modelDF["特征"].tolist()
            label = modelDF["标签"].tolist()
            # precision = modelDF["评价指标"].tolist()
            # ratio = modelDF["数据集划分比例"].tolist()
            for indexT, (tempModel, tempFeature,
                         tempLabel) in enumerate(zip(models, feature, label)):
                # 只运行指定模型
                if tempModel not in trainedModelsList:
                    continue
                # 模型读取
                model = getModel(tempModel)
                inputDF = df_cleaned[tempFeature]
                # print('=============测试数据集====')
                # print(inputDF)
                # 筛选出省份为'湖南省'和测报站点为'湘阴县'的所有行(不能删除,否则少特征)
                # filtered_df = df_cleaned[(df_cleaned['上级单位'] == province) & (df_cleaned['测报站点'] == station)]
                # 选取包含在 tempFeature 中的列
                # inputDF = filtered_df[tempFeature]
                # print(model)
                X = None
                if '上级单位' and '测报站点' in tempFeature:
                    X = pd.get_dummies(inputDF, columns=['上级单位', '测报站点'])
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                # 接下来您可以使用X_scaled进行进一步的模型训练和预测
                # model.predict() 方法需要接受和训练时相同的特征列
                predictions = model.predict(X_scaled)
                # 创建一个 DataFrame 包含预测值
                predictions_df = pd.DataFrame(predictions, columns=['Predicted_value'])
                # 重新调整表格索引,以确保predictions_df与df_cleaned合并大小一致
                df_cleaned_reset = df_cleaned.reset_index(drop=True)
                predictions_df_reset = predictions_df.reset_index(drop=True)
                # 合并两表
                data = pd.concat([df_cleaned_reset, predictions_df_reset], axis=1)
                # 提取指定区域的相关数据
                # print('-------------测试指定地区-------------')
                # print(weatherGeneratorProvinceSelected)
                # print(weatherGeneratorStationSelected)
                filtered_df = data[
                    (data['上级单位'] == weatherGeneratorProvinceSelected) &
                    (data['测报站点'] == weatherGeneratorStationSelected)]

                resultTempPath = os.path.join(
                    os.getcwd(),
                    'resource',
                    'modelsResults',
                    'modelsSimulateWeatherIndexResult',
                    str(tempModel) + '_'
                    + weatherScenes +
                    '_applicationPredict' +
                    '.xlsx')
                filtered_df.to_excel(resultTempPath, index=False)

                # =========================计算静态偏差指标=========================
                # 计算指标
                data_B = st.session_state.historicalWeatherData['实际标签']  # 实际
                data_A = filtered_df['Predicted_value']  # 预测
                # 计算两组数据相减的均值之和除以长度
                mean_diff = ((data_A - data_B).sum()) / len(data_A)

                # 计算数据 A 的标准差之和除以长度
                std_dev_B = data_B.std() / len(data_B)

                # print(f"预测值与实际发生程度之差的均值: {mean_diff}")
                # print(f"实际发生程度的标准差: {std_dev_B}")
                # print(f'Dev_s:{round(mean_diff / std_dev_B, 3)}')
                st.session_state.modelSituationIndexResult[str(tempModel) + '_' + weatherScenes] = [
                    resultTempPath, round(mean_diff / std_dev_B, 3)]
                st.toast(f'{weatherScenes}---{tempModel}模型评测完毕\n'
                         f'Dev_s:{round(mean_diff / std_dev_B, 3)}', icon='✅')
        # st.markdown(st.session_state.modelSituationIndexResult)


# ==============================界面==============================
st.markdown("##### 指定地区及模型与数据上传")

weatherGeneratorInfo, weatherGeneratorInstruction = st.columns(2)
with weatherGeneratorInfo:
    st.markdown("###### 选择地区")
    weatherGeneratorProvinceSelected = st.selectbox(
        label='province',
        options=pages_utils.TempDataSet[4]['上级单位'].drop_duplicates().tolist(),
        label_visibility='collapsed')
    weatherGeneratorStationSelected = st.selectbox(
        label='station',
        options=pages_utils.TempDataSet[4]['测报站点'].drop_duplicates().tolist(),
        label_visibility='collapsed')

with weatherGeneratorInstruction:
    st.markdown("###### 选择待评价模型")
    modelsList = pages_utils.multiselect_all(
        st, '全选-模型',
        pages_utils.TempDataSetField[4]['模型'].tolist(),
        'tempModels', 'collapsed')
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
            os.getcwd(), 'resource', '上传历史数据集模板-测试.xlsx')
        with open(path2, "rb") as file:
            st.download_button(
                label="下载历史站点气象数据模板",
                data=file,
                file_name="历史气象数据模板.xlsx",
                mime="application/octet-stream"
            )

col12331, col22332 = st.columns(2)
with col12331:
    st.markdown("###### 上传实际标签数据")
    # 上传实际标签数据
    uploadedActualLabelData = st.file_uploader(
        "上传实际标签数据",
        accept_multiple_files=False,
        type=['xlsx', 'xls'],
        help='help',
        label_visibility='collapsed'
    )
    if uploadedActualLabelData:
        bytes_data = uploadedActualLabelData.read()
        st.session_state.historicalWeatherData = pd.read_excel(bytes_data)

with col22332:
    warningMInfo = '''
    注意事项:根据上传的原始数据集字段填入数据
    '''
    st.markdown("&nbsp;", unsafe_allow_html=True)
    col233131, col233232 = st.columns([2, 1])
    with col233131:
        st.warning(warningMInfo, icon="⚠️")
    with col233232:
        # 根据模型构建最终数据集制作实际标签模板
        path2 = os.path.join(
            os.getcwd(), 'resource', 'uploadFileDir', '上传实际标签数据.xlsx')

        dataTemplate = pages_utils.TempDataSet[4]

        filteredTemplate = dataTemplate[
            (dataTemplate['上级单位'] == weatherGeneratorProvinceSelected) &
            (dataTemplate['测报站点'] == weatherGeneratorStationSelected)]

        # 只保留特定列，并加入实际标签列
        filteredTemplate = filteredTemplate[['上级单位', '测报站点', '年', 'DayOfYear']]
        filteredTemplate['实际标签'] = None  # 添加新的一列

        filteredTemplate.to_excel(path2, index=False)

        with open(path2, "rb") as file:
            st.download_button(
                label="下载实际标签数据模板",
                data=file,
                file_name="下载实际标签数据模板.xlsx",
                mime="application/octet-stream"
            )

st.markdown('---')
st.markdown("##### 天气情景生成器参数设置")
# ==============================时间长度==============================
today = datetime.datetime.now()
jan_1 = datetime.date(today.year - 13, 1, 1)
dec_31 = datetime.date(today.year, 12, 31)
st.markdown("###### 生成数据长度")
colYear1, colYear2 = st.columns(2)
with colYear1:
    generatedYears = st.date_input(
        "选择起止年月",
        (jan_1, datetime.date(today.year - 12, 1, 7)),
        jan_1,
        dec_31,
        format="YYYY.MM.DD", label_visibility='collapsed'
    )
    year_difference = generatedYears[1].year - generatedYears[0].year
    print(f'生成年份长度:{year_difference}')
with colYear2:
    st.warning('注意事项:生成年份需要与模型训练数据集内部年份相对应', icon="⚠️")
# print('----------')
# print(float(generatedYears), float(weatherScenes))

# st.info('生成的气象情景:\n'
#         '* 1:高温多雨 2:高温常雨 3:高温少雨\n'
#         '* 4:常温常雨 5:常温多雨 6:常温少雨\n'
#         '* 7:低温少雨 8:低温常雨 9:低温多雨\n', icon="ℹ️")
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

st.markdown("###### 异常程度设置")
# ==============================异常程度设置==============================
# ============================气温标准差============================
selectedWeather = pills("异常程度设置", weatherScenesList, label_visibility='collapsed')

# 获取天气情景对应异常程度值
anomalyValue = st.session_state.weatherSituationParams.get(selectedWeather)
col1231, col1232 = st.columns(2)
with col1231:
    st.info('标准差气温评价指标和等级:\n'
            '* 异常偏低:$$\Delta T<-2.0\sigma$$       \n* 明显偏低:$$-2.0\sigma \leq \Delta T<-1.5\sigma$$      \n'
            '* 偏低:$$-1.5\sigma \leq \Delta T<-0.5\sigma$$      \n* 正常(接近常年):$$-0.5\sigma \leq \Delta T\leq 0.5\sigma$$      \n'
            '* 偏高:$$0.5\sigma \leq \Delta T \leq1.5\sigma$$       \n* 明显偏高:$$1.5\sigma \leq \Delta T \leq2.0\sigma$$      \n'
            '* 异常偏高:$$\Delta T>2.0\sigma$$', icon="ℹ️")
with col1232:
    number51 = st.number_input("气温标准差下限", value=anomalyValue[0], max_value=10.0, min_value=-10.0, step=0.1)
    number52 = st.number_input("气温标准差上限", value=anomalyValue[1], max_value=10.0, min_value=-10.0, step=0.1)
# ============================降水量距平百分率============================
col12313, col12323 = st.columns(2)
with col12313:
    st.info('降水量距平百分率干旱等级划分(月尺度):\n'
            '* 无旱:$$-40<PA$$       \n* 轻旱:$$-60<PA \leq -40$$      \n'
            '* 中旱:$$-80<PA \leq -60$$      \n* 重旱:$$-95<PA \leq -80$$      \n'
            '* 特旱:$$PA \leq -95$$', icon="ℹ️")
with col12323:
    number53 = st.number_input("降水量距平百分率下限(PA)/%", value=anomalyValue[2], max_value=100, min_value=-100,
                               step=5)
    number54 = st.number_input("降水量距平百分率上限(PA)/%", value=anomalyValue[3], max_value=100, min_value=-100,
                               step=5)

# =============================保存异常程度参数==============================
# 更新场景对应的值
st.session_state.weatherSituationParams[selectedWeather] = [number51, number52, number53, number54]
# 打印更新后的值
# st.markdown(st.session_state.weatherSituationParams[selectedWeather])


sigama_temp, sigama_max_temp, PA_temp, PA_max_temp = number51, number53 * 0.01, number52, number54 * 0.01

btn = st.button('运行程序', on_click=onRun,
                args=[float(year_difference), weatherScenesList, st.session_state.weatherSituationParams, modelsList])

# =======================预测评价结果及数据下载=======================
st.markdown('---')
st.markdown("##### 模型评价指标结果及可视化")
with st.popover("效果图预览"):
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', 'weatherGeneratorEvaluateResult2.jpg'))
    st.image(img)
    co3, co4 = st.columns(2)
    with co3:
        st.metric("Dev_S", "0.0799")
    with co4:
        st.metric("Dev_S", "0.0899")
# ==============================准备下载数据==============================
if btn:
    zipPath = r'E:\a_python\program\diseaseForecastStreamlit\resource\基于天气情景生成器的模拟数据.zip'
    # 压缩生成的xlsx数据
    pathEE = r'E:\a_python\program\diseaseForecastStreamlit\resource\weatherGeneratorOutput'
    pages_utils.zip_folder(pathEE, zipPath)
    with open(zipPath, "rb") as file:
        st.download_button(
            label="下载模拟生成的气象数据",
            data=file,
            file_name="基于天气情景生成器的模拟数据.zip",
            mime="application/zip",
        )

# tab11, tab12 = st.tabs(['模型1', '模型2'])
colRes1, colRes2 = st.columns(2)
st.markdown('###### 静态偏差指标')

img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', 'figure22.png'))
st.image(img)
with st.container(height=700):
    items = list(st.session_state.modelSituationIndexResult.items())
    colIndex1, colIndex2 = st.columns(2)
    for i, (metric_name, metric_value) in enumerate(items):
        if i % 2 == 0:
            with colIndex1:
                st.metric(f'{metric_name}-Dev_S:', metric_value[1])
        else:
            with colIndex2:
                st.metric(f'{metric_name}-Dev_S:', metric_value[1])
