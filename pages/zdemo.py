import time

import streamlit as st

# 用户通过训练不同的模型进行精度比较,选择精度较高的数据

col1, col2, col3 = st.columns(3)
col1.metric("Temperature", "70 °F", "1.2 °F")
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")
import streamlit as st

st.info('This is a purely informational message', icon="ℹ️")