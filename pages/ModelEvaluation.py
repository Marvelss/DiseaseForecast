import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title
from streamlit_tree_select import tree_select

# add_page_title()
st.header('模型评估')
st.markdown('---')
nodes = [
    {"label": "机器学习", "value": "folder_a",
     "children": [{"label": "SVM", "value": "folder_b", },
                  {"label": "FLDA", "value": "FLDA", },
                  {"label": "KNN", "value": "KNN", }]
     },
    {"label": "统计类", "value": "folder_a1",
     "children": [{"label": "Logistic回归", "value": "folder_b1", },
                  {"label": "贝叶斯统计", "value": "FLDA1", },
                  {"label": "模糊综合评价", "value": "KNN1", }]
     },
]

modelECV, modelECM, modelECR = st.columns([0.3, 0.7, 0.7])
with modelECV:
    st.markdown("##### 模型")
    tree_select(nodes)
with modelECM:
    # tab1, tab2 = st.tabs(["处理", " "])
    st.markdown("##### 模型评估展示")
    # with tab1:
    colOption1, colOption2, colOption3 = st.columns(3)
    with colOption1:
        agree = st.checkbox('展示模型精度')
    with colOption2:
        agree2 = st.checkbox('比较模型精度')
    with colOption3:
        pass
    # with tab2:
    #     agree6 = st.checkbox('OA')
    #     agree7 = st.checkbox('Kappa')
    st.markdown('---')
    st.markdown("##### 参数设置")
    if agree:
        st.data_editor(['a', 'b'])
    st.button('运行')
with modelECR:
    tabb1, tabb2 = st.tabs(['评价指标', '可视化'])
    with tabb1:
        col2, col3 = st.columns(2)
        oa = col2.metric("OA", "0.36", "+8%")
        pa = col3.metric("Kappa", "0.5", "-8%")
        st.button("下载模型训练结果")
        st.button("下载模型结构和参数")
        st.button("下载模型输入参数格式")
    with tabb2:
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
        st.line_chart(chart_data)
