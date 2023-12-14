import streamlit as st
import numpy as np
import pandas as pd
from streamlit_tree_select import tree_select

from pages_utils import multiselect_all

st.header('特征优选')
st.markdown('---')
# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM, dataPCR = st.columns([0.3, 0.7, 0.7])
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
with dataPCV:
    st.markdown("##### 变量")
    return_select = tree_select(nodes, disabled=True)
with dataPCM:
    tab1, tab2 = st.tabs(["单因子敏感性分析", "多因子组合优化"])
    with tab1:
        genre = st.checkbox("Person相关性分析")
        genre1 = st.checkbox("t检验")

    # btn1 = st.button('预览')

    with tab2:
        genre3 = st.checkbox("Relief-F互相关分析")
    st.markdown('---')
    st.markdown("##### 参数设置")
    if genre1:
        st.markdown('提取条件')
        genre2 = st.radio(
            label='',
            horizontal=True,
            label_visibility="collapsed",
            options=['p-value<0.001', 'p-value<0.005', 'p-value<0.01']
        )
    if genre3:
        # st.markdown('提取条件')
        option = st.selectbox(
            '提取条件',
            ('按百分比选取', '按权重值计算'))
        if option == '按百分比选取':
            number1 = st.number_input("TOP(%)", value=5, min_value=5, step=5)
        if option == '按权重值计算':
            number2 = st.number_input("权重阈值", value=10, min_value=10)
    st.button('运行')

with dataPCR:
    tabb1, tabb2 = st.tabs(['结果', '可视化'])
    with tabb1:
        st.markdown('运行结果')
        st.json(({
            '气象数据': 'List (2个元素)',
            '气温 List (2个特征)': [
                '20.5',
                '30.5',
            ]}))
    with tabb2:
        st.subheader('展示数据处理前与处理后的图表')
        t1, t2 = st.columns(2)
        with t1:
            chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["p-value", "月份", "图例"])
            st.vega_lite_chart(
                chart_data,
                {
                    "mark": {"type": "circle", "tooltip": True},
                    "encoding": {
                        "x": {"field": "月份", "type": "quantitative"},
                        "y": {"field": "p-value", "type": "quantitative"},
                        "size": {"field": "图例", "type": "quantitative"},
                        "color": {"field": "图例", "type": "quantitative"},
                    },
                },
            )
            # st.image('resource/image/0.png')
        with t2:
            pass
