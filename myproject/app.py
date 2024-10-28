import datetime
import os

import pandas as pd
import streamlit as st

from st_pages import Page, show_pages, hide_pages
from streamlit import switch_page

import itertools

from lib.share import PROJECT_PATH, PAGES_PATH, RESOURCE_IMAGES_PATH, IMAGECOUNT, RESOURCE_PROCESS_PATH
from pages import ui, pages_utils
from pages.modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod

# add_page_title()


# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="多场景作物病虫害预测建模系统",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)

HORIZONTAL_BLUE = os.path.join(RESOURCE_IMAGES_PATH, 'icon.png')
ICON_BLUE = os.path.join(RESOURCE_IMAGES_PATH, 'HDU_Logo.png')
# HORIZONTAL_BLUE = os.path.join(RESOURCE_IMAGES_PATH, 'Header.png')

sidebar_logo = ICON_BLUE
main_body_logo = HORIZONTAL_BLUE

st.logo(sidebar_logo, icon_image=main_body_logo)

# 控制界面显示
show_pages(
    [
        Page(os.path.join(PROJECT_PATH, 'app.py'), "主页"),
        Page(os.path.join(PAGES_PATH, 'DataSet.py'), "原始数据"),
        Page(os.path.join(PAGES_PATH, 'DataPreparation.py'), "数据预处理"),
        Page(os.path.join(PAGES_PATH, 'FeatureCalculation.py'), "特征计算"),
        Page(os.path.join(PAGES_PATH, 'FeatureOptimization.py'), "特征优选"),
        Page(os.path.join(PAGES_PATH, 'ModelBuilding.py'), "模型构建"),
        Page(os.path.join(PAGES_PATH, 'WeatherGenerator.py'), "基于天气情景生成器的模型评价"),
        Page(os.path.join(PAGES_PATH, 'ModelingReport.py'), "建模报告"),
        Page(os.path.join(PAGES_PATH, 'ModelApplication.py'), "模型应用"),
        Page(os.path.join(PAGES_PATH, 'Visualization.py'), "数据下载中心"),

        Page(os.path.join(PAGES_PATH, 'DataSetFacet.py'), "原始数据-面状"),
        Page(os.path.join(PAGES_PATH, 'DataPreparationFacet.py'), "数据预处理-面状"),
        Page(os.path.join(PAGES_PATH, 'FeatureCalculationFacet.py'), "特征计算-面状"),
        Page(os.path.join(PAGES_PATH, 'FeatureOptimizationFacet.py'), "特征优选-面状"),
        Page(os.path.join(PAGES_PATH, 'ModelBuildingFacet.py'), "模型构建-面状"),
        Page(os.path.join(PAGES_PATH, 'WeatherGeneratorFacet.py'), "基于天气情景生成器的模型评价-面状"),
        Page(os.path.join(PAGES_PATH, 'ModelingReportFacet.py'), "建模报告-面状"),
        Page(os.path.join(PAGES_PATH, 'ModelApplicationFacet.py'), "模型应用-面状"),
        Page(os.path.join(PAGES_PATH, 'VisualizationFacet.py'), "数据下载中心-面状"),
        Page(os.path.join(PAGES_PATH, 'ModelEvaluation.py'), "测试界面"),

    ]
)

# 隐藏页面
hide_pages(
    ["原始数据", "数据预处理", "特征计算",
     "特征优选", "模型构建", "基于天气情景生成器的模型评价", "基于天气情景生成器的模型评价-面状",
     "模型应用", "模型应用-面状",
     "原始数据-面状",
     "数据预处理-面状",
     "特征计算-面状",
     "特征优选-面状",
     "模型构建-面状",
     "建模报告", "建模报告-面状",
     "数据下载中心", "数据下载中心-面状",
     ]
)

# 初始化控制各环节左侧内容展示
if 'page12' not in st.session_state:
    st.session_state.page12 = 0
