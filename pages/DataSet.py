# page2.py
from datetime import datetime

import pandas as pd
import streamlit as st

import pages_utils

from warnings import simplefilter

simplefilter(action="ignore", category=FutureWarning)
st.set_page_config(
    layout="wide"
)
# 模板路径及注释信息
path1 = r'E:\a_python\program\diseaseForecastStreamlit\resource\气象数据-模板.xlsx'
path2 = r'E:\a_python\program\diseaseForecastStreamlit\resource\植保数据-模板.xlsx'
path3 = r'E:\a_python\program\diseaseForecastStreamlit\resource\农学数据-模板.xlsx'

warningMInfo = '''
注意事项
1. 模版中的表头名称不可更改,表头行不可删除;
2. 删除示例数据后,添加新数据.
'''
warningPInfo = '''
    注意事项
1. 植保站数据每5天为周期记录一次数据;
2. 模版中的表头名称不可更改,表头行不可删除;
3. 删除示例数据后,添加新数据.
    '''
warningAInfo = '''
    注意事项
1. 模版中的表头名称不可更改,表头行不可删除;
2. 删除示例数据后,添加新数据.
    '''
# ==============================文件上传显示==============================
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
    # ==============================右侧数据模板下载及注意事项==============================
    st.markdown("##### 数据模板下载及注意事项")
    placeholder1 = st.empty()
    if ab == '气象数据':
        with placeholder1.container():
            st.warning(warningMInfo, icon="⚠️")
            with open(path1, "rb") as file:
                st.download_button(
                    label="下载气象数据模板",
                    data=file,
                    file_name="气象数据-模板.xlsx",
                    mime="application/octet-stream"
                )
    if ab == '植保数据':
        with placeholder1.container():
            st.warning(warningPInfo, icon="⚠️")
            with open(path2, "rb") as file:
                st.download_button(
                    label="下载植保数据模板",
                    data=file,
                    file_name="植保数据-模板.xlsx",
                    mime="application/octet-stream"
                )
    if ab == '农学数据':
        with placeholder1.container():
            st.warning(warningAInfo, icon="⚠️")
            with open(path3, "rb") as file:
                st.download_button(
                    label="下载农学数据模板",
                    data=file,
                    file_name="农学数据-模板.xlsx",
                    mime="application/octet-stream"
                )
    # ==============================控制文件上传逻辑==============================
    if uploaded_files:
        bytes_data = uploaded_files.read()
        data33 = pd.read_excel(bytes_data)
        # st.markdown(data33)
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": ab, "文件名称": uploaded_files.name, "传输状态": "已上传",
            "上传时间": datetime.now().strftime("%H:%M:%S"),
            "字段": data33.columns.tolist()}

        # 防止重复添加
        if (pages_utils.TempDataSetField[0]['文件名称'] == uploaded_files.name).any():
            pass
        else:
            # 添加并合并至原始数据集
            pages_utils.TempDataSetField[0].loc[len(pages_utils.TempDataSetField[0])] = new_data
            # 获取两个DataFrame列名的交集
            intersection_cols = pages_utils.getIntersectionCols(
                data33, pages_utils.TempDataSet[0]
            )
            # 合并数据
            pages_utils.TempDataSet[0] = pd.merge(
                data33, pages_utils.TempDataSet[0],
                on=intersection_cols, how="outer")
        print('======================实时原始数据集======================')
        print(pages_utils.TempDataSet[0])
# ==============================右侧文件上传状态显示==============================
with dataSCR:
    st.markdown("##### 文件上传状态显示")
    placeholder = st.empty()
    with placeholder.container():
        st.data_editor(
            pages_utils.TempDataSetField[0], height=390, width=800,
            disabled=["数据集", "文件名称", "传输状态", "上传时间"],
            column_order=["数据类型", "文件名称", "传输状态", "上传时间"],
            hide_index=False, )
