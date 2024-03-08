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
def onRun(year, situation):
    # 调用matlab程序
    # print(year, situation)
    # 调用matlab
    eng = matlab.engine.start_matlab()
    eng.cd(r'E:\a_python\program\testForMatlab\weather_generation', nargout=0)
    result = eng.myPython('0', 'out', year, situation, nargout=1)
    print(result)
    eng.exit()
    st.session_state.page16 += 1
    st.toast('运行完成,数据准备完毕', icon='✅')


# ==============================界面==============================
st.markdown("##### 加载模型和特征")
col2, col3 = st.columns(2)
with col2:
    uploaded_model = st.file_uploader("加载模型")
    uploaded_parameter = st.file_uploader("输入特征")
    interval_col34, interval_col33 = st.columns([5, 1])
    btn33 = interval_col33.button('运行')

with col3:
    ex = st.expander('下载基于天气情景生成器生成的全年模拟气温和降水数据')
    with ex:
        generatedYears = st.number_input('生成的气象数据长度(年为单位)', value=1)
        weatherScenes = st.number_input('生成的气象情景', value=1)
        # print('----------')
        # print(float(generatedYears), float(weatherScenes))
        st.info('生成的气象情景:\n'
                '* 1:高温多雨 2:高温常雨 3:高温少雨\n'
                '* 4:常温常雨 5:常温多雨 6:常温少雨\n'
                '* 7:低温少雨 8:低温常雨 9:低温多雨\n', icon="ℹ️")
        btn = st.button('运行程序', on_click=onRun, args=[float(generatedYears), float(weatherScenes)])
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
st.markdown("##### 可视化结果")
if btn33:
    chart_data = pd.DataFrame(np.cumsum(np.random.randint(0, 2, size=(365, 1))), columns=["病株率(%)"])
    st.line_chart(chart_data)