# 左侧内容标题
if "leftTabs" not in st.session_state:
    st.session_state["leftTabs"] = ['原始数据']
if "leftTabsFacet" not in st.session_state:
    st.session_state["leftTabsFacet"] = ['备选特征']
# 控制模型构建等后续步骤点/面界面显示
if "isPlanarInterface" not in st.session_state:
    st.session_state.isPlanarInterface = False

if "IMAGECOUNT" not in st.session_state:
    st.session_state.IMAGECOUNT = IMAGECOUNT

# 研究区经纬度中心
if "areaCenter" not in st.session_state:
    st.session_state.areaCenter = [30.314207, 120.343200]
# 设置网页标题
st.title('多场景作物病虫害快速预测建模系统')

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


# 清空各环节初始化按钮
def emptyValue():
    pages_utils.TempDataSetField = [
        pd.DataFrame(
            columns=["编号", "数据类型", "文件名称", "字段", "传输状态", "上传时间"]),
        pd.DataFrame(
            columns=["编号", "数据类型", "输入字段", "预处理后字段", "大小", "预处理方法", "方法参数", '时间',
                     "处理状态"]),
        pd.DataFrame(
            columns=["编号", "数据类型", "输入特征", "备选特征", "大小", "特征计算方法", "方法参数", "时间",
                     "处理状态"]),
        pd.DataFrame(
            columns=["编号", "数据类型", "输入特征", "优选特征", "大小", "特征优选方法", "方法参数", "时间",
                     "处理状态"]),
        pd.DataFrame(
            columns=["编号", "模型", "模型参数", "特征", "标签", "评价指标", "数据集划分比例", "时间", "实际和预测值",
                     "处理状态"])]

    pages_utils.TempDataSet = [
        pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"]),
        pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"]),
        pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"]),
        pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"]),
        pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])]

    # 初始化面状数据
    pages_utils.RawDataSetFieldFacet = {"编号": [], "文件名称": [], "数据类型": [], "数据格式": [],
                                        "根节点": [], "子节点": [], "字段": [], "传输状态": [], "上传时间": []}
    pages_utils.PreprocessedDataSetFieldFacet = {"编号": [], "数据类型": [], "数据格式": [], "根节点": [],
                                                 "子节点": [], "字段": [], "输入文件": [], "文件名称": [],
                                                 "预处理方法": [], "方法参数": [], "时间": [], "处理状态": []}
    pages_utils.FeatureDataSetFieldFacet = {"编号": [], "输入文件": [], "文件名称": [], "数据类型": [],
                                            "数据格式": [], "根节点": [], "子节点": [], "字段": [],
                                            "特征计算方法": [], "方法参数": [], "时间": [], "处理状态": []}
    pages_utils.OptimalFeatureDataSetFieldFacet = pd.DataFrame(
        columns=["编号", "数据类型", "输入特征", "优选特征", "大小", "特征优选方法", "方法参数", "时间", "处理状态"])
    pages_utils.UltimateFeatureDataSetFacet = pd.DataFrame(
        columns=["编号", "模型", "模型参数", "特征", "标签", "评价指标", "数据集划分比例", "模型结构", "模型训练结果",
                 "时间",
                 "处理状态"])
    pages_utils.TempDataSetFieldFacet = [
        pages_utils.RawDataSetFieldFacet,
        pages_utils.PreprocessedDataSetFieldFacet,
        pages_utils.FeatureDataSetFieldFacet,
        pages_utils.OptimalFeatureDataSetFieldFacet,
        pages_utils.UltimateFeatureDataSetFacet
    ]

    # 特征值
    pages_utils.RawDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
    pages_utils.PreprocessedDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
    pages_utils.FeatureDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
    pages_utils.OptimalFeatureDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
    pages_utils.UltimateFeatureDataSet = pd.DataFrame(columns=["经度", "纬度", "年", "DayOfYear"])
    pages_utils.TempDataSetFacet = [
        pages_utils.RawDataSet,
        pages_utils.PreprocessedDataSet,
        pages_utils.FeatureDataSet,
        pages_utils.OptimalFeatureDataSet,
        pages_utils.OptimalFeatureDataSet]

    # 预处理界面初始化(使用系统界面右上角界面clear cache自动清空)
    # st.session_state["preMethodName"] = {'checkBox': None}
    # st.session_state["DPVisualInformation"] = []
    # st.session_state["leftTabs"] = ['原始数据']
    # st.session_state.page12 = 0


