import streamlit as st
import numpy as np
import pandas as pd
from streamlit_tree_select import tree_select

nodes = [
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
                    {"label": "测报站点", "value": "sub_sub_a"},
                    {"label": "生化指标", "value": "sub_sub_b"},
                ],
            },
            {"label": "生化指标", "value": "sub_f"},
        ],
    },
]

st.header('数据预处理')
st.markdown('---')
# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM, dataPCR = st.columns([0.3, 0.7, 0.7])

with dataPCV:
    st.markdown("##### 变量")
    temp = tree_select(nodes)
with dataPCM:
    # 当选择一类数据集后,其他数据集禁选
    st.markdown("##### 预处理方法")

    dataFlag = temp.get('checked')
    # with tab1:
    col1, col2 = st.columns(2)
    # st.dataframe(df.style.highlight_null(null_color='yellow'))

    with col1:
        agree = st.checkbox('剔除数据')
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
    st.markdown("##### 方法参数设置")

    if agree10:
        option33 = st.selectbox(
            '选择表变量',
            options=('feature1', 'feature2'))

        option = st.selectbox(
            '插补方法',
            options=('线性插值', '自定义'))
        if option == '自定义':
            st.text_input('输入数值')
    st.button('运行')

with dataPCR:
    tabb0, tabb1, tabb2 = st.tabs(['数据', '结果', '可视化'])
    with tabb0:
        st.data_editor(pd.DataFrame(
            data={
                "温度": [1, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4],
            }
        ), height=210)

    with tabb1:
        st.markdown('##### 数据摘要')
        col111, col222 = st.columns(2)
        with col111:
            st.markdown('###### 处理前')
            st.markdown('特征名称:温度')
            st.markdown('个数:2')
            st.markdown('类型:整数')
            st.markdown('数值:[5,6]')

        with col222:
            st.markdown('###### 处理后')
            st.markdown('特征名称:温度')
            st.markdown('个数:5')
            st.markdown('数据类型:整数')
            st.markdown('数值:[5,2,3,3,2]')
        st.button('下载结果数据')
        st.button('下载方法参数值')
        st.button('保存修改')
    with tabb2:
        st.subheader('展示数据处理前与处理后的图表')
        t1, t2 = st.columns(2)
        with t1:
            st.image('resource/image/0.png')
        with t2:
            st.image('resource/image/1.png')

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
