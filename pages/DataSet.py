# page2.py
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import extra_streamlit_components as stx

import pages_utils


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# 用于获取上传数据集名称
# i = 0
data1 = pd.DataFrame(columns=["文件名称", "传输状态", "上传时间"])
data2 = pd.DataFrame(columns=["文件名称", "传输状态", "上传时间"])

data3 = pd.DataFrame(columns=["文件名称", "传输状态", "上传时间"])

# with every interaction, the script runs from top to bottom
# resulting in the empty dataframe
if 'weatherState' not in st.session_state:
    st.session_state.weatherState = data1
if 'plantState' not in st.session_state:
    st.session_state.plantState = data2
if 'agricultureState' not in st.session_state:
    st.session_state.agricultureState = data3

if 'RawDataSet' not in st.session_state:
    st.session_state.RawDataSet = pages_utils.RawDataSet


# if 'i' not in st.session_state:
#     st.session_state.i = 0

# def addInfo():
#     if uploaded_files:
#         # bytes_data = uploaded_files.read()
#         # data33 = pd.read_excel(bytes_data)
#         st.markdown('a')
# df = getStateDF(ab)
# new_data = {"文件名称": uploaded_files.name, "传输状态": "已上传",
#             "上传时间": datetime.now().strftime("%H:%M:%S")}
# df.loc[len(df)] = new_data


def addState(df, info):
    df.loc[len(df)] = info


def getStateDF(name):
    if name == '气象数据':
        return st.session_state.weatherState
    elif name == '植保数据':
        return st.session_state.plantState
    elif name == '农学数据':
        return st.session_state.agricultureState


dataSCM, dataSCR = st.columns([0.9, 0.4])

with dataSCM:
    st.markdown("##### 上传数据集")
    ab = st.selectbox(
        '选择数据集',
        ('气象数据', '植保数据', '农学数据'))

    uploaded_files = st.file_uploader(
        "上传数据集",
        accept_multiple_files=False,
        label_visibility='collapsed',
        type=['xlsx', 'csv', 'txt', 'xls'],
        help='help')

    # st.markdown('''
    #     <style>
    #         .uploadedFile {display: none}
    #     <style>''',
    #             unsafe_allow_html=True)

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

    if uploaded_files:
        bytes_data = uploaded_files.read()
        data33 = pd.read_excel(bytes_data)
        # st.markdown(data33)
        df = getStateDF(ab)
        new_data = {"文件名称": uploaded_files.name, "传输状态": "已上传",
                    "上传时间": datetime.now().strftime("%H:%M:%S")}
        st.session_state.RawDataSet = pd.concat(
            [st.session_state.RawDataSet, data33])
        pages_utils.RawDataSet = st.session_state.RawDataSet

        st.markdown(st.session_state.RawDataSet.columns)

        df.loc[len(df)] = new_data

        # st.markdown(uploaded_files.name)
with dataSCR:
    st.markdown("##### 文件上传状态显示")
    st.markdown("###### 气象数据")

    placeholder = st.empty()
    with placeholder.container():
        st.data_editor(
            st.session_state.weatherState, height=190, width=800,
            disabled=["文件名称", "传输状态", "上传时间"],
            hide_index=False, )
    st.markdown('---')

    st.markdown("###### 植保数据")
    st.data_editor(pd.DataFrame(
        st.session_state.plantState
    ), height=190, width=800, use_container_width=True)
    st.markdown('---')
    st.markdown("###### 农学数据")
    st.data_editor(pd.DataFrame(
        st.session_state.agricultureState
    ), height=190, width=800,
        disabled=["文件名称", "传输状态"], use_container_width=True)
