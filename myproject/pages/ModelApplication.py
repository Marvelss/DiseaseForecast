import os.path

import joblib
import streamlit as st
import pandas as pd
from st_pages import hide_pages
from lib.share import RESOURCE_MODELRESULT_PATH
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

st.markdown('')
st.markdown('')
st.markdown('')
st.markdown('')


# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)

colTemp1, colTemp2, colTemp3 = st.columns([0.1, 0.8, 0.1])
with colTemp1:
    pass
with colTemp3:
    pass
with colTemp2:
    col2, col3 = st.columns(2)
    with col2:
        st.markdown("##### 加载模型")
        st.selectbox('加载模型', options=['SVM'], label_visibility='collapsed')
        modelDF = pages_utils.TempDataSetField[4]
        # models = modelDF["特征"].tolist()
        models = [1]

        for tempModel in models:
            # model = joblib.load(
            #     os.path.join(RESOURCE_MODELRESULT_PATH, 'structure',
            #                  f'{tempModel}_structure.pkl'))
            model = joblib.load(
                os.path.join(RESOURCE_MODELRESULT_PATH, 'structure',
                             'FLDA_structure.pkl'))

        # 获取特征字段
        feature_names = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else None
        st.info(f"模型输入特征:{' '.join(feature_names)}")

    with col3:
        st.markdown("##### 输入特征")
        uploaded_dataSet = st.file_uploader(
            "输入原始字段",
            accept_multiple_files=False,
            label_visibility='collapsed')

    if uploaded_dataSet:
        bytes_data = uploaded_dataSet.read()
        predictDF = pd.read_excel(bytes_data)
        predictions = model.predict(predictDF)
        predictDF['预测结果'] = predictions
        st.table(predictDF)
