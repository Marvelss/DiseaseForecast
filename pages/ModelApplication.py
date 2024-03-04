import scipy
import streamlit as st
import numpy as np
import pandas as pd
import matlab.engine

st.set_page_config(
    layout="wide"
)
if 'page16' not in st.session_state:
    st.session_state.page16 = 0


@st.cache_data
def convert_df(df1):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df1.to_csv(index=False).encode('utf-8')


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


st.markdown("##### 加载模型和特征")
col2, col3 = st.columns(2)
with col2:
    uploaded_model = st.file_uploader("加载模型")
    uploaded_parameter = st.file_uploader("输入特征")
with col3:
    ex = st.expander('下载基于天气情景生成器生成的全年模拟气温和降水')
    with ex:
        generatedYears = st.number_input('生成的气象数据长度(年为单位)', value=1)
        weatherScenes = st.number_input('生成的气象情景', value=1)
        # print('----------')
        # print(float(generatedYears), float(weatherScenes))
        st.info('生成的气象情景:\n'
                '* 1:高温多雨 2:高温常雨 3:高温少雨\n'
                '* 4:常温常雨 5:常温多雨 6:常温少雨\n'
                '* 7:低温少雨 8:低温常雨 9:低温多雨\n'
                , icon="ℹ️")
        btn = st.button('运行程序', on_click=onRun, args=[float(generatedYears), float(weatherScenes)])

        if btn:
            # 读取数据
            pathM = r'E:\a_python\program\testForMatlab\weather_generation\out.mat'
            pathE = r'E:\a_python\program\diseaseForecastStreamlit\resource\simulatedData.xlsx'
            mat = scipy.io.loadmat(pathM)
            data1 = np.array((mat['gP']))
            data2 = np.array(mat['gTmax'])
            data3 = np.array(mat['gTmin'])
            # 创建DayOfYear列
            day_of_year = range(1, len(data1[0]) + 1)
            # 将数据转换为DataFrame
            my_large_df = pd.DataFrame({
                'Day Of Year': day_of_year,
                '模拟降水': data1.flatten(),
                '模拟最高温度': data2.flatten(),
                '模拟最低温度': data3.flatten()
            })
            my_large_df.to_excel(pathE, index=False)
            with open(pathE, "rb") as file:
                st.download_button(
                    label="下载数据",
                    data=file,
                    file_name="模拟气温和降水数据.xlsx",
                    mime="application/octet-stream"
                )

# uploaded_files = st.file_uploader("加载数据集", accept_multiple_files=True)
# for uploaded_file in uploaded_files:
#     bytes_data = uploaded_file.read()
#     st.write("filename:", uploaded_file.name)
# st.write(bytes_data)
print('---')
st.markdown("##### 可视化结果")
btn = st.button('运行')
if btn:
    chart_data = pd.DataFrame(np.cumsum(np.random.randint(0, 2, size=(365, 1))), columns=["病株率(%)"])
    st.line_chart(chart_data)
