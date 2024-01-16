import streamlit as st
import numpy as np
import pandas as pd
from streamlit_tree_select import tree_select

import pages_utils

# nodes = [
#     {"label": "气象数据", "value": "气象数据"},
#     {
#         "label": "植保数据",
#         "value": "植保数据",
#         "children": [
#             {"label": "feature1", "value": "sub_a"},
#             {"label": "feature2", "value": "sub_b"},
#             {"label": "feature3", "value": "sub_c"},
#         ],
#     },
#     {
#         "label": "农学数据",
#         "value": "folder_c",
#         "children": [
#             {"label": "晚稻移栽期", "value": "sub_d"},
#             {
#                 "label": "预测峰值",
#                 "value": "sub_e",
#                 "children": [
#                     {"label": "测报站点", "value": "sub_sub_a"},
#                     {"label": "生化指标", "value": "sub_sub_b"},
#                 ],
#             },
#             {"label": "生化指标", "value": "sub_f"},
#         ],
#     },
# ]
# nodes1 = [
#     {"label": "气象数据", "value": "气象数据"},
#     {
#         "label": "植保数据",
#         "value": "植保数据",
#         "children": [
#             {"label": "feature1", "value": "sub_a"},
#             {"label": "feature2", "value": "sub_b"},
#             {"label": "feature3", "value": "sub_c"},
#         ],
#     },
#     {
#         "label": "农学数据",
#         "value": "folder_c",
#         "children": [
#             {"label": "晚稻移栽期", "value": "sub_d"},
#             {
#                 "label": "预测峰值",
#                 "value": "sub_e",
#                 "children": [
#                     {"label": "测报站点", "value": "sub_sub4"},
#                     {"label": "生化指标", "value": "sub_s5"},
#                 ],
#             },
#             {"label": "生化指标", "value": "sub_f"},
#         ],
#     },
# ]
# nodes2 = [
#     {"label": "气象数据", "value": "气象数据"},
#     {
#         "label": "植保数据",
#         "value": "植保数据",
#         "children": [
#             {"label": "feature1", "value": "sub_4"},
#             {"label": "feature2", "value": "sub_3"},
#             {"label": "feature3", "value": "sub_2"},
#         ],
#     },
#     {
#         "label": "农学数据",
#         "value": "folder_c",
#         "children": [
#             {"label": "晚稻移栽期", "value": "sub_d"},
#             {
#                 "label": "预测峰值",
#                 "value": "sub_e",
#                 "children": [
#                     {"label": "测报站点", "value": "sub_sub_a"},
#                     {"label": "生化指标", "value": "sub_sub_b"},
#                 ],
#             },
#             {"label": "生化指标", "value": "sub_f"},
#         ],
#     },
# ]

# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    st.markdown("###### 特征")
    edited_df2 = st.data_editor(
        pages_utils.FeatureDataSet,
        column_config={
            "选择字段": st.column_config.CheckboxColumn(
                help="选择用于数据处理的字段",
                default=False,
            )
        },
        disabled=["数据集", "字段", "大小", "处理方法", "时间"],
        hide_index=True,
        num_rows="dynamic", )
    st.markdown('---')
    st.markdown("###### 预处理数据")
    edited_df223 = st.data_editor(
        pages_utils.PreprocessedDataSet,
        column_config={
            "选择字段": st.column_config.CheckboxColumn(
                help="选择用于数据处理的字段",
                default=False,
            )
        },
        disabled=["数据集", "字段", "大小", "处理方法", "时间"],
        hide_index=True,
        num_rows="dynamic", )
    st.markdown('---')
    st.markdown("###### 原始数据")
    edited_df = st.data_editor(pages_utils.RawDataSet)


