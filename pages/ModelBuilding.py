import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title
from streamlit_tree_select import tree_select

# add_page_title()
st.header('模型构建')
st.markdown('---')
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
        df = pd.DataFrame(
            [
                {"参数名": "a", "参数值": 4},
                {"参数名": "b", "参数值": 4},
                {"参数名": "c", "参数值": 6},
                {"参数名": "d", "参数值": 5},
            ]
        )
        st.data_editor(df)
    st.button('开始模型训练')
with modelACR:
    tabb1, tabb2 = st.tabs(['数据', '可视化'])
with tabb1:
    st.text('类型:double' + '\n' +
            '唯一值:50' + '\n' +
            '有重复值:True' + '\n' +
            '缺少计数:0' + '\n' +
            '最小值:50' + '\n' +
            '最大值:100' + '\n' +
            '均值:60' + '\n' +
            '中位数:50' + '\n' +
            '众数:60' + '\n' +
            '标准差:0.3' + '\n'
            )
with tabb2:
    st.markdown('数据表格')
