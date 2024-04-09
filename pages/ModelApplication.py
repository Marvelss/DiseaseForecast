import datetime
import os.path

import scipy
import streamlit as st
import numpy as np
import pandas as pd
import matlab.engine
from streamlit_pills import pills

import pages_utils

st.set_page_config(
    layout="wide"
)
# =======================可视化结果=======================
print('---')
st.markdown("##### 加载模型和特征")
# col2, col3 = st.columns(2)
# with col2:
uploaded_model = st.file_uploader("加载模型")
uploaded_parameter = st.file_uploader("输入特征")
interval_col34, interval_col33 = st.columns([5, 1])
btn33 = interval_col33.button('运行')
st.markdown("##### 可视化结果")
if btn33:
    chart_data = pd.DataFrame(np.cumsum(np.random.randint(0, 2, size=(365, 1))), columns=["病株率(%)"])
    st.line_chart(chart_data)
