import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title
from streamlit_tree_select import tree_select

# add_page_title()
st.header('建模方法')
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

st.markdown("##### 数据集关联")
col1, col2 = st.columns(2)
with col1:
    tree_select(nodes)
with col2:
    tab1, tab5 = st.tabs(["可视化", "数据"])

    with tab1:
        st.subheader('展示数据集整体情况的图表')
        # st.dataframe(df.style.highlight_null(null_color='yellow'))
        pass
    with tab5:
        df = pd.read_excel('resource/气象数据.xlsx')
        st.data_editor(df)
st.markdown('---')
st.markdown("##### 验证与训练数据集划分")
option = st.selectbox(
    label="验证与训练数据集划分", label_visibility="collapsed",
    options=("8:2", "7:3", "6:4")
)
st.markdown('---')
st.markdown("##### 建模方法")
tab11, tab22 = st.tabs(["机器学习", "统计类"])
with tab11:
    agree = st.checkbox('SVM')
    agree1 = st.checkbox('RF')
    agree2 = st.checkbox('KNN')

with tab22:
    agree3 = st.checkbox('Logistic回归')
    agree4 = st.checkbox('贝叶斯统计')
    agree5 = st.checkbox('模糊综合评价')
st.markdown('---')
st.markdown("##### 评价指标")
col11, coll22 = st.columns(2)
with col11:
    agree6 = st.checkbox('OA')
with coll22:
    agree7 = st.checkbox('Kappa')
# agree8 = st.checkbox('RMSE')