category("🌈 初始化建模数据")
colDPF21col1, colDPF21col2 = st.columns([8, 10])
with colDPF21col1:
    pass
with colDPF21col2:
    if st.button('↩️初始化各环节数据', on_click=emptyValue):
        st.toast("初始化完毕", icon="ℹ️️")


# st.markdown("""
# <style>
# button {
#     height: 150px;
#     width: 200px;
#     color: blue;
# border-radius: 25px; /* Optional: for rounded buttons */
# }
# </style>
# """, unsafe_allow_html=True)
@st.experimental_dialog("请输入建模场景名称")
def inputName(dataType):
    name = st.text_input("输入",
                         placeholder='水稻纹枯病SEIR动态预测模型',
                         # autocomplete='水稻纹枯病SEIR动态预测模型',
                         label_visibility='collapsed')
    if dataType == '面状数据建模':
        st.markdown('##### 设置研究区')
        colTT1, colTT2 = st.columns(2)
        st.session_state.areaCenter[0] = colTT1.text_input('纬度')
        st.session_state.areaCenter[1] = colTT2.text_input('经度')
    if st.button("提交并跳转界面"):
        st.session_state.modelingName = name
        if dataType == '点状数据建模':
            st.session_state.isPlanarInterface = False
            switch_page(os.path.join(PAGES_PATH, 'DataSet.py'))
        else:
            st.session_state.isPlanarInterface = True
            switch_page(os.path.join(PAGES_PATH, 'DataSetFacet.py'))


if "modelingName" not in st.session_state:
    st.session_state.modelingName = None

category("🗣️ 点/面数据建模入口")
colAppImg1, colAppImg2, = st.columns(2)
with colAppImg1:
    st.image(os.path.join(RESOURCE_IMAGES_PATH, 'IndexPoint.png'))
    _, colAppBtn2, = st.columns([0.4, 0.6])
    with colAppBtn2:
        if st.button('点状数据建模'):
            if not st.session_state.modelingName:
                inputName('点状数据建模')
            else:
                switch_page(os.path.join(PAGES_PATH, 'DataSet.py'))

with colAppImg2:
    st.image(os.path.join(RESOURCE_IMAGES_PATH, 'facetBtn.png'))
    _, colAppBtn3, = st.columns([0.4, 0.6])
    with colAppBtn3:
        if st.button('面状数据建模'):
            if not st.session_state.modelingName:
                inputName('面状数据建模')
            else:
                switch_page(os.path.join(PAGES_PATH, 'DataSetFacet.py'))


