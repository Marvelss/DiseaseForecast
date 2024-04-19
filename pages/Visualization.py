"""
@Author : SakuraFox
@Time: 2024-02-26 9:49
@File : Visualization.py
@Description : 数据可视化
"""
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
import seaborn as sns
from streamlit_pills import pills

import pages_utils

st.set_page_config(
    layout="wide"
)


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("gbk")


# with tab1:
tab1, tab2 = st.tabs(['数据及下载', '可视化'])

with tab1:
    col1, col2 = st.columns([0.7, 0.2])
    with col2:
        st.markdown('###### 选择下载内容')
        option55 = st.radio("选择下载内容",
                            options=['数据集', '各环节方法执行记录'],
                            label_visibility='collapsed')
        st.markdown('---')
        column = ['无数据']
        data = pd.DataFrame(columns=['无数据'])

        # 从第二个元素开始获取
        if not st.session_state["leftTabs"][1:]:
            downloadList = ['空']
        else:
            downloadList = st.session_state["leftTabs"][1:]
        option55 = pills("选择下载数据集类型或各环节数据名称", options=downloadList)
        st.markdown('---')
        if option55 == '模型':
            result1 = pages_utils.multiselect_all(
                st, '全选',
                pages_utils.TempDataSetField[4]['模型'],
                'temp11', 'collapsed')
            btn11 = st.button('下载特征和标签、模型结构及训练结果')
        elif option55 == '预处理后数据集':
            column = pages_utils.TempDataSet[1].columns.tolist()
            data = pages_utils.TempDataSet[1]
        elif option55 == '备选特征':
            column = pages_utils.TempDataSet[2].columns.tolist()
            data = pages_utils.TempDataSet[2]
        elif option55 == '优选特征':
            column = pages_utils.TempDataSet[3].columns.tolist()
            data = pages_utils.TempDataSet[3]
        result1 = pages_utils.multiselect_all(
            st, '全选',
            column,
            'temp111', 'collapsed')
        # 下载指定字段数据
        file = data[result1]
        csv = convert_df(file)
        st.download_button(
            label="下载",
            data=csv,
            file_name="导出数据.csv",
            mime='text/csv'
        )

    with col1:
        st.markdown('###### 数据集')
        tt1 = st.tabs(st.session_state["leftTabs"])
        for i in range(len(st.session_state["leftTabs"])):
            with tt1[i]:
                st.data_editor(
                    pages_utils.TempDataSet[i],
                    height=250, width=1500)
        st.markdown('###### 各环节方法执行记录')
        tt2 = st.tabs(st.session_state["leftTabs"])
        for j in range(len(st.session_state["leftTabs"])):
            with tt2[j]:
                st.data_editor(
                    pages_utils.TempDataSetField[j],
                    height=250, width=1500)
with col2:
    with tab2:
        col111, col222 = st.columns([0.2, 0.7])
        with col111:
            column1 = ['无数据']
            data1 = pd.DataFrame(columns=['无数据'])
            option4 = st.selectbox(
                '选择数据集或模型',
                options=st.session_state["leftTabs"])
            if option4 == '模型':
                column1 = pages_utils.TempDataSet[4].columns.tolist()
                data1 = pages_utils.TempDataSet[4]
            elif option4 == '预处理后数据集':
                column1 = pages_utils.TempDataSet[1].columns.tolist()
                data1 = pages_utils.TempDataSet[1]
            elif option4 == '备选特征':
                column1 = pages_utils.TempDataSet[2].columns.tolist()
                data1 = pages_utils.TempDataSet[2]
            elif option4 == '优选特征':
                column1 = pages_utils.TempDataSet[3].columns.tolist()
                data1 = pages_utils.TempDataSet[3]
            option1 = st.selectbox(
                '选择图形',
                options=('散点图', '直方图'))
            option2 = st.selectbox(
                '选择X轴',
                options=column1)
            option3 = st.selectbox(
                '选择Y轴',
                options=column1)
            interval_col1, interval_col2 = st.columns([1.4, 1])
            btn = interval_col2.button('添加图形')

        with col222:
            if btn:
                if option1 == '散点图':
                    # 取x,y轴数据
                    file = data[option3]
                    print(option2)
                    print(option3)
                    print(file)
                    # 以下未实现x轴和y轴数据合并成绘图格式
                    plt.rc("font", family='Microsoft YaHei')
                    tab1, tab2 = st.tabs(["1", "2"])
                    with tab1:
                        # 绘制最高温度和最低温度的折线图
                        plt.figure(figsize=(10, 5))
                        sns.lineplot(data=file, x="Year", y="Precipitation", label="降水量")
                        plt.xlabel('日期')
                        plt.ylabel('降水累积量(mm)')
                        plt.title('降水累积量特征')
                        plt.legend()
                        st.pyplot(plt)
            else:
                st.markdown('可视化')
