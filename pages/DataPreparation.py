import datetime
import os
import time
from PIL import Image
import streamlit as st
import numpy as np
import pandas as pd
from streamlit_tree_select import tree_select
import pages_utils
from streamlit_autorefresh import st_autorefresh
import seaborn as sns
import matplotlib.pyplot as plt

if 'page12' not in st.session_state: st.session_state.page12 = 0
if "leftTabs" not in st.session_state:
    # st.session_state["leftTabs"] = data1
    st.session_state["leftTabs"] = ['原始数据']
    # st.session_state["leftTabs"] = stx.tab_bar(data=[
    #     stx.TabBarItemData(id=1, title="气象数据", description=""),
    #     stx.TabBarItemData(id=2, title="植保数据", description=""),
    # ], default=1)

checkBoxNum = 2


# 模拟24小时气温数据
def simulate_temperature_data():
    now = datetime.datetime.now()
    hours = pd.date_range(start=now, periods=24, freq='H')
    temperatures = np.random.randint(10, 30, size=24)
    data = {'Time': hours, 'Temperature': temperatures}
    df = pd.DataFrame(data)
    return df


def clear_all():
    for i in range(checkBoxNum):
        st.session_state[f'checkbox{i}'] = False
    return


def clear_other(key):
    # st.markdown(key)
    for i in range(checkBoxNum):
        if i != key:
            st.session_state[f'checkbox{i}'] = False
    return


# 模拟24小时降水数据
def simulate_precipitation_data():
    now = datetime.datetime.now()
    hours = pd.date_range(start=now, periods=24, freq='H')
    precipitation = np.random.uniform(0, 10, size=24)
    data = {'Time': hours, 'Precipitation': precipitation}
    df = pd.DataFrame(data)
    return df


def simulate_box_data():
    # 模拟生成温度数据
    N = 500
    temperature1 = np.random.normal(loc=20, scale=2, size=(N,))
    temperature2 = np.random.normal(loc=25, scale=4, size=(N,))
    temperature3 = np.random.normal(loc=18, scale=1.5, size=(N,))
    temperature4 = np.random.normal(loc=22, scale=3, size=(N,))

    # 创建DataFrame
    df1 = pd.DataFrame(temperature1, columns=['Temperature'])
    df1['day'] = 'Thur'
    df2 = pd.DataFrame(temperature2, columns=['Temperature'])
    df2['day'] = 'Fri'
    df3 = pd.DataFrame(temperature3, columns=['Temperature'])
    df3['day'] = 'Sat'
    df4 = pd.DataFrame(temperature4, columns=['Temperature'])
    df4['day'] = 'Sun'

    # 合并数据
    df = pd.concat([df1, df2, df3, df4], axis=0)
    return df


def firstPage(): st.session_state.page12 = 0


def nextPage():
    if '预处理后数据' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('预处理后数据')
    st.session_state.page12 += 1
    data11 = {"数据集": "气象数据", "字段": "温度1",
              "大小": '1*3', "处理方法": "缺失值插补1", "时间": '22:130:20',
              "下载数据集": True}
    data12 = {"数据集": "气象数据", "字段": "降水1",
              "大小": '1*5', "处理方法": "剔除异常值1", "时间": '22:110:21',
              "下载数据集": True}
    data13 = {"数据集": "植保数据", "字段": "降水1",
              "大小": '1*1', "处理方法": "剔除异常值1", "时间": '22:33:21',
              "下载数据集": True}
    data14 = {"数据集": "农学数据", "字段": "降水2",
              "大小": '1*2', "处理方法": "剔除异常值1", "时间": '22:151:21',
              "下载数据集": True}
    data15 = {"数据集": "农学数据", "字段": "降水4",
              "大小": '1*3', "处理方法": "剔除异常值1", "时间": '22:14:21',
              "下载数据集": True}
    st.session_state.df11[0].loc[len(st.session_state.df11[0])] = data11
    st.session_state.df11[1].loc[len(st.session_state.df11[1])] = data12
    st.session_state.df11[1].loc[len(st.session_state.df11[1])] = data13
    st.session_state.df11[2].loc[len(st.session_state.df11[2])] = data14
    # st.session_state.df11[3].loc[len(st.session_state.df11[3])] = data15


if 'df11' not in st.session_state:
    st.session_state.df11 = pages_utils.PreprocessedDataSet

# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    # 根据st.session_state.page12的值刷新表格
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        # st.markdown(st.session_state.page12)
        with placeholder1.container():
            tt1 = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt1[i]:
                    for j in range(len(st.session_state["leftTabs"][i]) - 1):
                        st.markdown(str(j))
                        result = pages_utils.multiselect_all(
                            st, str(j), ['温度', '降水', j],
                            'temp', 'collapsed')
                        # st.markdown(result)
                        st.markdown(pages_utils.TempDataSet[i][j])
                        st.data_editor(
                            pages_utils.TempDataSet[i][j],
                            height=190, width=800, )
                        # column_config={
                        #     "选择字段": st.column_config.CheckboxColumn(
                        #         help="选择用于数据处理的字段",
                        #         default=False,
                        #     )
                        # })
                        st.markdown('---')

    if st.session_state.page12 == 1:
        with placeholder1.container():
            tt = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt[i]:
                    for j in range(len(st.session_state["leftTabs"][i]) - 1):
                        result = pages_utils.multiselect_all(
                            st, str(j)+str(i), ['温度', '降水', j, i],
                            'temp', 'collapsed')
                        # st.markdown(result)
                        st.markdown('第二次')
                        st.markdown(pages_utils.TempDataSet[i][j])
                        st.data_editor(
                            pages_utils.TempDataSet[i][j],
                            height=190, width=800, )
                    # column_config={
                    #     "选择字段": st.column_config.CheckboxColumn(
                    #         help="选择用于数据处理的字段",
                    #         default=False,
                    #     )
                    # })

with dataPCM:
    st.markdown("##### 预处理方法")
    # with tab1:
    col1, col2 = st.columns(2)

    with col1:
        agree = st.checkbox('剔除异常值', key='checkbox0', on_change=clear_other, args=[0])
        # agree5 = st.checkbox('剔除数据5')
    with col2:
        agree10 = st.checkbox("缺失值插补", key='checkbox1', on_change=clear_other, args=[1])
    st.markdown('---')
    # st.markdown("##### 方法参数设置")
    if agree10:
        coll11, coll22 = st.columns([0.6, 0.3])
        with coll11:
            st.info('用于填补缺失值', icon="ℹ️")
            # st.markdown(os.path.join(os.getcwd(), 'resource', 'image', '0.png'))
            img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '0.png'))
            st.image(img)
        with coll22:
            option = st.selectbox(
                '插补方法',
                options=('线性插值', '自定义'))
            if option == '自定义':
                st.text_input('输入数值')
        # st.markdown('---')
    if agree:
        number2 = st.text_input("剔除大于", value=0.1)
        number3 = st.text_input("剔除小于", value=0.1)
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clear_all)
    if btn:
        # update dataframe state
        # st.markdown(type(st.session_state.df))
        new_data = {"数据集": "气象数据", "输入字段": "温度", "输出字段": "温度",
                    "预处理方法": "缺失值插补", "时间": '22:20:20'}
        st.session_state.df.loc[len(st.session_state.df)] = new_data
        st.rerun()
    st.markdown('---')

    data = pd.DataFrame(columns=["数据集", "输入字段", "输出字段", "预处理方法", '时间'])
    # with every interaction, the script runs from top to bottom
    # resulting in the empty dataframe
    if 'df' not in st.session_state:
        st.session_state.df = data

    placeholder = st.empty()
    if st.session_state.page12 == 0:
        with placeholder.container():
            st.markdown('##### 任务清单')
            edited_df28 = st.data_editor(
                st.session_state.df, height=190, width=800,
                disabled=["数据集", "输入字段", "输出字段", "时间"], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])
            btn2 = interval_col33.button('运行', on_click=nextPage)

    elif st.session_state.page12 == 1:
        with placeholder.container():
            st.markdown('##### 可视化')
            tab1, tab2, tab3 = st.tabs(["1", "2", "3"])
            with tab1:
                # 模拟气温数据
                temperature_data = simulate_temperature_data()
                st.line_chart(temperature_data.set_index('Time'))
            with tab2:
                # 模拟降水数据
                precipitation_data = simulate_precipitation_data()
                fig, ax = plt.subplots()
                sns.lineplot(data=precipitation_data)
                ax.set_xlabel('Time(hours)')
                ax.set_ylabel('Precipitation')
                st.pyplot(fig)
            with tab3:
                df111 = simulate_box_data()
                # 绘制箱型图
                fig, ax = plt.subplots()
                sns.boxplot(x='day', y='Temperature', data=df111,
                            linewidth=2,
                            width=0.8,
                            fliersize=3,
                            palette='hls',
                            whis=1.5,
                            notch=True,
                            order=['Thur', 'Fri', 'Sat', 'Sun']
                            )
                ax.set_xlabel('Day')
                ax.set_ylabel('Temperature')
                plt.figure(figsize=(10, 6))
                # sns.(x='', y='', data=df, palette='Set3')
                plt.title('Boxplot of Temperature for Different Days')
                st.pyplot(fig)
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('返回', on_click=firstPage)
