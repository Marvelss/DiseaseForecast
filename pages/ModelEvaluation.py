import time

import streamlit as st
import pandas as pd
import numpy as np
from pygwalker.api.streamlit import StreamlitRenderer
from st_pages import add_page_title
from streamlit import switch_page
from streamlit_tree_select import tree_select
import extra_streamlit_components as stx

# add_page_title()
# st.header('模型评估')
# st.markdown('---')
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
mainIndex, tempIndex = st.columns([0.9, 0.2])
with mainIndex:
    val = stx.stepper_bar(steps=["数据集", "数据预处理", "特征计算", "特征优选", "模型构建"])
    st.info(f"Phase #{val}")
    if val == 1:
        switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\DataPreparation.py")
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
        st.markdown("##### 数据与特征")
        st.markdown("###### 原始数据")
        temp = tree_select(nodes)
        st.markdown('---')
        st.markdown("###### 预处理数据")
        temp1 = tree_select(nodes1)
        st.markdown('---')
        st.markdown("###### 特征")
        temp2 = tree_select(nodes2)
    with modelECM:
        # tab1, tab2 = st.tabs(["处理", " "])
        st.markdown("##### 模型评估展示")
        # with tab1:
        # colOption1, colOption2 = st.columns(2)
        # with colOption1:
        agree = st.checkbox('展示模型精度')
        # with colOption2:
        agree2 = st.checkbox('比较模型精度')
        # with colOption3:
        #     pass
        # with tab2:
        #     agree6 = st.checkbox('OA')
        #     agree7 = st.checkbox('Kappa')
        st.markdown('---')
        st.markdown("##### 参数设置")
        if agree:
            st.data_editor(['a', 'b'])
        # col1333, col2333 = st.columns([5, 1])
        # with col2333:
        #     st.button('运行')

    with modelECR:
        st.markdown('##### 结果')
        tabb1, tabb2 = st.tabs(['评价指标', '可视化'])
        with tabb1:
            st.metric("OA", "0.36", "+8%")
            # col2, col3 = st.columns(2)
            # oa = col2.metric("OA", "0.36", "+8%")
            # pa = col3.metric("Kappa", "0.5", "-8%")

        with tabb2:
            chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
            st.line_chart(chart_data)
        # with tabb3:
with tempIndex:
    st.markdown('##### 历史记录及数据下载')
    df = pd.DataFrame(
        {
            "名称": ["温度", "降雨日数", "降水"],
            "大小": ["1*3", "1*6", "1*5"],
            '处理方法': ['t检验', 'Person相关性分析', 'Person相关性分析'],
            "添加特征": [False, False, False],
        }
    )
    edited_df = st.data_editor(df)
    st.button("下载模型训练结果")
    st.button("下载模型结构和参数")
    st.button("下载模型输入参数格式")
# Add a title

# st.title("Use Pygwalker In Streamlit")
#
#
# # Get an instance of pygwalker's renderer. You should cache this instance to effectively prevent the growth of in-process memory.
# @st.cache_resource
# def get_pyg_renderer() -> "StreamlitRenderer":
#     df = pd.read_csv("https://kanaries-app.s3.ap-northeast-1.amazonaws.com/public-datasets/bike_sharing_dc.csv")
#     # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
#     return StreamlitRenderer(df, spec="./gw_config.json", debug=False)
#
#
# renderer = get_pyg_renderer()
#
# # Render your data exploration interface. Developers can use it to build charts by drag and drop.
# renderer.render_explore()
