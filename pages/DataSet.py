# page2.py
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import extra_streamlit_components as stx


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# 用于获取上传数据集名称
# i = 0
data = pd.DataFrame(columns=["文件名称", "传输状态", "上传时间"])
# with every interaction, the script runs from top to bottom
# resulting in the empty dataframe
if 'data_df' not in st.session_state:
    st.session_state.data_df = data


# if 'i' not in st.session_state:
#     st.session_state.i = 0

def remove():
    st.session_state.data_df = st.session_state.data_df.iloc[0:0]


dataSCM, dataSCR = st.columns([0.9, 0.4])

with dataSCM:
    st.markdown("##### 上传数据集")
    ab = st.selectbox(
        '选择数据集',
        ('气象数据', '植保数据', '农学数据'))

    uploaded_files = st.file_uploader(
        "上传数据集",
        accept_multiple_files=True,
        label_visibility='collapsed',
        type=['xlsx', 'csv', 'txt', 'xls'],
        help='help', on_change=remove)
    st.markdown('''
        <style>
            .uploadedFile {display: none}
        <style>''',
                unsafe_allow_html=True)
    for j in range(len(uploaded_files)):
        new_data = {"文件名称": uploaded_files[j].name, "传输状态": "已上传",
                    "上传时间": datetime.now().strftime("%H:%M:%S")}
        st.session_state.data_df.loc[j] = new_data
        bytes_data = uploaded_files[j].read()
        st.data_editor(pd.read_excel(bytes_data))

    st.markdown('---')
    st.markdown("###### 数据格式规范")
    if ab == '气象数据':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('温度数据')
        with col2:
            option15 = st.checkbox('降水数据')
        st.info('温度数据', icon="ℹ️")

    if ab == '植保数据':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('植保站数据')
        with col2:
            option15 = st.checkbox('众源数据')
        st.info('植保数据', icon="ℹ️")

    if ab == '农学数据':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('预测峰值数据')
            option17 = st.checkbox('晚稻移栽期数据')
        with col2:
            option15 = st.checkbox('长势数据')
        with col3:
            option16 = st.checkbox('生化指标数据')
        st.info('农学数据', icon="ℹ️")
with dataSCR:
    st.markdown("##### 文件上传状态显示")
    st.markdown("###### 气象数据")

    placeholder = st.empty()
    with placeholder.container():
        st.data_editor(
            st.session_state.data_df, height=190, width=800,
            disabled=["文件名称", "传输状态", "上传时间"],
            hide_index=False, )
    st.markdown('---')
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()

    st.markdown("###### 植保数据")
    st.data_editor(pd.DataFrame(
        data={
            "文件名称": ['植保站数据', '众源数据'],
            "传输状态": ['已上传', '上传出错'],
            "上传时间": ['13:15:10', '12:16:10']
        }
    ), height=190, width=800, use_container_width=True)
    st.markdown('---')
    st.markdown("###### 农学数据")
    st.data_editor(pd.DataFrame(
        data={
            "文件名称": ['预测峰值数据', '长势数据', '生化指标数据', '晚稻移栽期数据'],
            "传输状态": ['已上传', '上传出错', '已上传', '已上传'],
            "上传时间": ['13:15:10', '12:16:10', '13:15:10', '12:16:10']
        }
    ), height=190, width=800, use_container_width=True)
