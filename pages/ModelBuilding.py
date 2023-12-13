import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title
from streamlit_tree_select import tree_select

# add_page_title()
st.header('模型构建')
nodes = [
    {"label": "气象数据", "value": "folder_a"},
    {
        "label": "植保数据",
        "value": "folder_b",
        "children": [
            {"label": "feature1", "value": "sub_a"},
            {"label": "feature2", "value": "sub_b"},
            {"label": "feature3", "value": "sub_c"},
        ],
    },
    {
        "label": "农学数据",
        "value": "folder_c",
        "children": [
            {"label": "晚稻移栽期", "value": "sub_d"},
            {
                "label": "预测峰值",
                "value": "sub_e",
                "children": [
                    {"label": "测报站点", "value": "sub_sub_a"},
                    {"label": "生化指标", "value": "sub_sub_b"},
                ],
            },
            {"label": "生化指标", "value": "sub_f"},
        ],
    },
]

modelACV, modelACM, modelACR = st.columns([0.3, 0.7, 0.7])
with modelACV:
    st.markdown("##### 变量")
    tree_select(nodes)
with modelACM:
    tab1, tab2, tab3 = st.tabs(["建模方法", "评价指标", "验证与训练数据集划分"])
    with tab1:
        colOption1, colOption2, colOption3 = st.columns(3)
        with colOption1:
            agree = st.checkbox('SVM')
            agree1 = st.checkbox('RF')
        with colOption2:
            agree2 = st.checkbox('KNN')
            agree3 = st.checkbox('Logistic回归')
        with colOption3:
            agree4 = st.checkbox('贝叶斯统计')
            agree5 = st.checkbox('模糊综合评价')
    with tab2:
        agree6 = st.checkbox('OA')
        agree7 = st.checkbox('Kappa')
    with tab3:
        option = st.selectbox(
            label="划分比例",
            options=("8:2", "7:3", "6:4")
        )

    st.markdown('---')
    st.markdown("##### 参数设置")
    if agree:
        st.data_editor(['a', 'b'])
    st.button('开始模型训练')
with modelACR:
    tabb1, tabb2 = st.tabs(['可视化', '数据'])
with tabb1:
    st.markdown('展示字段整体数据情况')
with tabb2:
    st.markdown('数据表格')
