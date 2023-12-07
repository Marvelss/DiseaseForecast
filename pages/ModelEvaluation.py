import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title
from streamlit_tree_select import tree_select


# add_page_title()
st.header('模型评估')
tab1, tab2, tab3 = st.tabs(["SVM", "FLDA", "RF"])
with tab1:
    col2, col3 = st.columns(2)
    # with :
    oa = col2.metric("OA", "0.36", "+8%")
    pa = col3.metric("Kappa", "0.5", "-8%")
    # with col3:
    #     col1.metric("Temperature", "70 °F", "1.2 °F")
    #     col2.metric("Wind", "9 mph", "-8%")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

    st.line_chart(chart_data)

st.sidebar.download_button(
    label="下载模型训练结果",
    data='a',
    file_name='large_df.csv',
    mime='text/csv',
)
st.sidebar.download_button(
    label="下载模型结构和参数",
    data='None',
    file_name='large_df.csv',
    mime='text/csv',
)
st.sidebar.download_button(
    label="保存模型输入参数",
    data='None',
    file_name='large_df.csv',
    mime='text/csv',
)
