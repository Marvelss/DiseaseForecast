# page2.py
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import extra_streamlit_components as stx

import pages_utils

from warnings import simplefilter

simplefilter(action="ignore", category=FutureWarning)


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# 用于获取上传数据集名称
# i = 0


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
    st.markdown("##### 数据格式规范")
    col1, col2 = st.columns(2)
    with col1:
        st.warning('字段必须包含以下4个:\n'
                   '* 上级单位(文字)\n'
                   '* 测报站点(文字)\n'
                   '* 年(数字)\n'
                   '* DayOfYear(数字)\n', icon="⚠️")
    placeholder1 = st.empty()
    if ab == '气象数据':
        with placeholder1.container():
            with col2:
                st.info('其他可选字段:\n'
                        '* 温度(数字)\n'
                        '* 降水(数字)\n', icon="ℹ️️")
    if ab == '植保数据':
        with placeholder1.container():
            with col2:
                st.info('其他可选字段:\n'
                        '* 稻作类型(文字)\n'
                        '* 病害发生程度等级(数字)\n'
                        '* 预测病株率(数字)\n', icon="ℹ️️")
    if ab == '农学数据':
        with placeholder1.container():
            with col2:
                st.info('其他可选字段:\n'
                        '* 长势(数字)\n'
                        '* 生化指标(数字)\n', icon="ℹ️️")

    if uploaded_files:
        bytes_data = uploaded_files.read()
        data33 = pd.read_excel(bytes_data)
        # st.markdown(data33)
        # df = getStateDF(ab)
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": ab, "文件名称": uploaded_files.name, "传输状态": "已上传",
            "上传时间": datetime.now().strftime("%H:%M:%S"),
            "字段": data33.columns.tolist()}
        # 防止重复添加
        if (pages_utils.TempDataSetField[0]['文件名称'] == uploaded_files.name).any():
            # st.markdown(pages_utils.TempDataSetField[0])
            # st.markdown(uploaded_files.name)
            # st.markdown("和uploaded_files.name变量一致的文件名称已经存在，不执行以下操作")
            st.markdown('---')
        else:
            # 添加字段
            pages_utils.TempDataSetField[0].loc[len(pages_utils.TempDataSetField[0])] = new_data
            # 获取两个DataFrame列名的交集
            intersection_cols = pages_utils.getIntersectionCols(
                data33, pages_utils.TempDataSet[0]
            )
            # 合并数据
            pages_utils.TempDataSet[0] = pd.merge(
                data33, pages_utils.TempDataSet[0],
                on=intersection_cols, how="left")
        print('======================实时原始数据集======================')
        print(pages_utils.TempDataSet[0])
        # st.markdown('--合并后--')
        # st.markdown(pages_utils.TempDataSet[0].columns)
        # st.markdown(new_data)
        # st.markdown(pages_utils.TempDataSetField[0])

with dataSCR:
    st.markdown("##### 文件上传状态显示")
    placeholder = st.empty()
    with placeholder.container():
        st.data_editor(
            pages_utils.TempDataSetField[0], height=390, width=800,
            disabled=["数据集", "文件名称", "传输状态", "上传时间"],
            column_order=["数据类型", "文件名称", "传输状态", "上传时间"],
            hide_index=False, )