def navbar():
    """Shows a sticky navigation bar with links to other apps at the top of the page."""
    st.write(
        """
        <style>
            /* Add a black background color to the top navigation */
            .topnav-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3.5rem;
                /* border-bottom: 1px solid rgba(38, 39, 48, 0.2); */
                /* padding-left: 60px; */
                /* padding-top: 0.5rem;
                padding-bottom: 0.5rem; */
                /* padding-right: 100px; */
                background-color: white;
                z-index: 98;

                line-height: 3.5rem;

                flex: 1 1 0%;

            }

            .topnav {
                overflow: hidden;
                /* position: relative;
                top: -50px; */
                padding-left: 1rem;
                padding-right: 1rem;

                max-width: 730px;
                margin: 0 auto;

                display: flex;
                /*justify-content: space-between;*/
                justify-content: center;
                align-items: center;

                vertical-align: middle;
            }

            /* Style the links inside the navigation bar */
            .topnav a {
                color: rgb(38, 39, 48);
                text-align: center;
                text-decoration: none;
                /* font-size: 17px; */
            }

            /* Change the color of links on hover */
            .topnav a:hover {
                color: #e24768;
            }

            /* Add a color to the active/current link */
            .topnav a.active {
                color: #e24768;
            }

            /*.topnav-right a {
                margin-left: 3rem;
            }*/

            .topnav-right {
                display: none;
            }

            @media screen and (max-width: 800px) {
                .topnav-right {
                    display: none;
                }

                .topnav {
                    justify-content: center;
                }
            }

            .topnav-title {
                margin-left: 1rem;
                font-weight: 500;
            }
        </style>

        <div class="topnav-container">
            <nav class="topnav">
                <div class="topnav-left">
                    <a href="https://share.streamlit.io/jrieke/st-frontpage/main">
                        <img src="https://streamlit.io/images/brand/streamlit-mark-color.png" width=35>
                        <span class="topnav-title">View all apps</span>
                    </a>
                </div>
                <div class="topnav-right">
                    <a href="https://share.streamlit.io/jrieke/st-frontpage/main">View all apps</a>
                    <a href="https://share.streamlit.io/" target="_blank"><img src="https://screenshots.imgix.net/mui-org/material-ui-icons/account-circle-outlined/~v=3.9.2/e6ffca0e-87fa-4e5b-92ca-05c6079b5f9e.png?ixlib=js-1.2.0&s=c0f87e872aac058178a34a41422a425d" width=35 style="border-radius: 100%; margin-left: 1rem;"></a>
                </div>
            </nav>
        </div>
        """,
        unsafe_allow_html=True,
    )


# st.images("https://streamlit.io/images/brand/streamlit-mark-color.png", width=100)
# st.title("Snowflake Summit Demo Apps")

st.markdown(
    """
    <style>
        .screenshot {
            border: 1px solid rgba(38, 39, 48, 0.2);
            border-radius: 0.25rem;
        }

        h3 {
            padding-top: 1rem;
        }

        h3 a {
            color: var(--text-color) !important;
            text-decoration: none;
        }

        small a {
            color: var(--text-color) !important;
            text-decoration: none;
        }

        a:hover {
            text-decoration: none;
        }
    </style>

    <!-- Open links in new tabs by default. Required for Streamlit sharing to not open links within the iframe. -->
    <base target="_blank">
    """,
    unsafe_allow_html=True,
)


