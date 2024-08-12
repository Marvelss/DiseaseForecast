"""
@Author : SakuraFox
@Time: 2024-08-10 9:06
@File : ModelingReport.py
@Description : 建模报告
"""
import itertools
import os.path

import joblib
import streamlit as st
import seaborn as sns

import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from st_pages import hide_pages
from streamlit_pills import pills

import pages_utils
from modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
from modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod
from App import category
import ui

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

category_colors_cycle = itertools.cycle(
    [
        # ui.color("red-70"),
        ui.color("orange-70"),
        ui.color("light-blue-70"),
        ui.color("blue-green-70"),
        ui.color("blue-70"),
        ui.color("violet-70"),
        ui.color("red-70"),
        ui.color("green-70"),
    ]
)


def category(name, description=None):
    # if current_category_index != 0:
    # st.write("---")
    # st.write("")
    # pass
    # ui.colored_header(name, "rgba(38, 39, 48, 0.6)")
    ui.colored_header(name, next(category_colors_cycle), description)
    # st.header(name)
    st.write("")

    # current_category_index += 1


# st.header('建模报告')
st.markdown('# 建模报告')
category("📊️ 原始数据")

st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 28px;
}
</style>
""",
    unsafe_allow_html=True,
)

colDS1, colDS2 = st.columns(2)
with colDS1:
    st.metric('原始字段', '上级单位、测报站点、年、DayOfYear、温度')
with colDS2:
    st.metric('数据大小', '5*30')
colDS3, colDS4 = st.columns(2)
with colDS3:
    st.metric('数据类型', '气象数据 植保数据')
with colDS4:
    st.metric('影响因素', '气温 降水 湿度')

category("🌌 预处理")
colPre1, colPre2 = st.columns(2)
with colPre1:
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '数据预处理-缺失值插补.png'))
    st.image(img, width=680)
    colPart1, colPart2, colPart3 = st.columns(3)
    colPart1.metric('预处理字段', '降水')
    colPart2.metric('预处理方法', '缺失值插补')
    colPart3.metric('预处理数据条数', '30')
with colPre2:
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '数据预处理-剔除异常值.png'))
    st.image(img, width=800)
    colPart1, colPart2, colPart3 = st.columns(3)
    colPart1.metric('预处理字段', '温度')
    colPart2.metric('预处理方法', '异常值剔除')
    colPart3.metric('预处理数据条数', '50')

category("🌍 特征计算")
# 命名: 界面名称缩写
colFC1, colFC2 = st.columns(2)
with colFC1:
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '特征计算-降水累积量.png'))
    st.image(img, width=760)
    colFCPart1, colFCPart2 = st.columns([0.3, 0.5])
    colFCPart1.metric('输入字段', '降水')
    colFCPart2.metric('特征计算方法', '降水累积量计算')
    colFCPart3, colFCPart4 = st.columns([0.3, 0.5])
    colFCPart3.metric('输出特征', '降水累积量')
    colFCPart4.metric('特征条数', '30')
with colFC2:
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '特征计算-移栽期.png'))
    st.image(img, width=700)
    colFCPart1, colFCPart2 = st.columns([0.3, 0.5])
    colFCPart1.metric('输入字段', '温度')
    colFCPart2.metric('特征计算方法', '基于活动积温的生育期计算')
    colFCPart3, colFCPart4 = st.columns([0.3, 0.5])
    colFCPart3.metric('输出特征', '生育期')
    colFCPart4.metric('特征条数', '30')

category("🌎 特征优选")
colFO1, colFO2 = st.columns(2)
with colFO1:
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '特征优选-Pearson.png'))
    st.image(img, width=700)
    colFCPart1, colFCPart2 = st.columns([0.3, 0.5])
    colFCPart1.metric('输入特征', '降水、温度')
    colFCPart2.metric('特征优选方法', 'Pearson相关性分析')
    colFCPart3, colFCPart4 = st.columns([0.3, 0.5])
    colFCPart3.metric('优选特征集', '温度')
    colFCPart4.metric('筛选条件', '相关系数(R)<0.8')
with colFO2:
    img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '特征优选-Relief-F.png'))
    st.image(img, width=740)
    colFCPart1, colFCPart2 = st.columns([0.3, 0.5])
    colFCPart1.metric('输入特征', '降水、温度')
    colFCPart2.metric('特征优选方法', 'Relief-F互相关分析')
    colFCPart3, colFCPart4 = st.columns([0.3, 0.5])
    colFCPart3.metric('优选特征集', '温度')
    colFCPart4.metric('筛选条件', 'TOP80(%)')
category("🌏 模型构建")

st.markdown('#### 5.:'
            '模型,模型参数,评价指标,分配比例,特征信息(个数和条数)')

st.markdown('#### 6.天气情景生成器:'
            '地区,模型,年限长度,场景,异常程度,'
            '模拟气象数据生成图 ,模型预测结果 ,偏差指标结果')

st.markdown('#### 7.模型预测结果:'
            '模型构建中测试集和模拟气象数据的预测结果(地图中展示)')
