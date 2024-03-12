"""
@Author : SakuraFox
@Time: 2024-02-26 9:49
@File : Visualization.py
@Description : 数据可视化
"""
import streamlit as st

import pages_utils

st.set_page_config(
    layout="wide"
)

# with tab1:
tab1, tab2 = st.tabs(['数据及下载', '可视化'])

with tab1:
    col1, col2 = st.columns([0.2, 0.7])
    with col1:
        option55 = st.selectbox(
            '选择下载内容',
            options=st.session_state["leftTabs"])
        if option55 == '模型':
            result1 = pages_utils.multiselect_all(
                st, '全选',
                ['SVM', 'FLDA'],
                'temp11', 'collapsed')
            btn11 = st.button('下载特征和标签、模型结构及训练结果')
        else:
            result1 = pages_utils.multiselect_all(
                st, '全选',
                ['降水', '温度'],
                'temp111', 'collapsed')
            btn11 = st.button('下载')

    with col2:
        tt1 = st.tabs(st.session_state["leftTabs"])
        for i in range(len(st.session_state["leftTabs"])):
            with tt1[i]:
                st.data_editor(
                    pages_utils.TempDataSet[i],
                    height=800, width=1500)
with tab2:
    col1, col2 = st.columns([0.2, 0.7])
    with col1:
        option4 = st.selectbox(
            '选择数据集',
            options=st.session_state["leftTabs"])
        option1 = st.selectbox(
            '选择图形',
            options=('散点图', '直方图'))
        option2 = st.selectbox(
            '选择X轴',
            options=('年', 'DayOfYear'))
        option3 = st.selectbox(
            '选择Y轴',
            options=('预测病株率', '病害发生程度'))
        interval_col1, interval_col2 = st.columns([1.4, 1])
        btn = interval_col2.button('添加图形')

    with col2:
        if btn:
            st.bar_chart({"data": [1, 5, 2, 6, 2, 1]})
        else:
            st.markdown('可视化')
