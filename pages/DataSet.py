# page2.py
from datetime import datetime

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


# 用于获取上传数据集名称
i = 0
data = pd.DataFrame(columns=["文件名称", "传输状态", "上传时间"])
# with every interaction, the script runs from top to bottom
# resulting in the empty dataframe
if 'data_df' not in st.session_state:
    st.session_state.data_df = data
if 'i' not in st.session_state:
    st.session_state.i = i

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
    # 用于避免点击其他数据集选项卡时出现异常提示(但这样似乎无效)
    temp = 0
    if uploaded_files and uploaded_files != temp:
        # st.markdown(st.session_state.i)
        # st.markdown(uploaded_files[st.session_state.i].name)
        # if st.session_state.i != 0:
        new_data = {"文件名称": uploaded_files[st.session_state.i].name, "传输状态": "已上传",
                    "上传时间": datetime.now().strftime("%H:%M:%S")}
        st.session_state.data_df.loc[len(st.session_state.data_df)] = new_data
        st.session_state.i += 1
        temp = uploaded_files
    st.markdown('---')
    st.markdown("###### 模板下载")
    if chosen_id == '1':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('温度数据')
        with col2:
            option15 = st.checkbox('降水数据')
        # with col3:
        # option16 = st.checkbox('')
    if chosen_id == '2':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('植保站数据')
        with col2:
            option15 = st.checkbox('众源数据')
        # with col3:
        #     option16 = st.checkbox('模板7')
    if chosen_id == '3':
        col1, col2, col3 = st.columns(3)
        with col1:
            option14 = st.checkbox('预测峰值数据')
            option17 = st.checkbox('晚稻移栽期数据')
        with col2:
            option15 = st.checkbox('长势数据')
        with col3:
            option16 = st.checkbox('生化指标数据')
    st.markdown('---')
    st.markdown("###### 模板预览")
    csv = convert_df(pd.read_csv(r'E:\a_python\program\diseaseForecastStreamlit\resource\房价数据.csv'))
    interval_col1, interval_col2 = st.columns([5, 1])
    interval_col2.download_button(
        label="下载",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
    )
with dataSCR:
    st.markdown("##### 文件上传状态显示")
    st.markdown("###### 气象数据")

    placeholder = st.empty()
    with placeholder.container():
        st.data_editor(
            st.session_state.data_df, height=190, width=800,
            disabled=["文件名称", "传输状态", "上传时间"],
            hide_index=False, )
    # st.write("文件名称:", '气温.xlsx')
    st.markdown('---')
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        # st.write("filename:", uploaded_file.name)
        # dataframe = pd.read_excel(uploaded_file)
        # st.write(dataframe)

    st.markdown("###### 植保数据")
    st.data_editor(pd.DataFrame(
        data={
            "文件名称": ['植保站数据', '众源数据'],
            "传输状态": ['已上传', '上传出错'],
            "上传时间": ['13:15:10', '12:16:10']
        }
    ),height=190, width=800, use_container_width=True)
    # col1ab, col2ab = st.columns(2)
    # col1ab.write("文件名称: 气温.xlsx")
    # col1ab.write("文件名称: 降水.xlsx")
    # col2ab.write("状态:已上传")
    # col2ab.write("状态:上传出错")
    st.markdown('---')
    st.markdown("###### 农学数据")
    st.data_editor(pd.DataFrame(
        data={
            "文件名称": ['预测峰值数据', '长势数据', '生化指标数据', '晚稻移栽期数据'],
            "传输状态": ['已上传', '上传出错', '已上传', '已上传'],
            "上传时间": ['13:15:10', '12:16:10', '13:15:10', '12:16:10']
        }
    ), height=190, width=800, use_container_width=True)
