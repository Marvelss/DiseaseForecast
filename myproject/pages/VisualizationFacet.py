"""
@Author : SakuraFox
@Time: 2024-02-26 9:49
@File : Visualization.py
@Description : 数据可视化-面状
"""
import os
import zipfile

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
import seaborn as sns
from st_pages import hide_pages

from lib.share import RESOURCE_MODELRESULT_PATH
from pages import pages_utils

st.set_page_config(
    layout="wide"
)

# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
if st.session_state.isPlanarInterface:
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
            "数据下载中心",
        ]
    )
else:
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
            "数据下载中心-面状",
        ]
    )


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("gbk")


# with tab1:
tab1, tab2 = st.tabs(['数据下载', '可视化(待完成)'])

with tab1:
    col1, col2 = st.columns([0.7, 0.2])
    with col2:
        st.markdown('###### 模型结构与训练结果下载')
        # option55 = st.radio("选择下载内容",
        #                     options=['数据集', '各环节方法执行记录'],
        #                     label_visibility='collapsed')
        # st.markdown('---')
        # column = ['无数据']
        # data = pd.DataFrame(columns=['无数据'])
        #
        # # 从第二个元素开始获取
        # if not st.session_state["leftTabs"][1:]:
        #     downloadList = ['空']
        # else:
        #     downloadList = st.session_state["leftTabs"][1:]
        # option55 = pills("选择下载数据集类型或各环节数据名称", options=downloadList)
        # st.markdown('---')
        # if option55 == '模型':
        #     result1 = pages_utils.multiselect_all(
        #         st, '全选',
        #         pages_utils.TempDataSetField[4]['模型'],
        #         'temp11', 'collapsed')
        #     btn11 = st.button('下载特征和标签、模型结构及训练结果')
        # elif option55 == '预处理后数据集':
        #     column = pages_utils.TempDataSet[1].columns.tolist()
        #     data = pages_utils.TempDataSet[1]
        # elif option55 == '备选特征':
        #     column = pages_utils.TempDataSet[2].columns.tolist()
        #     data = pages_utils.TempDataSet[2]
        # elif option55 == '优选特征':
        #     column = pages_utils.TempDataSet[3].columns.tolist()
        #     data = pages_utils.TempDataSet[3]
        result1 = pages_utils.multiselect_all(
            st, '全选',
            pages_utils.TempDataSetField[4]['模型'],
            'temp111', 'collapsed')
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

    with col1:
        st.markdown('###### 数据集')
        arr1 = st.session_state["leftTabs"]
        tt1 = st.tabs(st.session_state["leftTabs"])
        for i in range(len(st.session_state["leftTabs"])):
            with tt1[i]:
                st.dataframe(
                    pages_utils.TempDataSet[i],
                    height=250, width=1500)
        st.markdown('###### 各环节方法执行记录')
        tt2 = st.tabs(st.session_state["leftTabs"])
        for j in range(len(st.session_state["leftTabs"])):
            with tt2[j]:
                st.dataframe(
                    pages_utils.TempDataSetField[j],
                    height=250, width=1500)
with col2:
    with tab2:
        col111, col222 = st.columns([0.2, 0.7])
        with col111:
            column1 = ['无数据']
            data1 = pd.DataFrame(columns=['无数据'])
            option4 = st.selectbox(
                '选择数据集或模型',
                options=st.session_state["leftTabs"])
            if option4 == '模型':
                column1 = pages_utils.TempDataSet[4].columns.tolist()
                data1 = pages_utils.TempDataSet[4]
            elif option4 == '预处理后数据集':
                column1 = pages_utils.TempDataSet[1].columns.tolist()
                data1 = pages_utils.TempDataSet[1]
            elif option4 == '备选特征':
                column1 = pages_utils.TempDataSet[2].columns.tolist()
                data1 = pages_utils.TempDataSet[2]
            elif option4 == '优选特征':
                column1 = pages_utils.TempDataSet[3].columns.tolist()
                data1 = pages_utils.TempDataSet[3]
            option1 = st.selectbox(
                '选择图形',
                options=('散点图', '直方图'))
            option2 = st.selectbox(
                '选择X轴',
                options=column1)
            option3 = st.selectbox(
                '选择Y轴',
                options=column1)
            interval_col1, interval_col2 = st.columns([1.4, 1])
            btn = interval_col2.button('添加图形')

        with col222:
            if btn:
                if option1 == '散点图':
                    # 取x,y轴数据
                    # file = data[option3]
                    print(option2)
                    print(option3)
                    print(file)
                    # 以下未实现x轴和y轴数据合并成绘图格式
                    plt.rc("font", family='Microsoft YaHei')
                    tab1, tab2 = st.tabs(["1", "2"])
                    with tab1:
                        # 绘制最高温度和最低温度的折线图
                        plt.figure(figsize=(10, 5))
                        sns.lineplot(data=file, x="Year", y="Precipitation", label="降水量")
                        plt.xlabel('日期')
                        plt.ylabel('降水累积量(mm)')
                        plt.title('降水累积量特征')
                        plt.legend()
                        st.pyplot(plt)
            else:
                st.markdown('可视化')
