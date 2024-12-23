"""
@Author : SakuraFox
@Time: 2024-02-26 9:49
@File : Visualization.py
@Description : 数据可视化
"""
import os
import zipfile

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
import seaborn as sns
from st_pages import hide_pages

from lib.share import RESOURCE_MODELRESULT_PATH, RESOURCE_TEMPDIR_PATH, RESOURCE_PROCESS_PATH
from pages import pages_utils

st.set_page_config(
    layout="wide"
)

# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据-面状",
        "数据预处理-面状",
        "特征计算-面状",
        "特征优选-面状",
        "模型构建-面状",
        "基于天气情景生成器的模型评价-面状",
        "建模报告-面状",
        "模型应用-面状",
        "数据下载中心-面状",
    ]
)

# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr2 {display: none;}
    </style>
    """, unsafe_allow_html=True)
st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("gbk")


# col1, col2 = st.columns([0.7, 0.2])

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
st.markdown('###### 数据集')

tt1 = st.tabs(['预处理', '备选特征', '优选特征', '模型'])
with tt1[0]:
    st.dataframe(
        pages_utils.TempDataSet[1],
        height=250, width=1500)
with tt1[1]:
    st.dataframe(
        pages_utils.TempDataSet[2],
        height=250, width=1500)
with tt1[2]:
    st.dataframe(
        pages_utils.TempDataSet[3],
        height=250, width=1500)
with tt1[3]:
    st.dataframe(
        pages_utils.TempDataSet[4],
        height=250, width=1500)
st.markdown('###### 各环节方法执行记录')
tt2 = st.tabs(['原始数据', '预处理后数据', '备选特征', '优选特征', '模型'])
for j in range(len(['原始数据', '预处理后数据', '备选特征', '优选特征', '模型'])):
    with tt2[j]:
        st.dataframe(
            pages_utils.TempDataSetField[j],
            height=250, width=1500)

st.markdown('###### 模型结构与训练结果下载')
# result1 = pages_utils.multiselect_all(
#     st, '全选',
#     pages_utils.TempDataSetField[4]['模型'],
#     'temp111', 'collapsed')
result1 = st.columns(3)[0].multiselect('模型下载', pages_utils.TempDataSetField[4]['模型'], label_visibility='collapsed')
if not pages_utils.TempDataSetField[4].empty:
    models = pages_utils.TempDataSetField[4]['模型'].tolist()
    modelsStruct = pages_utils.TempDataSetField[4]['模型结构'].tolist()
    modelResult = pages_utils.TempDataSetField[4]['模型训练结果'].tolist()

    zipPath = os.path.join(
        RESOURCE_MODELRESULT_PATH, '模型结构与训练结果.zip')

    with zipfile.ZipFile(zipPath, 'w') as zipf:
        pass  # 不添加任何文件
    # 输入压缩包的文件路径
    zipFilesPath = []
    for model in result1:
        row = pages_utils.TempDataSetField[4][pages_utils.TempDataSetField[4]['模型'] == model]
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

# st.markdown('###### 模拟气象情景数据下载')
#
# zipPath = os.path.join(RESOURCE_TEMPDIR_PATH, '基于天气情景生成器的模拟数据.zip')
# # 压缩生成的xlsx数据
# pathEE = os.path.join(RESOURCE_PROCESS_PATH, 'weatherGeneratorOutput')
# pages_utils.zip_folder(pathEE, zipPath)
# with open(zipPath, "rb") as file:
#     st.download_button(
#         label="下载模拟生成的气象数据",
#         data=file,
#         file_name="基于天气情景生成器的模拟数据.zip",
#         mime="application/zip",
#     )
