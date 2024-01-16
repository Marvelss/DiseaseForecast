import streamlit as st
import numpy as np
import pandas as pd
from streamlit_tree_select import tree_select
import pages_utils
from streamlit_autorefresh import st_autorefresh

# count = st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")

# The function returns a counter for number of refreshes. This allows the
# ability to make special requests at different intervals based on the count
# if count == 0:
#     st.write("Count is zero")
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
#
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
#
# st.session_state.page = 0


# def addData(pha, rootNode):
#     rootNode.append(
#         {
#             "label": "农学数据",
#             "value": "folder_c",
#             "children": [
#                 {"label": "晚稻移栽期", "value": "sub_d"},
#                 {
#                     "label": "预测峰值",
#                     "value": "sub_e",
#                 }]})
#     if st.session_state.page != -1:
#         st.session_state.page += 1
#         # st.write(st.session_state.page)
#         # if st.session_state.page == 1:
#         st.session_state.page += 1
#         # st.write(st.session_state.page)
#         with pha.container():
#             st.markdown("sub_a" + str(st.session_state.page))
#             # temp1 = tree_select(rootNode)


# st.header('数据预处理')
# st.markdown('---')
# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    st.markdown("###### 原始数据")
    # edited_df = st.data_editor(df)
    edited_df22 = st.data_editor(
        pages_utils.RawDataSet,
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
    # for index, row in edited_df223.iterrows():
    #     st.markdown(row.get('下载数据集'))
    #     if row.get('下载数据集'):
    #         st.markdown('下载')

    st.markdown('---')
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

with dataPCM:
    # 当选择一类数据集后,其他数据集禁选
    st.markdown("##### 预处理方法")

    # dataFlag = temp.get('checked')
    # with tab1:
    col1, col2 = st.columns(2)
    # st.dataframe(df.style.highlight_null(null_color='yellow'))

    with col1:
        agree = st.checkbox('剔除异常值')
        # agree5 = st.checkbox('剔除数据5')
    with col2:
        agree10 = st.checkbox("缺失值插补")
    # st.markdown(dataFlag)
    # if '植保数据' in dataFlag:
    #     with col1:
    #         agree111 = st.checkbox('剔除数据1')
    #         # agree5 = st.checkbox('剔除数据5')
    #     with col2:
    #         agree101 = st.checkbox("标记不连续数据")
    # with tab2:
    # agree1 = st.checkbox('')
    # # with tab3:
    # agree4 = st.checkbox('剔除数据4')
    # # with tab4:
    # agree2 = st.checkbox('剔除数据2')
    # agree3 = st.checkbox('剔除数据3')
    st.markdown('---')
    # st.markdown("##### 方法参数设置")
    if agree10:
        option = st.selectbox(
            '插补方法',
            options=('线性插值', '自定义'))
        if option == '自定义':
            st.text_input('输入数值')
        # st.markdown('---')
    if agree:
        number2 = st.text_input("剔除大于", value=0.1)
        number3 = st.text_input("剔除小于", value=0.1)
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('保存')
    if btn:
        # update dataframe state
        # st.markdown(type(st.session_state.df))
        new_data = {"数据集": "气象数据", "字段": "温度",
                    "预处理方法": "缺失值插补", "时间": '22:20:20'}
        st.session_state.df.loc[len(st.session_state.df)] = new_data
        st.rerun()
    st.markdown('---')

    data = pd.DataFrame(columns=["数据集", "字段", "预处理方法", '时间'])
    # with every interaction, the script runs from top to bottom
    # resulting in the empty dataframe
    if 'df' not in st.session_state:
        st.session_state.df = data
    placeholder = st.empty()
    with placeholder.container():
        st.markdown('##### 任务清单')
        edited_df28 = st.data_editor(
            st.session_state.df, height=190, width=800,
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
# with dataPCR:
#     tabb2, tabb3 = st.tabs(['可视化', ' '])
# with tabb0:
#     st.data_editor(pd.DataFrame(
#         data={
#             "温度": [1, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4],
#         }
#     ), height=210)
#
# with tabb1:
#     st.markdown('##### 数据摘要')
#     col111, col222 = st.columns(2)
#     with col111:
#         st.markdown('###### 处理前')
#         st.markdown('特征名称:温度')
#         st.markdown('个数:2')
#         st.markdown('类型:整数')
#         st.markdown('数值:[5,6]')
#
#     with col222:
#         st.markdown('###### 处理后')
#         st.markdown('特征名称:温度')
#         st.markdown('个数:5')
#         st.markdown('数据类型:整数')
#         st.markdown('数值:[5,2,3,3,2]')
# with tabb2:
#     st.subheader('展示数据处理前与处理后的图表')
#     t1, t2 = st.columns(2)
#     with t1:
#         st.image('resource/image/0.png')
#     with t2:
#         st.image('resource/image/1.png')
# with tabb3:
#     pass
# st.markdown('###### 历史记录')
# df = pd.DataFrame(
#     {
#         "数据集": ["气象数据", "植保数据", "农学数据"],
#         "字段": ["温度", "生育期", "预测峰值"],
#         "大小": ["1*3", "1*6", "1*5"],
#         '处理方法': ['缺失值插补', '缺失值插补', '缺失值插补'],
#         "时间": ['22:10:20', '20:10:20', '21:10:20'],
#     }
# )
# edited_df = st.data_editor(df)
# st.markdown('---')
# st.markdown('###### 数据下载')
# option = st.selectbox(
#     '历史记录编号',
#     (1, 2, 3))
# pages_utils.multiselect_all(st, ['气温', '降雨日数', '生育期'], '字段', "collapsed")
# interval_col13, interval_col12 = st.columns([5, 1])
# interval_col12.button('下载')
# with tab2:
#     st.subheader('植保数据')
# df = pd.read_excel('resource/植保数据 - 副本.xlsx')
# agree1 = st.checkbox('标记不连续数据')
# agree2 = st.checkbox('标记病株率负值数据', on_change=show)
# t = st.dataframe(df.style.highlight_null(color='yellow'))
# if agree2:
#     t.empty()
#     # 替换符合条件的单元格内容
#     # df = df.replace('\\', np.nan)
#     styled = df.style.applymap(highlight_negative, subset=['预测病株率'])
#     if 'df' not in st.session_state:
#         st.session_state.df = df
#         st.session_state.styled_df = styled
#     # ed = st.data_editor(st.session_state.styled_df)
#
#     st.dataframe(styled)
# st.dataframe(df)

# df1 = pd.read_excel('resource/植保数据 - 副本.xlsx')
# # 替换符合条件的单元格内容
# # df = df.replace('\\', np.nan)
# styled = df1.style.applymap(highlight_negative, subset=pd.IndexSlice[:, ['预测病株率']])
# edited_df = st.data_editor(styled)
# edited_df=st.data_editor(styled,use_container_width=True,hide_index=True,disabled=["Host IP","Component","Validation_Command","Status"])
