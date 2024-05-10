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
from streamlit_pills import pills
from modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
from modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod

import pages_utils

st.set_page_config(
    layout="wide"
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


# 函数替换数据
def replace_data(df1, df2):
    # 根据条件筛选并替换原始数据表格中的值
    for index, row in df2.iterrows():
        condition = (df1['上级单位'] == row['上级单位']) & (df1['测报站点'] == row['测报站点']) & \
                    (df1['年'] == row['年']) & (df1['DayOfYear'] == row['DayOfYear'])
        df1.loc[condition, '降水'] = row['降水']
        df1.loc[condition, '温度'] = row['温度']
    return df1


# 获取模拟气象数据(待修正)
def getSimulateWeather(weatherSituation, startYear, province, station):
    modelPathRoot = os.path.join(os.getcwd(),
                                 'resource',
                                 'weatherGeneratorOutput')
    fileDirPath = os.path.join(modelPathRoot, weatherSituation)
    merged_data = pd.DataFrame()
    for fileTemp in os.listdir(fileDirPath):
        # Get the file name
        file_name = os.path.join(fileDirPath, fileTemp)
        yearNum = fileTemp.split('年')[0].split('第')[1]

        # Read the Excel file
        data = pd.read_excel(file_name)

        # Merge the data using the 'left' method
        merged_data = pd.merge(data, merged_data, how='left')
    print(merged_data)
    return merged_data


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


# =======================调用matlab天气情景生成器并保存结果数据=======================
# 调用matlab程序
def onRun(year, selectedWeatherScenesList, weatherSituationParams):
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
        print(result)
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

    # =========================替换模拟气象数据=========================
    # 用户输入:上级单位、测报站点、年份范围
    # province = '湖南省'
    # station = '湘阴县'
    # sd, ed = '2010', '2010'

    # 调用天气情景生成器,获取数据
    # 根据上级单位、测报站点、年份范围替换原始数据

    # 多个情景遍历, 这里目前用一个
    df3T = getSimulateWeather(
        selectedWeatherScenesList,
        weatherGeneratorProvinceSelected,
        weatherGeneratorStationSelected,
        generatedYears[0])
    rawData = replace_data(pages_utils.TempDataSet[0], df3T)
    print('=========================替换后数据=========================')
    rawData.to_excel('weatherReplaced.xlsx', index=False)
    # =========================特征计算及读取执行方法=========================
    # 读取记录
    featureCalculateDF = pages_utils.TempDataSetField[1]
    inputFeature1 = featureCalculateDF["输入特征"].tolist()
    # outputFeature1 = featureCalculateDF["备选特征"].tolist()
    featureCalculateList = featureCalculateDF["特征计算方法"].tolist()
    modelParam1 = featureCalculateDF["方法参数"].tolist()
    print(modelParam1)
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

    print(f'=============特征字段计算完成=============')
    # rawData.to_excel(r'E:\a_python\program\diseaseForecastStreamlit\resource\uploadFileDir\featureCalculated.xlsx')
    # =========================特征优选及读取执行方法=========================
    featureOptimalDF = pages_utils.TempDataSetField[2]

    inputFeature2 = featureOptimalDF["输入特征"].tolist()
    # outputFeature2 = featureOptimalDF["优选特征"].tolist()
    featureOptimalList = featureOptimalDF["特征优选方法"].tolist()
    modelParam2 = featureOptimalDF["方法参数"].tolist()

    print('==========测试列=============')
    print(rawData.columns)
    print(type(rawData.columns))
    tool2 = FeatureOptimizationMethod(rawData, rawData.columns.tolist())
    # 初始化特征优选方法
    for indexT, tempMethod in enumerate(featureOptimalList):
        if tempMethod == 'Pearson相关性分析':
            print('=============Pearson相关性分析检测============')
            print(modelParam2[indexT].split(','))
            rawData, _ = tool2.Pearson(modelParam2[indexT].split(','))
        elif tempMethod == 'Relief-F互相关分析':
            rawData, _ = tool2.ReliefF(
                inputFeature2[0], modelParam2)

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
    modelDF = pages_utils.TempDataSetField[3]

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
        predictions_df.to_excel(
            os.path.join(os.getcwd(),
                         'resource',
                         'modelsResults',
                         'modelsApplicationResult',
                         str(tempModel) +
                         '_applicationPredicts' +
                         '.xlsx'), index=False)
        st.toast(f'{tempModel}模型预测完毕', icon='✅')
        # =========================计算静态偏差指标=========================
        # 输入真实植保数据(测试是否缺失)(输入原始特征中有),并结合上述模型输出预测数据

        # (单一气象场景)结果可视化(暂不处理)
        # 计算指标
        data = pd.read_excel('predictsSVR.xlsx')
        data_B = data['病害峰值']  # 实际
        data_A = data['Predicted_value']  # 预测
        # 计算两组数据相减的均值之和除以长度
        mean_diff = ((data_A - data_B).sum()) / len(data_A)

        # 计算数据 A 的标准差之和除以长度
        std_dev_B = data_B.std() / len(data_B)

        print(f"预测值与实际发生程度之差的均值: {mean_diff}")
        print(f"实际发生程度的标准差: {std_dev_B}")
        print(f'Dev_s:{mean_diff / std_dev_B}')


# ==============================界面==============================


# with col3:
# ex = st.expander('下载基于天气情景生成器生成的全年模拟气温和降水数据')
# st.markdown("##### 天气情景生成器")
# with ex:
# generatedYears = st.number_input('输入时间序列的起始年', value=1)
# generatedYears1 = st.number_input('输入时间序列的起始月', value=1)
# generatedYears2 = st.number_input('输入时间序列的截至年', value=1)
# generatedYears3 = st.number_input('输入时间序列的截至月', value=1)
st.markdown("##### 历史气象站点数据上传及模板下载注意事项")
st.markdown("##### 选择地区")
weatherGeneratorInfo, weatherGeneratorInstruction = st.columns(2)
with weatherGeneratorInfo:
    weatherGeneratorProvinceSelected = st.selectbox(
        label='province',
        options=['上级单位'], label_visibility='collapsed')
    weatherGeneratorStationSelected = st.selectbox(
        label='station',
        options=['测报站点'],
        label_visibility='collapsed')
with weatherGeneratorInstruction:
    warningMInfo = '''
    设置参数说明(待填):选择上级单位、测报站点\n

    '''
    st.warning(warningMInfo, icon="⚠️")
col123, col223 = st.columns(2)
with col123:
    st.markdown("##### 上传数据")
    # 上传历史气象数据
    uploadedHistoricalData = st.file_uploader(
        "上传数据",
        accept_multiple_files=False,
        type=['xlsx', 'xls'],
        help='help',
        label_visibility='collapsed'
    )
with col223:
    warningMInfo = '''
    注意事项(待填)
    '''
    st.markdown("###### 模板下载")
    st.warning(warningMInfo, icon="⚠️")
    path2 = r'E:\a_python\program\diseaseForecastStreamlit\resource\上传历史数据集模板-测试.xlsx'
    with open(path2, "rb") as file:
        st.download_button(
            label="下载历史站点气象数据模板",
            data=file,
            file_name="历史气象数据模板.xlsx",
            mime="application/octet-stream"
        )

st.markdown("##### 生成数据长度")
# ==============================时间长度==============================
today = datetime.datetime.now()
next_year = today.year + 1
jan_1 = datetime.date(today.year, 1, 1)
dec_31 = datetime.date(today.year + 1, 12, 31)
generatedYears = st.date_input(
    "选择起止年月",
    (jan_1, datetime.date(next_year, 1, 7)),
    jan_1,
    dec_31,
    format="YYYY.MM.DD",
)
year_difference = generatedYears[1].year - generatedYears[0].year
print(year_difference)

# print('----------')
# print(float(generatedYears), float(weatherScenes))

# st.info('生成的气象情景:\n'
#         '* 1:高温多雨 2:高温常雨 3:高温少雨\n'
#         '* 4:常温常雨 5:常温多雨 6:常温少雨\n'
#         '* 7:低温少雨 8:低温常雨 9:低温多雨\n', icon="ℹ️")
st.markdown(' ')
st.markdown("##### 生成模拟气象情景")
# st.markdown("##### 生成气象情景")
# ==============================生成气象情景==============================
weatherScenesList = pages_utils.multiselect_all(
    st, '全选',
    [
        '高温多雨', '高温常雨', '高温少雨',
        '常温常雨', '常温多雨', '常温少雨',
        '低温少雨', '低温常雨', '低温多雨'],
    'temp111', 'collapsed')
if not weatherScenesList:
    weatherScenesList = ['高温少雨']

st.markdown("##### 异常程度设置")
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

st.markdown("##### 指定评价模型")
modelSList = pages_utils.multiselect_all(
    st, '全选-模型',
    [
        '模型1', '模型2'],
    'tempModels', 'collapsed')
sigama_temp, sigama_max_temp, PA_temp, PA_max_temp = number51, number53 * 0.01, number52, number54 * 0.01

btn = st.button('运行程序', on_click=onRun,
                args=[float(year_difference), weatherScenesList, st.session_state.weatherSituationParams])
# ==============================准备下载数据==============================
if btn:
    zipPath = r'E:\a_python\program\diseaseForecastStreamlit\resource\基于天气情景生成器的模拟数据.zip'
    # 压缩生成的xlsx数据
    pathEE = r'E:\a_python\program\diseaseForecastStreamlit\resource\weatherGeneratorOutput'
    pages_utils.zip_folder(pathEE, zipPath)
    with open(zipPath, "rb") as file:
        st.download_button(
            label="下载数据",
            data=file,
            file_name="基于天气情景生成器的模拟数据.zip",
            mime="application/zip",
        )
# =======================预测评价结果及数据下载=======================
st.markdown("##### 模型评价指标结果及可视化")
# tab11, tab12 = st.tabs(['模型1', '模型2'])
with st.container(height=700):
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', 'weatherGeneratorEvaluateResult2.jpg'))
    st.image(img)
    co3, co4 = st.columns(2)
    with co3:
        st.metric("Dev_D", "0.0799")
    with co4:
        st.metric("Dev_D", "0.0899")
    # 评价指标结果示意图
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', 'weatherGeneratorEvaluateResult1.jpg'))
    st.image(img)
    co1, co2 = st.columns(2)
    with co1:
        st.metric("Dev_S", "0.0262")
    with co2:
        st.metric("Dev_S", "0.0888")
