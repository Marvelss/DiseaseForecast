# page2.py
import numpy as np
import pandas as pd
import streamlit as st
import extra_streamlit_components as stx

from pages_utils import multiselect_all


# st.sidebar.info("注意:按照数据集模板内容填写")


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# st.header('数据集')
# st.markdown('---')
dataSCM, dataSCR = st.columns([0.9, 0.4])

with dataSCM:
    st.markdown("##### 上传数据集")
    chosen_id = stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title="气象数据", description=""),
        stx.TabBarItemData(id=2, title="植保数据", description=""),
        stx.TabBarItemData(id=3, title="农学数据", description=""),
    ], default=1)
    uploaded_files = st.file_uploader(
        "上传数据集",
        accept_multiple_files=True,
        label_visibility='collapsed',
        type=['xlsx', 'csv', 'txt', 'xls'],
        help='help', )
    st.markdown('''
        <style>
            .uploadedFile {display: none}
        <style>''',
                unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("###### 模板下载")
    if chosen_id == '1':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('温度')
        with col2:
            option15 = st.checkbox('降水')
        with col3:
            option16 = st.checkbox('')
    if chosen_id == '2':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('生育期')
        with col2:
            option15 = st.checkbox('模板6')
        with col3:
            option16 = st.checkbox('模板7')
    if chosen_id == '3':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('生育期')
        with col2:
            option15 = st.checkbox('模板6')
        with col3:
            option16 = st.checkbox('模板7')
    st.markdown('---')
    st.markdown("###### 模板预览")
    interval_col1, interval_col2 = st.columns([5, 1])
    interval_col2.button('下载')
with dataSCR:
    st.markdown("##### 文件上传状态显示")
    st.markdown("###### 气象数据")
    st.write("文件名称:", '气温.xlsx')
    st.markdown('---')
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)
        dataframe = pd.read_excel(uploaded_file)
        st.write(dataframe)
    st.markdown("###### 植保数据")
    col1ab, col2ab = st.columns(2)
    col1ab.write("文件名称: 气温.xlsx")
    col2ab.write("状态:已上传")
    st.markdown('---')
    st.markdown("###### 农学数据")
    st.write("文件名称:", '气温.xlsx')
