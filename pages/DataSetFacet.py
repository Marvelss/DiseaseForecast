"""
@Author : SakuraFox
@Time: 2024-07-05 10:14
@File : test.py
@Description : 原始数据界面-面状
"""
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from st_pages import hide_pages, show_pages
from streamlit import Page
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap

import pages_utils
from streamlit_pills import pills
from warnings import simplefilter

simplefilter(action="ignore", category=FutureWarning)
st.set_page_config(
    layout="wide"
)
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")
if 'count' not in st.session_state:
    st.session_state.count = 0

if 'leftBars' not in st.session_state:
    st.session_state.leftBars = [
        {"label": "原始数据集", "value": "原始数据集"},
        {
            "label": "预处理数据集",
            "value": "预处理数据集",
            "children": [
                {"label": "temperature_1", "value": "temperature_1_2024"},
                {"label": "temperature_2", "value": "temperature_2_2024"},
                {"label": "temperature_3", "value": "temperature_3_2024"},
            ],
        },
        {
            "label": "特征计算数据集",
            "value": "特征计算数据集",
            "children": [
                {"label": "晚稻移栽期", "value": "sub_d"},
                {
                    "label": "预测峰值",
                    "value": "sub_e",
                    "children": [
                        {"label": "测报站点", "value": "sub_sub4"},
                        {"label": "生化指标", "value": "sub_s5"},
                    ],
                },
                {"label": "生化指标", "value": "sub_f"},
            ],
        },
        {"label": "特征优选数据集",
         "value": "特征优选数据集",
         "children": [
             {"label": "模板文件", "value": "模板文件"},
             {"label": "待提取特征文件", "value": "待提取特征文件"},
         ],
         },
    ]
# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据",
        "数据预处理",
        "特征计算",
        "特征优选",
    ]
)


# st.navigation([
#     st.Page("App.py", title='主页'),
#     st.Page("DataSetFacet.py", title='原始'),
#     st.Page("FeatureOptimizationFacet.py", title='特征优选'),
#     st.Page("DataPreparationFacet.py"),
# ])

# 保存文件到本地

def savedFile(uploadedFile):
    filePath = os.path.join(
        os.getcwd(),
        'resource',
        'uploadFileDir',
        uploadedFile.name)
    # 模型文件保存到本地
    with open(filePath, 'wb') as f:
        f.write(uploadedFile.read())


empty1 = st.empty()
# ==============================文件上传显示==============================
dataSCM, dataSCMap, dataSCR = st.columns([0.2, 0.7, 0.4])
with dataSCM:
    # with empty1.container():
    temp = tree_select(st.session_state.leftBars)
    st.markdown(temp)

btn = st.button('上传')

if btn:
    new_node = {
        "label": f"新数据节点{st.session_state.count}",
        "value": f"新数据值{st.session_state.count}",
        "children": [
            {"label": f"子节点{st.session_state.count}",
             "value": f"子节点{st.session_state.count}值"},
        ]
    }
    st.session_state.count += 1
    # 将新节点添加到现有的leftBars列表中
    st.session_state.leftBars.append(new_node)
    st.rerun()
with dataSCMap:
    pass
    # # 初始化地图
    # m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
    #
    # m.to_streamlit()

# ==============================右侧文件上传状态显示==============================
with dataSCR:
    st.markdown("##### 上传数据集")

    selectedTemplate = pills("选择数据集", ['气象数据', '植保数据(未开放)', '农学数据(未开放)'], ["🌨️️", "🌾", "☣️"])

    uploaded_files = st.file_uploader(
        "上传数据集",
        accept_multiple_files=True,
        label_visibility='collapsed',
        type=['tif', 'shp', 'txt'],
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
        # with placeholder1.container():
        st.warning('warningMInfo', icon="⚠️")
    #     with open(path1, "rb") as file:
    #         st.download_button(
    #             label="下载气象数据模板",
    #             data=file,
    #             file_name="气象数据-模板.xlsx",
    #             mime="application/octet-stream"
    #         )
    if selectedTemplate == '植保数据':
        # with placeholder1.container():
        st.warning('warningPInfo', icon="⚠️")
    #     with open(path2, "rb") as file:
    #         st.download_button(
    #             label="下载植保数据模板",
    #             data=file,
    #             file_name="植保数据-模板.xlsx",
    #             mime="application/octet-stream"
    #         )
    if selectedTemplate == '农学数据':
        with placeholder1.container():
            st.warning('warningAInfo', icon="⚠️")
            # with open(path3, "rb") as file:
            #     st.download_button(
            #         label="下载农学数据模板",
            #         data=file,
            #         file_name="农学数据-模板.xlsx",
            #         mime="application/octet-stream"
            #     )
    # ==============================控制文件上传逻辑==============================
    if uploaded_files:
        # 获取已有文件名的集合
        existing_file_names = set(pages_utils.TempDataSetFieldFacet[0]['文件名称'])
        for uploaded_file in uploaded_files:
            try:
                # 保存文件到本地
                savedFile(uploaded_file)
                # 获取文件名
                file_name = uploaded_file.name
                # 输出文件信息
                tempNF = uploaded_file.name.split('.')
                fileName = tempNF[0]
                fileFormat = tempNF[1]
                # 防止重复添加
                if fileName in existing_file_names:
                    st.toast(f"文件 {fileName} 已存在,跳过上传", icon="⚠️")
                    continue
                new_entry = {
                    "编号": pages_utils.generateID(),
                    "数据类型": selectedTemplate,
                    "文件名称": fileName,
                    "数据格式": fileFormat,
                    "传输状态": "已上传",
                    "上传时间": datetime.now().strftime("%H:%M:%S"),
                    "字段": '暂无'}
                # 添加到TempDataSetFieldFacet[0]
                for key in pages_utils.TempDataSetFieldFacet[0].keys():
                    pages_utils.TempDataSetFieldFacet[0][key].append(new_entry[key])
            # 上传出错提示
            except BaseException as e:
                st.toast('上传错误,请检测文件内容及格式无误后重新上传', icon="⚠️")
                raise e
        print('======================原始数据集======================')
        st.markdown(pages_utils.TempDataSetFieldFacet[0])
