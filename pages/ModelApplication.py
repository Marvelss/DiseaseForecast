import time

import streamlit as st
import numpy as np
import pandas as pd
from st_pages import add_page_title

# add_page_title()
st.header('模型应用')
st.markdown('---')
uploaded_model = st.file_uploader("加载模型")

uploaded_parameter = st.file_uploader("加载输入参数")

col2, col3 = st.columns(2)
with col2:
    st.text_input('经度')
    st.text_input('纬度')
with col3:
    st.text_input('温度')
    st.text_input('降水')


# uploaded_files = st.file_uploader("加载数据集", accept_multiple_files=True)
# for uploaded_file in uploaded_files:
#     bytes_data = uploaded_file.read()
#     st.write("filename:", uploaded_file.name)
# st.write(bytes_data)

st.button('运行')
chart_data = pd.DataFrame(np.cumsum(np.random.randint(0, 2, size=(365, 1))), columns=["病株率(%)"])

st.line_chart(chart_data)

