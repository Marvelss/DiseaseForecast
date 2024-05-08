import datetime
import io
import os.path
import pickle

import joblib
import scipy
import streamlit as st
import numpy as np
import pandas as pd
import matlab.engine
from sklearn.preprocessing import StandardScaler
from streamlit_pills import pills

import pages_utils

# 原始数据
if "dataSet" not in st.session_state:
    st.session_state["dataSet"] = pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])
# 已训练模型路径
if "trainedModel" not in st.session_state:
    st.session_state["trainedModel"] = {}

st.set_page_config(
    layout="wide"
)
# =======================可视化结果=======================
print('---')
col2, col3 = st.columns(2)
with col2:
    st.markdown("##### 输入原始数据")
    uploaded_dataSet = st.file_uploader(
        "输入原始字段",
        accept_multiple_files=False,
        label_visibility='collapsed')

with col3:
    st.markdown("##### 加载模型")
    uploaded_model = st.file_uploader("加载模型", label_visibility='collapsed')

if uploaded_dataSet:
    bytes_data = uploaded_dataSet.read()
    dataTemp = pd.read_excel(bytes_data)
    # 获取两个DataFrame列名的交集
    intersection_cols = pages_utils.getIntersectionCols(
        dataTemp, st.session_state["dataSet"]
    )
    # 合并数据
    st.session_state["dataSet"] = pd.merge(
        dataTemp, st.session_state["dataSet"],
        on=intersection_cols, how="outer")

if uploaded_model:
    modelPath = os.path.join(
        os.getcwd(),
        'resource',
        'uploadFileDir',
        uploaded_model.name)
    # 模型文件保存到本地
    with open(modelPath, 'wb') as f:
        f.write(uploaded_model.read())
    st.session_state["trainedModel"][uploaded_model.name.split('_')[0]] = modelPath
    st.markdown(st.session_state["trainedModel"])
st.markdown('---')
col1112, col1113 = st.columns([0.6, 0.4])
with col1112:
    st.markdown("##### 数据展示")
    st.data_editor(
        pages_utils.TempDataSet[0],
        height=550, width=1500)
with col1113:
    st.markdown("##### 各环节处理方法")
    st.info("注意:\n上传内容可直接从各环节导出", icon="ℹ️️")
    selectedTemplate = pills("选择数据处理步骤",
                             ['数据预处理',
                              '特征计算', '特征优选'])
    uploaded_files = st.file_uploader(
        "选择数据处理步骤",
        accept_multiple_files=False,
        label_visibility='collapsed',
        type=['xlsx', 'csv', 'txt', 'xls'],
        help='help')
    tab1, tab2, tab3, tab4 = st.tabs(["数据预处理", "特征计算", "特征优选", '模型'])
    with tab1:
        st.data_editor(
            pages_utils.TempDataSetField[1],
            height=220, width=800,
            column_order=['编号', '输入字段', '预处理后字段', '预处理方法'])
    with tab2:
        st.data_editor(
            pages_utils.TempDataSetField[2],
            height=220, width=800,
            column_order=['编号', '输入特征', '备选特征', '特征计算方法'])
        # temperature_data = simulate_temperature_data()
    with tab3:
        st.data_editor(
            pages_utils.TempDataSetField[3],
            height=220, width=800,
            column_order=['编号', '输入特征', '优选特征', '特征优选方法'])
    with tab4:
        st.data_editor(
            pages_utils.TempDataSetField[4],
            height=220, width=800,
            column_order=['编号', '模型', '特征', '标签', "评价指标", "数据集划分比例"])
    interval_col34, interval_col33 = st.columns([2.8, 1])
    # btn33 = interval_col33.button('运行')

    with interval_col33:
        @st.experimental_dialog("准备模型训练", width='large')
        def vote():
            beforeDF = st.session_state["dataSet"]
            isExtract = st.checkbox('提取有效值')
            # 分组并提取每个分组的第一个非空值
            result = beforeDF.groupby(['上级单位', '测报站点', '年']).first().reset_index()
            # ******删除包含缺失值的行******
            df_cleaned = result.dropna()
            if isExtract:
                a = st.data_editor(df_cleaned, num_rows="dynamic", width=700, height=300)
                pages_utils.TempDataSet[4] = df_cleaned
            else:
                b = st.data_editor(beforeDF, num_rows="dynamic", width=700, height=300)
                pages_utils.TempDataSet[4] = beforeDF
            # 选择后变化
            if st.button("Submit"):
                if isExtract:
                    print('开始')
                    print(df_cleaned)
                st.rerun()


        if st.button("准备模型应用"):
            vote()

st.markdown('---')
st.markdown("##### 可视化结果")
# if btn33:
#     chart_data = pd.DataFrame(np.cumsum(np.random.randint(0, 2, size=(365, 1))), columns=["病株率(%)"])
#     st.line_chart(chart_data)
