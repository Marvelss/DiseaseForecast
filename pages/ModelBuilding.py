import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title
from streamlit_tree_select import tree_select

# add_page_title()
# st.header('模型构建')
# st.markdown('---')
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
nodes1 = [
    {"label": "气象数据", "value": "气象数据"},
    {
        "label": "植保数据",
        "value": "植保数据",
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
                    {"label": "测报站点", "value": "sub_sub4"},
                    {"label": "生化指标", "value": "sub_s5"},
                ],
            },
            {"label": "生化指标", "value": "sub_f"},
        ],
    },
]
nodes2 = [
    {"label": "气象数据", "value": "气象数据"},
    {
        "label": "植保数据",
        "value": "植保数据",
        "children": [
            {"label": "feature1", "value": "sub_4"},
            {"label": "feature2", "value": "sub_3"},
            {"label": "feature3", "value": "sub_2"},
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
    st.markdown("##### 数据与特征")
    st.markdown("###### 原始数据")
    temp = tree_select(nodes)
    st.markdown('---')
    st.markdown("###### 预处理数据")
    temp1 = tree_select(nodes1)
    st.markdown('---')
    st.markdown("###### 特征")
    temp2 = tree_select(nodes2)
with modelACM:
    st.markdown("###### 建模方法")
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

    if agree:
        df = pd.DataFrame(
            [
                {"参数名": "a", "参数值": 4},
                {"参数名": "b", "参数值": 4},
                {"参数名": "c", "参数值": 6},
                {"参数名": "d", "参数值": 5},
            ]
        )
        st.data_editor(df)
    st.markdown('---')
    st.markdown("###### 评价指标")
    agree6 = st.checkbox('OA')
    agree7 = st.checkbox('Kappa')
    st.markdown('---')
    st.markdown("###### 验证与训练数据集划分")
    option = st.selectbox(
        label="划分比例",
        options=("8:2", "7:3", "6:4")
    )
    # st.markdown("##### 模型参数设置")
    interval_col1, interval_col2 = st.columns([2, 1])
    interval_col2.button('开始模型训练')
with modelACR:
    tabb1, tabb2, tabb3 = st.tabs(['精度', '可视化', '工作区'])
with tabb1:
    col2, col3 = st.columns(2)
    oa = col2.metric("OA", "0.36", "+8%")
    pa = col3.metric("Kappa", "0.5", "-8%")
with tabb2:
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    st.line_chart(chart_data)
with tabb3:
    df = pd.DataFrame(
        {
            "名称": ["SVM", "KNN", "RF"],
            '参数数量': ['5', '6', '5'],
            "下载参数": [True, True, True],
        }
    )
    edited_df = st.data_editor(df)
    st.button('下载')
