import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title

# add_page_title()
st.header('建模方法')

with st.expander("机器学习"):
    agree = st.checkbox('SVM')
    agree1 = st.checkbox('RF')
    agree2 = st.checkbox('KNN')

with st.expander("统计类"):
    agree3 = st.checkbox('Logistic回归')
    agree4 = st.checkbox('贝叶斯统计')
    agree5 = st.checkbox('模糊综合评价')
with st.expander("评价指标"):
    agree6 = st.checkbox('OA')
    agree7 = st.checkbox('Kappa')
    # agree8 = st.checkbox('RMSE')

option = st.selectbox(
    "验证与训练数据集划分",
    ("8:2", "7:3", "6:4")
)
