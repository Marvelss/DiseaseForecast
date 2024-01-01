# page2.py
import numpy as np
import pandas as pd
import streamlit as st

from pages_utils import multiselect_all


# st.sidebar.info("注意:按照数据集模板内容填写")


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# st.header('数据集')
# st.markdown('---')
dataSCM, dataSCR = st.columns([0.5, 0.7])
with dataSCM:
    st.markdown("##### 上传数据集")
    tab1, tab2, tab3 = st.tabs(["气象数据", "植保数据", "农学数据"])
    uploaded_files = st.file_uploader("上传数据集", accept_multiple_files=True, label_visibility='collapsed')
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)
        st.write(bytes_data)

    st.markdown("###### 模板下载")
    col1, col2, col3 = st.columns(3)
    with col1:
        option14 = st.checkbox('模板1')
    with col2:
        option15 = st.checkbox('模板2')
    with col3:
        option16 = st.checkbox('模板3')
with dataSCR:
    st.markdown("##### 模板预览")
    st.markdown('---')
    # tab3, tab4 = st.tabs(["", "其他"])
    # with tab3:
    csv = convert_df(pd.read_csv('resource/房价数据.csv'))
    temperature = np.random.randint(low=0, high=40, size=1000)
    df = pd.read_excel('resource/农学数据.xlsx', header=1)
    st.data_editor(df)
    st.button('下载')
    # with tab4:
    #     st.markdown('其他')
