import streamlit as st
import pandas as pd
import numpy as np
from st_pages import add_page_title
from streamlit_tree_select import tree_select

# add_page_title()
st.header('模型评估')
modelEC1, modelEC2 = st.columns([0.8, 0.2])
with modelEC1:
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
with modelEC2:
    tab111, tab222 = st.tabs(["结果保存", " "])
    with tab111:
        st.button("保存模型训练结果")
        st.button("保存模型结构和参数")
        st.button("保存模型输入参数")
