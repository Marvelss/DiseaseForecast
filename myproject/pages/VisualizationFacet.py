"""
@Author : SakuraFox
@Time: 2024-02-26 9:49
@File : Visualization.py
@Description : 数据下载-面状
"""
import zipfile
from collections import deque

import streamlit as st
import os

from st_pages import hide_pages
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap
from lib.share import RESOURCE_MODELRESULT_PATH, RESOURCE_TEMPDIR_PATH, RESOURCE_PROCESS_PATH
from pages import pages_utils

st.set_page_config(
    layout="wide"
)
hide_pages(
    [
        "测试界面",
        "原始数据",
        "数据预处理",
        "特征计算",
        "特征优选",
        "模型构建",
        "基于天气情景生成器的模型评价",
        "建模报告",
        "模型应用",

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

# 显示地图图层,创建一个最大长度为5的队列
if 'VisualMapLayer' not in st.session_state:
    st.session_state.VisualMapLayer = deque(maxlen=2)


st.markdown(
    """
    <style>
    h2 {
        margin-top: -100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.header('多场景作物病虫害快速预测建模系统')
def findFeatureFile(featureList, fileList):
    # 创建一个字典来存储特征名称及其对应的文件
    feature_files = {}

    # 遍历每个特征名称
    for feature in featureList:
        # 找出所有文件名中包含特征名称的文件
        matched_files = [file for file in fileList if feature in file]

        # 将结果存储在字典中
        feature_files[feature] = matched_files
    matched_files = [file for files in feature_files.values() for file in files]
    return matched_files


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


# st.markdown('#### 预处理和特征计算环节数据集下载')
colFCFV1, colFCFV2, colFCFV3 = st.columns([0.3, 0.7, 0.2])
with colFCFV1:
    st.markdown("##### 数据与特征选择")
    with st.container(height=750, border=False):
        if len(pages_utils.PreprocessedDataSetFieldFacet['编号']) == 0:
            leftBarsPreData = [{"label": "预处理后数据", "value": "预处理后数据"}]
        else:
            leftBarsPreData = tree_select(nodes=pages_utils.updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet))
        leftBarsFCalData = tree_select(nodes=pages_utils.updateLeftBars(pages_utils.FeatureDataSetFieldFacet))
with colFCFV2:
    onVisual = st.toggle(label="选中文件时自动显示对应图层", help='图层加载时间较长')

    # 初始化地图
    pe = st.empty()
    with pe:
        mV1 = leafmap.Map(center=st.session_state.areaCenter, zoom_start=16)
        mV1.add_basemap('SATELLITE')

        with st.status('加载数据中...'):
            tempList = []
            if len(pages_utils.RawDataSetFieldFacet['编号']) != 0:
                if len(leftBarsPreData) != 1:
                    tempList = tempList + leftBarsPreData['checked']
                if len(leftBarsFCalData) != 1:
                    tempList = tempList + leftBarsFCalData['checked']
                else:
                    tempList = [{"label": "无数据", "value": "无数据"}]
                # print(leftBarsFCalData['checked'])
                for name in tempList:
                    if '.' in name:
                        st.session_state.VisualMapLayer.append(name)
                if not onVisual:
                    st.session_state.VisualMapLayer.clear()
                for tempLayer in st.session_state.VisualMapLayer:
                    path = os.path.join(RESOURCE_TEMPDIR_PATH, tempLayer)
                    addLayer(mV1, path)
                    st.header(f'{tempLayer}文件加载完成')
        mV1.to_streamlit()
with colFCFV3:
    st.markdown("##### 数据下载")
    zipPath = os.path.join(
        RESOURCE_PROCESS_PATH, '面状数据下载.zip')
    with zipfile.ZipFile(zipPath, 'w') as zipf:
        pass  # 不添加任何文件
    # 输入压缩包的文件路径
    zipFilesPath = []
    for fileName in tempList:
        if '.' not in fileName:
            continue
        # 遍历文件夹及子文件夹下的所有文件
        for root, dirs, files in os.walk(RESOURCE_TEMPDIR_PATH):
            for file_name in files:
                # 打印文件名
                # print(file_name)
                if fileName == file_name:
                    zipFilesPath.append(os.path.join(RESOURCE_TEMPDIR_PATH, file_name))
                    break
                else:
                    pass
                    # print(f"文件:{fileName} 未找到\n")

    pages_utils.zip_files(zipFilesPath, zipPath)
    with open(zipPath, "rb") as file:
        st.download_button(
            label="下载",
            data=file,
            file_name="面状数据下载.zip",
            mime="application/zip",
        )
# st.markdown('#### 特征优选环节数据')
#
# st.dataframe(
#     pages_utils.TempDataSetField[3],
#     height=250, width=1500)
st.markdown('---')
st.markdown('##### 模型结构与训练结果下载')
result1 = pages_utils.multiselect_all(
    st.columns([0.3, 0.6, 0.4])[0], '全选',
    pages_utils.TempDataSetFieldFacet[4]['模型'],
    'temp111', 'collapsed')
if not pages_utils.TempDataSetFieldFacet[4].empty:
    models = pages_utils.TempDataSetFieldFacet[4]['模型'].tolist()
    modelsStruct = pages_utils.TempDataSetFieldFacet[4]['模型结构'].tolist()
    modelResult = pages_utils.TempDataSetFieldFacet[4]['模型训练结果'].tolist()

    zipPath = os.path.join(
        RESOURCE_MODELRESULT_PATH, '模型结构与训练结果.zip')

    with zipfile.ZipFile(zipPath, 'w') as zipf:
        pass  # 不添加任何文件
    # 输入压缩包的文件路径
    zipFilesPath = []
    for model in result1:
        row = pages_utils.TempDataSetFieldFacet[4][pages_utils.TempDataSetFieldFacet[4]['模型'] == model]
        if not row.empty:
            model_structure = row['模型结构'].values[0]
            model_training_result = row['模型训练结果'].values[0]
            # print(f"匹配到模型: {model}")
            # print(f"模型结构: {model_structure}")
            # print(f"模型训练结果: {model_training_result}\n")

            rootPathTemp = RESOURCE_MODELRESULT_PATH

            modelStructurePath = os.path.join(rootPathTemp,
                                              'structure', model_structure)
            # 保存预测结果
            modelResultPath = os.path.join(rootPathTemp,
                                           'predict',
                                           model_training_result)
            # print(modelStructurePath)
            # print(modelResultPath)
            zipFilesPath.append(modelStructurePath)
            zipFilesPath.append(modelResultPath)
        else:
            print(f"模型 {model} 未找到\n")

    pages_utils.zip_files(zipFilesPath, zipPath)
    with open(zipPath, "rb") as file:
        st.download_button(
            label="下载",
            data=file,
            file_name="模型结构与训练结果.zip",
            mime="application/zip",
        )
st.markdown('---')
st.markdown('##### 模拟气象情景数据下载')
zipPath = os.path.join(RESOURCE_TEMPDIR_PATH, '基于天气情景生成器的模拟数据.zip')
# 压缩生成的xlsx数据
pathEE = os.path.join(RESOURCE_PROCESS_PATH, 'weatherGeneratorOutput')
pages_utils.zip_folder(pathEE, zipPath)
with open(zipPath, "rb") as file:
    st.download_button(
        label="下载模拟生成的气象数据",
        data=file,
        file_name="基于天气情景生成器的模拟数据.zip",
        mime="application/zip",
    )