@st.experimental_dialog("接口调用", width='large')
def vote(titleName):
    afterHandleData = pd.DataFrame()
    if titleName == '降雨日数计算':
        # 上传数据集
        st.markdown('### 上传数据集')
        # col1321, col1322 = st.columns([0.5, 0.5])
        # with col1321:
        st.info("说明:  \n"
                "上传的数据集必须包含字段:经度、纬度、DayOfYear、年、降水", icon="ℹ️️")
        # with col1322:
        uploaded_files = st.file_uploader(
            "上传数据集",
            accept_multiple_files=False,
            label_visibility='collapsed',
            type=['xlsx', 'csv', 'txt', 'xls', 'zip'],
            help='help')

        st.markdown('### 参数设置')
        d1 = st.date_input("开始时间(默认处理各年数据集)",
                           value=datetime.date(1990, 7, 6),
                           format='MM/DD/YYYY',
                           )
        d2 = st.date_input("结束时间", format='MM/DD/YYYY', value=datetime.date(2024, 8, 9))
        st.selectbox(
            '计算阈值方式',
            ('单日降水量',))
        number2 = st.text_input("单日降水量数值(mm)", value=0.1)
        number1 = st.number_input("连续降雨日数时长(天数)", value=1, min_value=1)
        if uploaded_files:
            bytes_data = uploaded_files.read()
            data33 = pd.read_excel(bytes_data)
            afterHandleData, _ = FeatureCalculationMethod(
                data33, data33.columns.tolist()).rainfallDaysAccumulation(
                ['降水'], [str(d1), str(d2), '单日降水量', str(number2), str(number1)])
        interval_col1, interval_col2 = st.columns([6, 1])
        btn = interval_col2.button('运行')
        if btn:
            # 保存文件
            afterDataPath = os.path.join(RESOURCE_PROCESS_PATH, f'{titleName}_api返回数据.xlsx')
            afterHandleData.to_excel(afterDataPath)
            with open(afterDataPath, "rb") as file:
                interval_col2.download_button(
                    label="下载数据",
                    data=file,
                    file_name=f'{titleName}_api返回数据.xlsx',
                    mime="application/octet-stream"
                )
    elif titleName == '降水累积量计算':
        # 上传数据集
        st.markdown('### 上传数据集')
        st.info("说明:  \n"
                "上传的数据集必须包含字段:经度、纬度、DayOfYear、年、降水", icon="ℹ️️")
        uploaded_files = st.file_uploader(
            "上传数据集",
            accept_multiple_files=False,
            label_visibility='collapsed',
            type=['xlsx', 'csv', 'txt', 'xls', 'zip'],
            help='help')
        st.markdown('### 参数设置')
        option3 = st.selectbox(
            '降水累积量计算',
            ('指定日期', '月累积降水量'))
        param1 = [option3]
        if option3 == '指定日期':
            sd1 = st.date_input("开始时间", value=datetime.date(2024, 7, 1))
            ed1 = st.date_input("结束时间", value=datetime.date(2024, 8, 1))
            param1 = [option3, sd1.strftime('%m-%d'), ed1.strftime('%m-%d')]
        if uploaded_files:
            bytes_data = uploaded_files.read()
            data33 = pd.read_excel(bytes_data)
            afterHandleData, _ = FeatureCalculationMethod(
                data33, data33.columns.tolist()).precipitationAccumulation(
                ['降水'], param1)
        interval_col1, interval_col2 = st.columns([6, 1])
        btn = interval_col2.button('运行')
        if btn:
            # 保存文件
            afterDataPath = os.path.join(RESOURCE_PROCESS_PATH, f'{titleName}_api返回数据.xlsx')
            afterHandleData.to_excel(afterDataPath)
            with open(afterDataPath, "rb") as file:
                interval_col2.download_button(
                    label="下载数据",
                    data=file,
                    file_name=f'{titleName}_api返回数据.xlsx',
                    mime="application/octet-stream"
                )
    elif titleName == '基于活动积温的生育期计算':
        # 上传数据集
        st.markdown('### 上传数据集')
        st.info("说明:  \n"
                "上传的数据集必须包含字段:经度、纬度、DayOfYear、年、温度", icon="ℹ️️")
        uploaded_files = st.file_uploader(
            "上传数据集",
            accept_multiple_files=False,
            label_visibility='collapsed',
            type=['xlsx', 'csv', 'txt', 'xls', 'zip'],
            help='help')
        st.markdown('### 参数设置')
        growthPeriod = st.selectbox(
            '生育期',
            ('抽穗期', '孕穗期', '移栽期'))
        growthPeriodStartDate = st.date_input("开始时间", value='today')
        growthPeriodEndDate = st.date_input("结束时间", value='today')
        # 积温阈值默认为50
        threshold = 50
        if growthPeriod == '抽穗期':
            threshold = 50
        elif growthPeriod == '孕穗期':
            threshold = 100
        elif growthPeriod == '移栽期':
            threshold = 150
        growthPeriodNumber = st.number_input(
            "积温阈值温度(50-300℃)", value=threshold, step=50,
            min_value=50, max_value=300)
        param1 = [growthPeriod,
                  growthPeriodStartDate.strftime('%m-%d'),
                  growthPeriodEndDate.strftime('%m-%d'),
                  str(growthPeriodNumber)]
        if uploaded_files:
            bytes_data = uploaded_files.read()
            data33 = pd.read_excel(bytes_data)
            afterHandleData, _ = FeatureCalculationMethod(
                data33, data33.columns.tolist()).growthPeriodCalculation(
                ['温度'], param1)
        interval_col1, interval_col2 = st.columns([6, 1])
        btn = interval_col2.button('运行')
        if btn:
            # 保存文件
            afterDataPath = os.path.join(RESOURCE_PROCESS_PATH, f'{titleName}_api返回数据.xlsx')
            afterHandleData.to_excel(afterDataPath)
            with open(afterDataPath, "rb") as file:
                interval_col2.download_button(
                    label="下载数据",
                    data=file,
                    file_name=f'{titleName}_api返回数据.xlsx',
                    mime="application/octet-stream"
                )


