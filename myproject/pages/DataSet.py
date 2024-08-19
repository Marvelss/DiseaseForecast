# page2.py
import os.path
from datetime import datetime

import pandas as pd
import streamlit as st
from st_pages import hide_pages

from lib.share import RESOURCE_TEMPLATE_PATH
from pages import pages_utils
from streamlit_pills import pills
from warnings import simplefilter

simplefilter(action="ignore", category=FutureWarning)
st.set_page_config(
    layout="wide"
)
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")

# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据-面状",
        "数据预处理-面状",
        "特征计算-面状",
        "特征优选-面状",
        "模型构建-面状",
    ]
)
# 模板路径及注释信息
path1 = os.path.join(RESOURCE_TEMPLATE_PATH, '气象数据-模板.xlsx')
path2 = os.path.join(RESOURCE_TEMPLATE_PATH, '植保数据-模板.xlsx')
path3 = os.path.join(RESOURCE_TEMPLATE_PATH, '农学数据-模板.xlsx')

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

emptyHeadDSP = st.empty()
# ==============================文件上传显示==============================
dataSCM, dataSCR = st.columns([0.7, 0.4])
with dataSCM:
    st.markdown("##### 上传数据集")

    selectedTemplate = pills("选择数据集", ['气象数据', '植保数据', '农学数据'], ["🌨️️", "🌾", "☣️"])

    uploaded_files = st.file_uploader(
        "上传数据集",
        accept_multiple_files=False,
        label_visibility='collapsed',
        type=['xlsx', 'csv', 'txt', 'xls', 'zip'],
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
    if selectedTemplate == '气象数据':
        with placeholder1.container():
            st.warning(warningMInfo, icon="⚠️")
            with open(path1, "rb") as file:
                st.download_button(
                    label="下载气象数据模板",
                    data=file,
                    file_name="气象数据-模板.xlsx",
                    mime="application/octet-stream"
                )
    if selectedTemplate == '植保数据':
        with placeholder1.container():
            st.warning(warningPInfo, icon="⚠️")
            with open(path2, "rb") as file:
                st.download_button(
                    label="下载植保数据模板",
                    data=file,
                    file_name="植保数据-模板.xlsx",
                    mime="application/octet-stream"
                )
    if selectedTemplate == '农学数据':
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
    with emptyHeadDSP:
        with st.spinner('处理数据中...'):
            if uploaded_files:
                # print(uploaded_files)
                try:
                    bytes_data = uploaded_files.read()
                    data33 = pd.read_excel(bytes_data)
                    isErrorData = False
                    # 检测非数值型输入
                    # 取前10行
                    subset = data33.head(10)

                    # 检测每一列是否包含非数值型数据，并显示对应的列名
                    non_numeric_columns = []

                    for column in subset.columns:
                        if not pd.to_numeric(subset[column], errors='coerce').notna().all():
                            non_numeric_columns.append(column)
                    # 去除上级单位、测报站点(固定)
                    tempT1 = [col for col in non_numeric_columns if col not in ['上级单位', '测报站点']]

                    # 防止重复添加
                    if (pages_utils.TempDataSetField[0]['文件名称'] == uploaded_files.name).any():
                        pass
                    # 存在非数值型输入
                    elif len(tempT1):
                        tempT2 = ' '.join(tempT1)
                        st.toast(f'以下列存在非数值型数据,请转换为数值后重新上传  \n字段:{tempT2}', icon="⚠️")
                    # 正确情况
                    else:
                        new_data = {
                            "编号": pages_utils.generateID(),
                            "数据类型": selectedTemplate, "文件名称": uploaded_files.name, "传输状态": "已上传",
                            "上传时间": datetime.now().strftime("%H:%M:%S"),
                            "字段": data33.columns.tolist()}
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
                # 上传出错提示
                except BaseException as e:
                    st.toast('上传错误  \n请检查文件内容及格式无误后重新上传', icon="⚠️")
                    # new_data = {
                    #     "编号": pages_utils.generateID(),
                    #     "数据类型": selectedTemplate, "文件名称": uploaded_files.name, "传输状态": "上传出错",
                    #     "上传时间": datetime.now().strftime("%H:%M:%S"),
                    #     "字段": '未识别'}
                    # pages_utils.TempDataSetField[0].loc[len(pages_utils.TempDataSetField[0])] = new_data
                print('======================原始数据集======================')
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
