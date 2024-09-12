"""
@Author : SakuraFox
@Time: 2024-08-10 9:06
@File : ModelingReport.py
@Description : 建模报告
"""
import base64
import itertools
import os.path

import streamlit as st

from PIL import Image
from st_pages import hide_pages

from lib.share import RESOURCE_IMAGES_PATH, MODEL_REPORT_NUMBER, RESOURCE_TEMPDIR_PATH
from pages import ui

st.set_page_config(
    layout="wide"
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
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
    btnTemp1 = ui.colored_header_btn(name, next(category_colors_cycle), description)
    st.write("")
    return btnTemp1


# st.header('建模报告')
colHead1, colHead2 = st.columns([0.7, 0.2])
with colHead1:
    st.title('多场景作物病虫害预测建模报告')
with colHead2:
    st.markdown(' ')
    st.markdown(f'#### 编号:20000801x{str(MODEL_REPORT_NUMBER)}')
    st.markdown('#### 日期:2024年8月31日')
# st.markdown('# 建模报告')
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
if 'hideBtnDict' not in st.session_state:
    st.session_state.hideBtnDict = {
        'brief': False,
        'raw': False,
        'pre': False,
        'fc': False,
        'fo': False,
        'mb': False,
        'wg': False,
    }

hideBtnBrief = st.empty()
hideBtnRaw = st.empty()
hideBtnPre = st.empty()
hideBtnFC = st.empty()
hideBtnFO = st.empty()
hideBtnMB = st.empty()
hideBtnWG = st.empty()

with hideBtnBrief.container():
    btnBrief = category("ℹ️ 简介", '简介')
    st.markdown('##### &emsp;&emsp;本次建模使用了<u>气象数据和植保数据</u>，'
                '通过<u>缺失值插补</u>、<u>异常值剔除</u>等预处理步骤，'
                '并计算了<u>降水累积量</u>、<u>降雨日数</u>等特征，'
                '然后基于<u>Relief-F算法</u>筛选了优选特征集，'
                '最后采用<u>SVM、RF</u>等机器学习方法，'
                '构建了<u>茶树炭疽病</u>动态预测模型。', unsafe_allow_html=True)
    colInfo1, colInfo2, colInfo3, colInfo4 = st.columns(4)
    if btnBrief:
        st.session_state.hideBtnDict['brief'] = True

with hideBtnRaw.container():
    btnRaw = category("📊️ 原始数据", '原始数据')
    colDS1, colDS2 = st.columns(2)
    with colDS1:
        st.metric('原始字段', '经度、纬度、年、DayOfYear、温度')
    with colDS2:
        st.metric('数据大小', '5*30')
    colDS3, colDS4 = st.columns(2)
    with colDS3:
        st.metric('数据类型', '气象数据 植保数据')
    with colDS4:
        st.metric('影响因素', '气温 降水 湿度')
    if btnRaw:
        st.session_state.hideBtnDict['raw'] = True
with hideBtnPre.container():
    btnPre = category("🌌 预处理", '预处理')
    st.markdown('##### &emsp;&emsp;本次预处理涉及<u>降水、温度、湿度</u>字段，'
                '目前剩余<u>10000</u>条数据，具体内容如下:', unsafe_allow_html=True)
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '数据预处理-缺失值插补.png'))
    st.image(img)
    colPart1, colPart2, colPart3 = st.columns(3)
    colPart1.metric('预处理字段', '温度')
    colPart2.metric('预处理方法', '缺失值插补')
    colPart3.metric('预处理数据条数', '3')
    # with colPre2:
    #     img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '数据预处理-剔除异常值.png'))
    #     st.image(img, width=800)
    #     colPart1, colPart2, colPart3 = st.columns(3)
    #     colPart1.metric('预处理字段', '温度')
    #     colPart2.metric('预处理方法', '异常值剔除')
    #     colPart3.metric('预处理数据条数', '50')
    if btnPre:
        st.session_state.hideBtnDict['pre'] = True