def app(image, link, name, description, developer, repo_link):
    ui.linked_image(image, link)
    # st.subheader(f"[{name}]({link})")
    st.subheader(f"{name}")
    st.write(f"{description}")
    #     st.caption(f"[{description}]({link})")
    # clone_code = "git clone {} ".format(repo_link)
    # st.text(clone_code)
    #     repo_link = "https://github.com/streamlit/{0}/".format(repo_name)
    # st.write(f"[View App]({link})")
    # st.write("[View GitHub Repo](%s)" % repo_link)
    st.caption(f"开发人员：[{developer}](%s)" % repo_link)

    # st.write("[调用接口](%s)" % repo_link)
    # if st.button(f"调用API:{name}"):
    #     vote(name)
    # st.markdown(link)
    # st.text("[调用该接口](%s)" % repo_link)

    st.write("")


category("📊️ 各项特征计算方法API")
col1, col2, col3 = st.columns(3)
with col1:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'featureP1.png'),
        '#',
        "降雨日数计算",
        "基于特定时间段内降雨量和阈值及连续时长计算有效降雨日数",
        "杭电数字农业团队",
        "https://github.com/Marvelss",
        )

with col2:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'featureP2.png'),
        '#',
        "降水累积量计算",
        "积累加某个时间段内降雨量以计算降水累量",
        "杭电数字农业团队",
        "https://github.com/Marvelss",
        )
with col3:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'featureP3.png'),
        '#',
        "活动积温计算",
        "积累加某个时间段内活动温度以计算积温",
        "杭电数字农业团队",
        "https://github.com/Marvelss",
        )
col21, col22, col23 = st.columns(3)
with col21:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'featureSE.png'),
        '#',
        "时空抽取",
        "差异化提取作物病害敏感时段下的遥感数据的ROI区域均值",
        "杭电数字农业团队",
        "https://github.com/Marvelss",
        )

with col22:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'NDVI.jpg'),
        '#',
        "植被指数计算",
        "基于卫星可见光和近红外波段进行组合形成的指数",
        "杭电数字农业团队",
        "https://github.com/Marvelss",
        )
with col23:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'land-12-00496-g001-550.png'),
        '#',
        "景观指数计算",
        "反映景观结构的组成和空间配置某些方面特征的简单定量指标",
        "Landscapemetrics",
        "https://github.com/r-spatialecology/landscapemetrics",
        )
category("🌾 各项建模方法API")
col31, col32, col33 = st.columns(3)
with col31:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'modelSIER.png'),
        '#',
        " 水稻纹枯病SEIR机理模型",
        "基于SEIR基本模型框架,耦合气象和峰值数据,实现水稻纹枯病株率预测",
        "杭电数字农业团队",
        "https://github.com/Marvelss",
        )
with col32:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'modeRF.jpg'),
        '#',
        " 随机森林",
        "一种机器学习方法，用于构建作物病虫害分类模型",
        "scikit-learn",
        "https://github.com/Marvelss",
        )
with col33:
    app(os.path.join(RESOURCE_IMAGES_PATH, 'modelPLSR.png'),
        '#',
        " 偏最小二乘回归",
        "一种统计模型，可用于构建作物病虫害峰值模型",
        "scikit-learn",
        "https://github.com/Marvelss",
        )
