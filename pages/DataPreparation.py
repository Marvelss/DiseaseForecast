import streamlit as st
import numpy as np
import pandas as pd
from streamlit_tree_select import tree_select

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

st.header('数据预处理')
st.markdown('---')
# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM, dataPCR = st.columns([0.3, 0.7, 0.7])

with dataPCV:
    st.markdown("##### 变量")
    tree_select(nodes)
with dataPCM:
    tab1, tab2, tab3, tab4 = st.tabs(["气象数据", "植保数据", "农学数据", "遥感数据"])
    with tab1:
        col1, col2 = st.columns(2)
        # st.dataframe(df.style.highlight_null(null_color='yellow'))
        with col1:
            agree = st.checkbox('剔除数据')
            agree5 = st.checkbox('剔除数据5')
        with col2:
            agree10 = st.checkbox("缺失值插补")
    with tab2:
        agree1 = st.checkbox('标记不连续数据')
    with tab3:
        agree4 = st.checkbox('剔除数据4')
    with tab4:
        agree2 = st.checkbox('剔除数据2')
        agree3 = st.checkbox('剔除数据3')
    st.markdown('---')
    st.subheader('参数设置')
    if agree10:
        option = st.selectbox(
            '插补方法',
            options=('线性插值', '自定义'))
        if option == '自定义':
            st.text_input('温度')
            st.text_input('降水')
    st.button('运行')

with dataPCR:
    tabb1, tabb2 = st.tabs(['结果', '可视化'])
    with tabb1:
        st.markdown('运行结果')
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
