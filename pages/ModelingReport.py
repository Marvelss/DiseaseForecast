"""
@Author : SakuraFox
@Time: 2024-08-10 9:06
@File : ModelingReport.py
@Description : 建模报告
"""
import os.path

import joblib
import streamlit as st
import seaborn as sns

import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from st_pages import hide_pages
from streamlit_pills import pills

import pages_utils
from modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
from modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod

st.set_page_config(
    layout="wide"
)
if st.session_state.isPlanarInterface:
    hide_pages(
        [
            "测试界面",
            "原始数据",
            "数据预处理",
            "特征计算",
            "特征优选",
        ]
    )
else:
    hide_pages(
        [
            "测试界面",
            "原始数据-面状",
            "数据预处理-面状",
            "特征计算-面状",
            "特征优选-面状",
            "模型构建-面状",
        ]
    )

st.header('建模报告')
st.markdown('### 预期展示的信息')
st.markdown('#### 1.原始数据:条数,字段,数据类型,影响因素')
st.markdown('---')

st.markdown('#### 2.预处理:预处理图,剔除和插补信息')
st.markdown('---')

st.markdown('#### 3.特征计算:处理图,所有特征')
st.markdown('---')

st.markdown('#### 4.特征优选:优选图,最优特征集')
st.markdown('---')

st.markdown('#### 5.模型构建:'
            '模型,模型参数,评价指标,分配比例,特征信息(个数和条数)')

st.markdown('#### 6.天气情景生成器:'
            '地区,模型,年限长度,场景,异常程度,'
            '模拟气象数据生成图 ,模型预测结果 ,偏差指标结果')

st.markdown('#### 7.模型预测结果:'
            '模型构建中测试集和模拟气象数据的预测结果(地图中展示)')
