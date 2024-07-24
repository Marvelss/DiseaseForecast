"""
@Author : SakuraFox
@Time: 2024-07-05 10:14
@File : test.py
@Description : 原始数据界面-面状
"""
import os
import time
from datetime import datetime

import streamlit as st
from st_pages import hide_pages, show_pages
from stqdm import stqdm
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
# 地图
if 'dSFmap' not in st.session_state:
    st.session_state.dSFmap = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)


@st.cache_resource
def get_database_session():
    # Create a database session object that points to the URL.
    return st.session_state.dSFmap


# json1 = [
#         {"label": "原始数据集", "value": "原始数据集"},
#         {
#             "label": "预处理数据集",
#             "value": "预处理数据集",
#             "children": [
#                 {"label": "temperature_1", "value": "temperature_1_2024"},
#                 {"label": "temperature_2", "value": "temperature_2_2024"},
#                 {"label": "temperature_3", "value": "temperature_3_2024"},
#             ],
#         },
#         {
#             "label": "特征计算数据集",
#             "value": "特征计算数据集",
#             "children": [
#                 {"label": "晚稻移栽期", "value": "sub_d"},
#                 {
#                     "label": "预测峰值",
#                     "value": "sub_e",
#                     "children": [
#                         {"label": "测报站点", "value": "sub_sub4"},
#                         {"label": "生化指标", "value": "sub_s5"},
#                     ],
#                 },
#                 {"label": "生化指标", "value": "sub_f"},
#             ],
#         },
#         {"label": "特征优选数据集",
#          "value": "特征优选数据集",
#          "children": [
#              {"label": "模板文件", "value": "模板文件"},
#              {"label": "待提取特征文件", "value": "待提取特征文件"},
#          ],
#          },
#     ]
if 'leftBars' not in st.session_state:
    st.session_state.leftBars = [
        {
            "label": "原始数据集",
            "value": "原始数据集",
            "children": [
                {"label": "气象数据", "value": "气象数据"}
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


# 更新左侧目标显示
def updateLeftBars(raw_data_facet):
    # 初始化 leftBars 从 RawDataSetFieldFacet 获取数据
    left_bars = []
    structure = {}

    for i in range(len(raw_data_facet["编号"])):
        root = raw_data_facet["根节点"][i]
        child = raw_data_facet["子节点"][i]
        file_name1 = raw_data_facet["文件名称"][i]
        file_value = f"{file_name1}.{raw_data_facet['数据格式'][i]}"

        if root not in structure:
            structure[root] = {}

        if child not in structure[root]:
            structure[root][child] = []

        structure[root][child].append({"label": file_name1, "value": file_value})

    for root, children in structure.items():
        root_node = {"label": root, "value": root, "children": []}
        for child, files in children.items():
            child_node = {"label": child, "value": child, "children": files}
            root_node["children"].append(child_node)
        left_bars.append(root_node)

    return left_bars


# st.markdown(f'测试左侧数据不显示问题:{st.session_state.leftBars}')
# ==============================文件上传显示==============================
dataSCM, dataSCMap, dataSCR = st.columns([0.2, 0.9, 0.3])
# dataSCM, dataSCMap = st.columns([0.2, 0.7])
with dataSCM:
    st.markdown("##### 数据与特征")
    checkedNameList = [f"{name}.{format1}" for name, format1 in zip(
        pages_utils.RawDataSetFieldFacet['文件名称'],
        pages_utils.RawDataSetFieldFacet['数据格式'])]
    with st.container(height=750, border=False):
        temp = tree_select(nodes=st.session_state.leftBars, checked=checkedNameList)

# ==============================右侧文件上传状态显示==============================
with dataSCMap:
    placeHolderDSF = st.empty()
    with placeHolderDSF:
        map1 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

        # 初始化地图
        # m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

        # 后续删除,为结果可视化而用
        # # 点
        # m.add_shp(r'E:\a_python\program\testPlatform\demo\demo137\test3\02_05shp.shp', layer_name="point")
        # # 插值后
        # m.add_raster(r'E:\a_python\program\testPlatform\demo\demo138\reveal\output_file2.tif',layer_name='interpolation')
        # # 掩膜模板
        # m.add_shp(r'E:\a_python\program\testPlatform\demo\demo138\reveal\zjsshp.shp',layer_name='coverTemplate')
        # # 裁剪后
        # m.add_raster(r'E:\a_python\program\testPlatform\demo\demo138\reveal\output_file_cropped.tif',layer_name='cropped')
        with st.status('加载数据中...'):
            for name in temp['checked']:
                if '.' in name and name.split('.')[0] in pages_utils.TempDataSetFieldFacet[0]['文件名称']:
                    path = os.path.join(
                        os.getcwd(),
                        'resource',
                        'uploadFileDir', name)
                    print('=============')
                    print(path)
                    # map1.add_raster(path, layer_name=name.split('.')[0])
                    # map1.add_shp(path, layer_name=name.split('.')[0])
                    # map1.add_shp(r'E:\a_python\program\testPlatform\demo\demo137\test3\02_05shp.shp', layer_name="point")
                    st.header(f'{name}加载完成')
        map1.to_streamlit()
with dataSCR:
    st.markdown("##### 上传数据集")

    selectedTemplate = pills("选择数据集", ['气象数据', '植保数据(未开放)', '遥感数据(未开放)'], ["🌨️️", "🌾", "🚁"])
    suuDirName = st.text_input(label='子文件夹名称', value='气象数据')
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

    # st.markdown('---')

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
                    # st.toast(f"文件 {fileName} 已存在,跳过上传", icon="⚠️")
                    continue
                new_entry = {
                    "编号": pages_utils.generateID(),
                    "数据类型": selectedTemplate,
                    "根节点": '原始数据集',
                    "子节点": suuDirName,
                    "文件名称": fileName,
                    "数据格式": fileFormat,
                    "传输状态": "已上传",
                    "上传时间": datetime.now().strftime("%H:%M:%S"),
                    "字段": '暂无'}
                # 添加到TempDataSetFieldFacet[0]
                for key in pages_utils.TempDataSetFieldFacet[0].keys():
                    pages_utils.TempDataSetFieldFacet[0][key].append(new_entry[key])
                # print('============更新原始数据============')
                # print(pages_utils.TempDataSetFieldFacet[0])

            # 上传出错提示
            except BaseException as e:
                st.toast('上传错误,请检测文件内容及格式无误后重新上传', icon="⚠️")
                raise e
        # 更新左侧目标显示
        st.session_state.leftBars = updateLeftBars(pages_utils.RawDataSetFieldFacet)

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
