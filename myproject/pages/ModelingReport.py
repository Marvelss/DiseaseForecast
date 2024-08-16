"""
@Author : SakuraFox
@Time: 2024-08-10 9:06
@File : ModelingReport.py
@Description : 建模报告
"""
import itertools
import os.path

import streamlit as st

from PIL import Image
from st_pages import hide_pages

from lib.share import RESOURCE_IMAGES_PATH
from pages import ui

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
st.title('建模报告')
# st.markdown('# 建模报告')
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
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '数据预处理-缺失值插补.png'))
    st.image(img, width=680)
    colPart1, colPart2, colPart3 = st.columns(3)
    colPart1.metric('预处理字段', '降水')
    colPart2.metric('预处理方法', '缺失值插补')
    colPart3.metric('预处理数据条数', '30')
with colPre2:
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '数据预处理-剔除异常值.png'))
    st.image(img, width=800)
    colPart1, colPart2, colPart3 = st.columns(3)
    colPart1.metric('预处理字段', '温度')
    colPart2.metric('预处理方法', '异常值剔除')
    colPart3.metric('预处理数据条数', '50')

category("🌍 特征计算")
# 命名: 界面名称缩写
colFC1, colFC2 = st.columns(2)
with colFC1:
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '特征计算-降水累积量.png'))
    st.image(img, width=760)
    colFCPart1, colFCPart2 = st.columns([0.3, 0.5])
    colFCPart1.metric('输入字段', '降水')
    colFCPart2.metric('特征计算方法', '降水累积量计算')
    colFCPart3, colFCPart4 = st.columns([0.3, 0.5])
    colFCPart3.metric('输出特征', '降水累积量')
    colFCPart4.metric('特征条数', '30')
with colFC2:
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '特征计算-移栽期.png'))
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
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '特征优选-Pearson.png'))
    st.image(img, width=670)
    colFCPart1, colFCPart2 = st.columns([0.3, 0.5])
    colFCPart1.metric('输入特征', '降水、温度')
    colFCPart2.metric('特征优选方法', 'Pearson相关性分析')
    colFCPart3, colFCPart4 = st.columns([0.3, 0.5])
    colFCPart3.metric('优选特征集', '温度')
    colFCPart4.metric('筛选条件', '相关系数(R)<0.8')
with colFO2:
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '特征优选-Relief-F.png'))
    st.image(img, width=740)
    colFCPart1, colFCPart2 = st.columns([0.3, 0.5])
    colFCPart1.metric('输入特征', '降水、温度')
    colFCPart2.metric('特征优选方法', 'Relief-F互相关分析')
    colFCPart3, colFCPart4 = st.columns([0.3, 0.5])
    colFCPart3.metric('优选特征集', '温度')
    colFCPart4.metric('筛选条件', 'TOP80(%)')
category("🌏 模型构建")

colMB1, colMB2 = st.columns(2)
img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '模型构建-回归模型1.png'))
img1 = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '模型构建-预测结果图.png'))
with colMB1:
    st.image(img1, width=750)
    st.metric('特征集', '降水、温度、降水累积量、降雨日数')
    colMBPart1, colMBPart2 = st.columns(2)
    colMBPart1.metric('标签', '病害峰值')
    colMBPart2.metric('特征大小', '5*90')
with colMB2:
    st.image(img, width=720)
    st.metric('模型', 'Random Forest')
    colMBPart3, colMBPart4 = st.columns(2)
    colMBPart3.metric('评价指标', 'MSE、R方')
    colMBPart4.metric('数据集分配比例', '5:6')

category("🌐 基于天气情景生成器的模型评估")
colWG1, colWG2 = st.columns(2)
with colWG1:
    st.metric('地区', '湖南省湘阴县')
    st.metric('模型', 'RF、SVM')
with colWG2:
    st.metric('天气情景', '高温少雨、低温多雨')
    st.metric('年限长度', '3年')
colWG3, colWG4 = st.columns(2)
img2 = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'Figure_1.png'))
img3 = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'Figure_2.png'))
colWG3.image(img2)
colWG4.image(img3)

st.markdown('#### 基于天气情景生成器的模拟气象数据与训练数据的模型预测结果对比(去除?)')
img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '高温多雨情景下和实际病害发生程度对比图.png'))
st.image(img)
st.markdown('#### 基于天气情景生成器的模型预测与实际数据结果对比')
img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'weatherGeneratorEvaluateResult2.jpg'))
st.image(img)
co3, co4 = st.columns(2)
with co3:
    st.metric("Dev_S", "0.0799")
with co4:
    st.metric("Dev_S", "0.0899")
category("🌑 模型稳定性评估结果")
st.markdown('##### 在高温多雨的条件下，RF模型极易受到温度的影响，可能导致决策树中的特征选择不稳定。'
            '原因可能在于树模型对高维度数据的分裂规则过于敏感，高温可能使某些特征权重过高或过低。'
            '这种情况下，模型的输出可能波动较大，预测结果不稳定。\n'
            '##### RF模型在高温多雨的极端气象情景下,极易遭受温度的影响,模型极不稳定\n'
            '##### KNN模型在低温多雨的极端气象情景下,不易遭受温度的影响,模型十分稳定')
