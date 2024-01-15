import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title
from streamlit_tree_select import tree_select
import pages_utils

# add_page_title()
# st.header('模型构建')
# st.markdown('---')
# Pages logic
if 'page' not in st.session_state: st.session_state.page = 0


#
#
def nextPage(): st.session_state.page += 1


#
#
def firstPage(): st.session_state.page = 0


# nodes = [
#     {"label": "气象数据", "value": "folder_a"},
#     {
#         "label": "植保数据",
#         "value": "folder_b",
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

modelACV, modelACM = st.columns([0.5, 0.7])
with modelACV:
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
    st.markdown("###### 模型")
    edited_df1 = st.data_editor(pages_utils.ModelSet)
with modelACM:
    ph = st.empty()

    # Page 0
    if st.session_state.page == 0:
        with ph.container():
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
            st.markdown('---')
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
            interval_col1, interval_col2 = st.columns([4, 1])
            interval_col2.button("下一步", on_click=nextPage)
            # st.button()

    # Page 1
    elif st.session_state.page == 1:
        with ph.container():
            st.markdown("###### 评价指标")
            agree6 = st.checkbox('OA')
            agree7 = st.checkbox('Kappa')
            interval_col1, interval_col2 = st.columns([4, 1])
            interval_col2.button("下一步", on_click=nextPage)

    # Page 2
    elif st.session_state.page == 2:
        with ph.container():
            st.markdown("###### 验证与训练数据集划分")
            option = st.selectbox(
                label="划分比例",
                options=("8:2", "7:3", "6:4")
            )
            interval_col1, interval_col2 = st.columns([5, 2])
            interval_col1.button("返回", on_click=firstPage)
            interval_col2.button("开始模型训练")
    st.markdown('---')

    col2, col3 = st.columns(2)
    oa = col2.metric("OA", "0.36")
    pa = col3.metric("Kappa", "0.5")
# with modelACR:
#     tabb1, tabb2, tabb3 = st.tabs(['精度', '可视化', '模型训练记录及结果下载'])
# with tabb1:
#     col2, col3 = st.columns(2)
#     oa = col2.metric("OA", "0.36", "+8%")
#     pa = col3.metric("Kappa", "0.5", "-8%")
# with tabb2:
#     chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
#     st.line_chart(chart_data)
# with tabb3:
#     st.markdown('###### 模型训练记录')
#     df = pd.DataFrame(
#         {
#             "名称": ["SVM", "KNN", "RF"],
#             '参数数量': ['5', '6', '5'],
#             "时间": ['22:10:20', '20:10:20', '21:10:20'],
#         }
#     )
#     edited_df = st.data_editor(df)
#     st.markdown('---')
#     st.markdown('###### 结果下载')
#     pages_utils.multiselect_all(st, ['SVM', 'KNN', 'RF'], '选择模型', "collapsed")
#     st.markdown('下载内容')
#     option_col1, option_col2, option_col3 = st.columns(3)
#     with option_col1:
#         st.checkbox('模型结构')
#     with option_col2:
#         st.checkbox('模型训练结果')
#     with option_col3:
#         st.checkbox('模型参数')
#     interval_col13, interval_col12 = st.columns([5, 1])
#     interval_col12.button('下载')