with hideBtnFC.container():
    btnFC = category("🌍 特征计算", '特征计算')
    # 命名: 界面名称缩写
    colFC1, colFC2 = st.columns(2)
    # with colFC1:
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '特征计算-降水累积量.png'))
    st.image(img)
    colFCPart1, colFCPart2 = st.columns(2)
    colFCPart1.metric('输入字段', '降水')
    colFCPart2.metric('特征计算方法', '降水累积量计算')
    colFCPart3, colFCPart4 = st.columns(2)
    colFCPart3.metric('输出特征', '07-19_08-23_降水累积量')
    colFCPart4.metric('特征条数', '1271')
    # with colFC2:
    #     img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '特征计算-移栽期.png'))
    #     st.image(img, width=700)
    #     colFCPart1, colFCPart2 = st.columns([0.3, 0.5])
    #     colFCPart1.metric('输入字段', '温度')
    #     colFCPart2.metric('特征计算方法', '基于活动积温的生育期计算')
    #     colFCPart3, colFCPart4 = st.columns([0.3, 0.5])
    #     colFCPart3.metric('输出特征', '生育期')
    #     colFCPart4.metric('特征条数', '30')
    if btnFC:
        st.session_state.hideBtnDict['fc'] = True

with hideBtnFO.container():
    btnFO = category("🌎 特征优选", '特征优选')
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
    if btnFO:
        st.session_state.hideBtnDict['fo'] = True

with hideBtnMB.container():
    btnMB = category("🌏 模型构建", '模型构建')
    colMB1, colMB2 = st.columns(2)
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '模型构建-回归模型1.png'))
    img1 = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '模型构建-预测结果图.png'))
    # with colMB1:
    # st.image(img1, width=750)
    cc1, colMBPart1, colMBPart2 = st.columns([0.7, 0.3, 0.3])
    cc1.metric('特征集', 'class-AREA_MN、land-FRAC_MN、class-FRAC_MN、01-01_01-31降雨日数、07-19_08-23_降水累积量')
    colMBPart1.metric('标签', '病害峰值')
    colMBPart2.metric('特征大小', '5*90')
    # with colMB2:
    # st.image(img, width=720)
    # st.metric('模型', 'PLSR')
    cc2, colMBPart3, colMBPart4 = st.columns([0.7, 0.3, 0.3])
    cc2.metric('模型', 'PLSR')
    colMBPart3.metric('评价指标', 'MSE、R方')
    colMBPart4.metric('数据集分配比例', '5:6')
    if btnMB:
        st.session_state.hideBtnDict['mb'] = True

with hideBtnWG.container():
    btnWG = category("🌐 基于天气情景生成器的模型评估", '模型评估')
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
    st.markdown('#### 基于天气情景生成器的模型预测与实际数据结果对比')
    img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'weatherGeneratorEvaluateResult2.jpg'))
    st.image(img)
    co3, co4 = st.columns(2)
    with co3:
        st.metric("Dev_S", "0.0799")
    with co4:
        st.metric("Dev_S", "0.0899")
    if btnWG:
        st.session_state.hideBtnDict['wg'] = True

# 控制隐藏
for key, btn in st.session_state.hideBtnDict.items():
    if st.session_state.hideBtnDict.get(key, False):
        if key == 'brief':
            hideBtnBrief.empty()
        elif key == 'raw':
            hideBtnRaw.empty()
        elif key == 'pre':
            hideBtnPre.empty()
        elif key == 'fc':
            hideBtnFC.empty()
        elif key == 'fo':
            hideBtnFO.empty()
        elif key == 'mb':
            hideBtnMB.empty()
        elif key == 'wg':
            hideBtnWG.empty()


def displayLocalGIF1(placeholder, localImagePath, caption):
    imgFile = open(localImagePath, "rb")
    contents = imgFile.read()
    imgData = base64.b64encode(contents).decode("utf-8")
    imgFile.close()

    # Define CSS styles for the container and caption
    container_style = (
        "position: relative;"  # Enable relative positioning
        "display: inline-block;"  # Display as inline-block to align with placeholder
    )

    caption_style = (
        "font-size: 20px;"  # Adjust the font size as needed
        "color: #888888;"  # Dimmer color
        "text-align: center;"  # Center the caption text
    )

    # Display the GIF and caption with positioning relative to the placeholder
    placeholder.markdown(f"""<div style="{container_style}">
                    <img src="data:image/gif;base64,{imgData}" width='610' height='610'>
                    <p style="{caption_style}">{caption}</p>
                    </div>""", unsafe_allow_html=True)