with dataPCM:
    tab1, tab2 = st.tabs(["单因子敏感性分析", "多因子组合优化"])
    with tab1:
        genre = st.checkbox("Person相关性分析")
        genre1 = st.checkbox("t检验")
    with tab2:
        genre3 = st.checkbox("Relief-F互相关分析")
    st.markdown('---')
    # st.markdown("##### 方法参数设置")
    if genre1:
        st.markdown('提取条件')
        genre2 = st.radio(
            label='',
            horizontal=True,
            label_visibility="collapsed",
            options=['p-value<0.001', 'p-value<0.005', 'p-value<0.01']
        )
        st.markdown('---')
    # st.markdown('---')
    if genre3:
        # st.markdown('提取条件')
        option = st.selectbox(
            '提取条件',
            ('按百分比选取', '按权重值计算'))
        if option == '按百分比选取':
            number1 = st.number_input("TOP(%)", value=5, min_value=5, step=5)
        if option == '按权重值计算':
            number2 = st.number_input("权重阈值", value=10, min_value=10)
        # st.markdown('---')

    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('保存')
    if btn:
        # update dataframe state
        # st.markdown(type(st.session_state.df))
        new_data = {"数据集": "气象数据", "字段": "降水",
                    "特征优选方法": "t检验", "时间": '22:20:20'}
        st.session_state.df1.loc[len(st.session_state.df1)] = new_data
        st.rerun()
    st.markdown('---')
    data = pd.DataFrame(columns=["数据集", "字段", "特征优选方法", '时间'])

    if 'df1' not in st.session_state:
        st.session_state.df1 = data
    placeholder = st.empty()

    with placeholder.container():
        st.markdown('##### 任务清单')
        edited_df28 = st.data_editor(
            st.session_state.df1, height=190, width=800,
            disabled=["数据集", "字段", "时间"],
            hide_index=False, )
        interval_col34, interval_col33 = st.columns([5, 1])
        btn2 = interval_col33.button('运行')
    if btn2:
        # with placeholder.container():
        placeholder.empty()
        st.markdown('##### 可视化')
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
        # btn2 = st.button('下载')


# with dataPCR:
#     tabb2, tabb3 = st.tabs(['可视化', ' '])
    # with tabb1:
    #     st.markdown('##### 数据摘要')
    #     st.markdown('特征名称:温度')
    #     st.markdown('个数:2')
    #     st.markdown('类型:整数')
    #     st.markdown('数值:[5,6]')
    # with tabb2:
    #     st.subheader('展示数据处理前与处理后的图表')
    #     t1, t2 = st.columns(2)
    #     with t1:
    #         chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["p-value", "月份", "图例"])
    #         st.vega_lite_chart(
    #             chart_data,
    #             {
    #                 "mark": {"type": "circle", "tooltip": True},
    #                 "encoding": {
    #                     "x": {"field": "月份", "type": "quantitative"},
    #                     "y": {"field": "p-value", "type": "quantitative"},
    #                     "size": {"field": "图例", "type": "quantitative"},
    #                     "color": {"field": "图例", "type": "quantitative"},
    #                 },
    #             },
    #         )
            # st.image('resource/image/0.png')
        # with t2:
        #     pass
        # with tabb3:
        #     pass
            # st.markdown('###### 历史记录')
            # df = pd.DataFrame(
            #     {
            #         "数据集": ["气象数据", "植保数据", "农学数据"],
            #         "特征": ["降雨日数", "基于活动积温的生育期", "预测峰值"],
            #         "大小": ["1*3", "1*6", "1*5"],
            #         '处理方法': ['t检验', 'Person相关性分析', 'Person相关性分析'],
            #         "时间": ['22:10:20', '20:10:20', '21:10:20'],
            #     }
            # )
            # edited_df = st.data_editor(df)
            # st.markdown('---')
            # st.markdown('###### 数据下载')
            # option = st.selectbox(
            #     '历史记录编号',
            #     (1, 2, 3))
            # pages_utils.multiselect_all(st, ['气温', '降雨日数', '生育期'], '特征',"collapsed")
            # interval_col13, interval_col12 = st.columns([5, 1])
            # interval_col12.button('下载')
