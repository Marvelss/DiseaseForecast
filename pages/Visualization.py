"""
@Author : SakuraFox
@Time: 2024-02-26 9:49
@File : Visualization.py
@Description : 数据可视化
"""
import streamlit as st

import pages_utils

# with tab1:
col1, col2 = st.columns(2)

with col1:
    st.markdown('##### 数据')
    tt1 = st.tabs(st.session_state["leftTabs"])
    for i in range(len(st.session_state["leftTabs"])):
        with tt1[i]:
            st.data_editor(
                pages_utils.TempDataSet[i],
                height=720, width=800)
with col2:
    st.markdown('##### 可视化')
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
    # with st.expander("选择坐标"):
    st.bar_chart({"data": [1, 5, 2, 6, 2, 1]})
