"""
@Author : SakuraFox
@Time: 2024-07-05 10:14
@File : test.py
@Description : 原始数据界面-面状
"""
import os
from datetime import datetime

import streamlit as st
from st_pages import hide_pages
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap
from collections import deque

from lib.share import RESOURCE_TEMPDIR_PATH
from pages import pages_utils
from streamlit_pills import pills
from warnings import simplefilter

simplefilter(action="ignore", category=FutureWarning)
st.set_page_config(
    layout="wide"
)
# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据",
        "数据预处理",
        "特征计算",
        "特征优选",
        "模型构建",
        "基于天气情景生成器的模型评价",
        "模型应用",
        "建模报告",
        "数据下载中心",
    ]
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")
if 'count' not in st.session_state:
    st.session_state.count = 0
# 地图
if 'dSFmap' not in st.session_state:
    st.session_state.dSFmap = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

# 显示地图图层,创建一个最大长度为2的队列
if 'dSMapLayer' not in st.session_state:
    st.session_state.dSMapLayer = deque(maxlen=2)


# 添加图层
def addLayer(mapTemp, filePath):
    fileNameT = os.path.basename(filePath)
    if 'tif' in fileNameT:
        mapTemp.add_raster(filePath,
                           layer_name=fileNameT.split('.')[0])
    elif 'shp' in fileNameT:
        mapTemp.add_shp(filePath,
                        layer_name=fileNameT.split('.')[0])
    elif 'json' in fileNameT:
        mapTemp.add_json(filePath,
                         layer_name=fileNameT.split('.')[0])


@st.cache_resource
def get_database_session():
    # Create a database session object that points to the URL.
    return st.session_state.dSFmap


# if 'leftBars' not in st.session_state:
#     st.session_state.leftBars = [
#         {
#             "label": "原始数据集",
#             "value": "原始数据集",
#             "children": [
#                 {"label": "气象数据", "value": "气象数据"}
#             ],
#         },
#     ]




# 保存文件到本地
def savedFile(uploadedFile):
    filePath = os.path.join(RESOURCE_TEMPDIR_PATH,
                            uploadedFile.name)
    # 模型文件保存到本地
    with open(filePath, 'wb') as f:
        f.write(uploadedFile.read())


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
        if len(pages_utils.RawDataSetFieldFacet['编号']) == 0:
            tree_select([{"label": "原始数据集", "value": "原始数据集", "children": []}])
        else:
            leftBarsRawData = tree_select(nodes=pages_utils.updateLeftBars(pages_utils.RawDataSetFieldFacet),
                                          checked=checkedNameList)

# ==============================右侧文件上传状态显示==============================
with dataSCMap:
    onDS = st.toggle(label="选中文件时自动显示对应图层",
                     help='图层加载时间较长',
                     value=False)

    placeHolderDSF = st.empty()
    # st.markdown(temp['checked'])

    with placeHolderDSF:
        map1 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

        # 初始化地图
        # m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

        # 后续删除,为结果可视化而用
        # # 点
        # m.add_shp(r'E:\a_python\program\testPlatform\demo1\demo137\test_fo_p\02_05shp.shp', layer_name="point")
        # # 插值后
        # m.add_raster(r'E:\a_python\program\testPlatform\demo1\demo138\reveal\output_file2.tif',layer_name='interpolation')
        # # 掩膜模板
        # m.add_shp(r'E:\a_python\program\testPlatform\demo1\demo138\reveal\zjsshp.shp',layer_name='coverTemplate')
        # # 裁剪后
        # m.add_raster(r'E:\a_python\program\testPlatform\demo1\demo138\reveal\output_file_cropped.tif',layer_name='cropped')
        with st.status('加载数据中...'):
            # 排除初次加载时
            if len(pages_utils.RawDataSetFieldFacet['编号']) != 0:
                for name in leftBarsRawData['checked']:
                    if '.' in name and name.split('.')[0] in pages_utils.TempDataSetFieldFacet[0]['文件名称']:
                        path = os.path.join(RESOURCE_TEMPDIR_PATH, name)
                        print('=============')
                        print(path)
                        st.session_state.dSMapLayer.append(path)

                if not onDS:
                    st.session_state.dSMapLayer.clear()
                # temp_last_two = [st.session_state.dSMapLayer[-i] for i in range(1, 3)]

                for layer in st.session_state.dSMapLayer:
                    path = os.path.join(RESOURCE_TEMPDIR_PATH, layer)
                    addLayer(map1, path)
                    st.header(f'{layer}加载完成')
        map1.to_streamlit()
with dataSCR:
    st.markdown("##### 上传数据集")

    selectedTemplate = pills("选择数据集", ['气象数据', '植保数据', '遥感数据'], ["🌨️️", "🌾", "🚁"])
    suuDirName = st.text_input(label='子文件夹名称', value=selectedTemplate)
    uploaded_files = st.file_uploader(
        "上传数据集",
        accept_multiple_files=True,
        label_visibility='collapsed',
        type=['tif', 'shp', 'txt', 'cpg',
              'dbf', 'prj', 'xml', 'shx', 'xlsx'],
        help='help')

    # st.markdown('''
    #     <style>
    #         .uploadedFile {display: none}
    #     <style>''',
    #             unsafe_allow_html=True)

    # st.markdown('---')

    # ==============================控制文件上传逻辑==============================
    count = 0
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
                # 不添加除shp外的相关数据
                if fileFormat.lower() in ['shx', 'cpg', 'dbf', 'prj', 'xml']:
                    continue
                new_entry = {
                    "编号": pages_utils.generateID(),
                    "数据类型": selectedTemplate,
                    "根节点": '原始数据集',
                    "子节点": suuDirName,
                    "字段": fileName.split('_')[0] if '_' in fileName else "其他",
                    "文件名称": fileName,
                    "数据格式": fileFormat,
                    "传输状态": "已上传",
                    "上传时间": datetime.now().strftime("%H:%M:%S")
                }
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
        # st.session_state.leftBars = updateLeftBars(pages_utils.RawDataSetFieldFacet)

    # ==============================右侧数据模板下载及注意事项==============================
    st.markdown("##### 数据上传注意事项")
    placeholder1 = st.empty()
    st.warning('shp文件名称不能以shp结尾', icon="⚠️")
