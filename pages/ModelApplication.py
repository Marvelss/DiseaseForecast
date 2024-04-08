import datetime
import os.path

import scipy
import streamlit as st
import numpy as np
import pandas as pd
import matlab.engine

import pages_utils

st.set_page_config(
    layout="wide"
)
if 'page16' not in st.session_state:
    st.session_state.page16 = 0


# =======================调用matlab天气情景生成器=======================
def onRun(year, situation, sigama_temp, sigama_max_temp, PA_temp, PA_max_temp):
    # 调用matlab程序
    # print(year, situation)
    # 调用matlab
    eng = matlab.engine.start_matlab()
    eng.cd(r'E:\a_python\program\testForMatlab\weather_generation', nargout=0)
    # sigama_temp, sigama_max_temp, PA_temp, PA_max_temp = 2.5, 3.0, 90 * 0.01, 95 * 0.01
    # result = eng.myPython('0', 'out', 1.0, 1.0, sigama_temp, sigama_max_temp, PA_temp, PA_max_temp, nargout=1)
    result = eng.myPython('0', 'out', year, situation, sigama_temp, sigama_max_temp, PA_temp, PA_max_temp, nargout=1)
    print(result)
    eng.exit()
    st.session_state.page16 += 1
    st.toast('运行完成,数据准备完毕', icon='✅')


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
col123, col223 = st.columns(2)
with col123:
    # 上传历史气象数据
    uploadedHistoricalData = st.file_uploader(
        "上传数据",
        accept_multiple_files=False,
        type=['xlsx', 'xls'],
        help='help')
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

st.markdown("##### 生成模拟气象情景及数据长度")
# st.markdown("##### 生成气象情景")
# ==============================生成气象情景==============================
weatherScenesList = pages_utils.multiselect_all(
    st, '全选',
    [
        '高温多雨', '高温常雨', '高温少雨',
        '常温常雨', '常温多雨', '常温少雨',
        '低温少雨', '低温常雨', '低温多雨'],
    'temp111', 'collapsed')

# 情景转换为对应数字
weatherNumList = pages_utils.getWeatherNum(weatherScenesList)
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
# ==============================异常程度设置==============================
st.markdown("##### 异常程度设置")
# ============================气温标准差============================
col1231, col1232 = st.columns(2)
with col1231:
    st.info('标准差气温评价指标和等级:\n'
            '* 异常偏低:$$\Delta T<-2.0\sigma$$       \n* 明显偏低:$$-2.0\sigma \leq \Delta T<-1.5\sigma$$      \n'
            '* 偏低:$$-1.5\sigma \leq \Delta T<-0.5\sigma$$      \n* 正常(接近常年):$$-0.5\sigma \leq \Delta T\leq 0.5\sigma$$      \n'
            '* 偏高:$$0.5\sigma \leq \Delta T \leq1.5\sigma$$       \n* 明显偏高:$$1.5\sigma \leq \Delta T \leq2.0\sigma$$      \n'
            '* 异常偏高:$$\Delta T>2.0\sigma$$', icon="ℹ️")
with col1232:
    number51 = st.number_input("气温标准差下限", value=2.0, max_value=10.0, min_value=-10.0, step=0.1)
    number52 = st.number_input("气温标准差上限", value=2.5, max_value=10.0, min_value=-10.0, step=0.1)
# ============================降水量距平百分率============================
col12313, col12323 = st.columns(2)
with col12313:
    st.info('降水量距平百分率干旱等级划分(月尺度):\n'
            '* 无旱:$$-40<PA$$       \n* 轻旱:$$-60<PA \leq -40$$      \n'
            '* 中旱:$$-80<PA \leq -60$$      \n* 重旱:$$-95<PA \leq -80$$      \n'
            '* 特旱:$$PA \leq -95$$', icon="ℹ️")
with col12323:
    number53 = st.number_input("降水量距平百分率下限(PA)/%", value=90, max_value=100, min_value=-100, step=5)
    number54 = st.number_input("降水量距平百分率上限(PA)/%", value=95, max_value=100, min_value=-100, step=5)

sigama_temp, sigama_max_temp, PA_temp, PA_max_temp = number51, number53 * 0.01, number52, number54 * 0.01
if not weatherNumList:
    weatherNumList = ['无']
btn = st.button('运行程序', on_click=onRun,
                args=[float(year_difference), weatherNumList[0], sigama_temp, sigama_max_temp, PA_temp, PA_max_temp])
# ==============================获取并准备下载数据==============================
if btn:
    # 读取数据
    pathM = r'E:\a_python\program\testForMatlab\weather_generation\out.mat'
    pathE = r'E:\a_python\program\diseaseForecastStreamlit\resource\simulate'
    if not os.path.exists(pathE):
        os.mkdir(pathE)
    # 清空上一次生成数据
    pages_utils.delete_files_in_folder(pathE)
    # 加载结果
    mat = scipy.io.loadmat(pathM)
    data1 = np.array((mat['gP']))
    data2 = np.array(mat['gTmax'])
    data3 = np.array(mat['gTmin'])
    for i in range(len(data1)):
        tempPath = os.path.join(pathE, '第' + str(i + 1) + '年.xlsx')
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
    # 气象数据的压缩文件路径
    zipPath = r'E:\a_python\program\diseaseForecastStreamlit\resource\基于天气情景生成器的模拟数据.zip'
    # 压缩生成的xlsx数据
    pages_utils.zip_folder(pathE, zipPath)
    with open(zipPath, "rb") as file:
        st.download_button(
            label="下载数据",
            data=file,
            file_name="基于天气情景生成器的模拟数据.zip",
            mime="application/zip",
        )
        # =======================可视化结果=======================
print('---')
st.markdown("##### 加载模型和特征")
# col2, col3 = st.columns(2)
# with col2:
uploaded_model = st.file_uploader("加载模型")
uploaded_parameter = st.file_uploader("输入特征")
interval_col34, interval_col33 = st.columns([5, 1])
btn33 = interval_col33.button('运行')
st.markdown("##### 可视化结果")
if btn33:
    chart_data = pd.DataFrame(np.cumsum(np.random.randint(0, 2, size=(365, 1))), columns=["病株率(%)"])
    st.line_chart(chart_data)