def displayLocalGIF2(placeholder, localImagePath1, localImagePath2, caption1, caption2):
    # Function to generate the base64 encoded image data
    def get_img_data(image_path):
        with open(image_path, "rb") as img_file:
            contents = img_file.read()
            return base64.b64encode(contents).decode("utf-8")

    imgData1 = get_img_data(localImagePath1)
    imgData2 = get_img_data(localImagePath2)

    # Define CSS styles for the container and images
    container_style = (
        "display: flex;"  # Use flexbox layout for side-by-side alignment
        "justify-content: center;"  # Center the container content
        "gap: 20px;"  # Add space between the GIFs
    )

    img_style = "width: 610px; height: 610px;"  # Set image size

    caption_style = (
        "font-size: 20px;"  # Adjust the font size as needed
        "color: #888888;"  # Dimmer color
        "text-align: center;"  # Center the caption text
    )

    # Display the GIFs and captions side by side
    placeholder.markdown(f"""
        <div style="{container_style}">
            <div>
                <img src="data:image/gif;base64,{imgData1}" style="{img_style}">
                <p style="{caption_style}">{caption1}</p>
            </div>
            <div>
                <img src="data:image/gif;base64,{imgData2}" style="{img_style}">
                <p style="{caption_style}">{caption2}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


btnResult = category("🌑 模型稳定性评估结果", '所有按钮')
st.markdown('##### &emsp;&emsp;本实施例基于气象多情景仿真器输出的<u>高温多雨情景</u>、<u>低温少雨情景</u>数据与'
            '常温常雨情景数据对<u>茶小绿叶蝉虫害预测模型</u>进行评价，该模型为<u>动态预</u>'
            '测模型，使用动态预测模型评价方法对其进行评价，模型输出为<u>病害压力值</u>。\n'
            '##### &emsp;&emsp;计算可得常温常雨情景下压力值预测输出的动态偏差指标Dev_D 压力值＝0.'
            '0047，模型等级预测输出的动态偏差指标Dev_D 等级＝<u>-0.0359</u>；高温多雨情'
            '景下模型压力值预测输出的动态偏差指标Dev_D 压力值＝＝0.0262，模型等级'
            '预测输出的动态偏差指标Dev_D 等级＝0.0539；低温少雨情景下模型压力值预'
            '测输出的动态偏差指标Dev_D 压力值＝＝-0.0815，模型等级预测输出的动态'
            '偏差指标Dev_D 等级＝-0.0179。\n'
            '##### &emsp;&emsp;已知茶小绿叶蝉虫害的发生与温度、降雨量等关系密切，适宜的温度和降雨'
            '将促进小绿叶蝉的生长，否则会抑制生长，且一年中茶小绿叶蝉虫害的发生'
            '存在两个高峰期，分别在<u>5月和9月</u>。\n'
            '##### &emsp;&emsp;通过比对中各情景'
            '下预测模型输出的预测发生程度及预测压力值，可看到预测模型预测的整体'
            '虫害趋势未发生改变，各情景在5月和9月均存在虫害高峰期。由于温度降水'
            '影响，高温多雨情景下虫害发生期在<u>2月和3月</u>略有延长，该情景下模型动态'
            '偏差指标均呈现<u>正向</u>偏移，整体预测虫害压力值<u>高于</u>普通常温常雨情景；低'
            '温少雨情景下虫害发生期在3月略有缩短，模型动态偏差指标均呈现负向偏'
            '移，压力值低于普通常温常雨情景。预测结果与病虫害习性较为相符，且在'
            '多次模拟过程中结果趋势均保持较高程度的一致，模型输出较为合理。\n'
            '##### &emsp;&emsp;根据上述计算结果进行综合评估，可认为该模型<u>可靠性较高</u>，参数设置较为'
            '合理，具有良好的预测效果和鲁棒性。', unsafe_allow_html=True)
if btnResult:
    st.markdown("""
    <style>
    .st-emotion-cache-1vt4y43.ef3psqc12 {display: none;}
    </style>
    """, unsafe_allow_html=True)
imagePath1 = os.path.join(RESOURCE_TEMPDIR_PATH, "s_output1.gif")
imagePath2 = os.path.join(RESOURCE_TEMPDIR_PATH, "e_output1.gif")
displayLocalGIF2(st.empty(), imagePath1, imagePath2, "模型预测结果图", "模型预测结果图2")
