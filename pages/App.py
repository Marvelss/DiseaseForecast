import pandas as pd
import streamlit as st

from st_pages import Page, show_pages

import pages_utils
import itertools
import ui

# add_page_title()


# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="病虫害预测系统",
    layout="wide"
)

# Establish communication between pygwalker and streamlit
# init_streamlit_comm()

# 控制界面显示
show_pages(
    [
        Page("pages/App.py", "主页"),
        Page("pages/DataSet.py", "原始数据"),
        Page("pages/DataPreparation.py", "数据预处理"),
        Page("pages/FeatureCalculation.py", "特征计算"),
        Page("pages/FeatureOptimization.py", "特征优选"),
        Page("pages/ModelBuilding.py", "模型构建"),
        Page("pages/WeatherGenerator.py", '基于天气情景生成器的模型评价'),
        Page("pages/Visualization.py", '可视化及数据下载'),
        Page("pages/ModelApplication.py", '模型应用'),
        Page("pages/ModelEvaluation.py", "测试界面")
    ]
)
# 初始化控制各环节左侧内容展示
if 'page12' not in st.session_state:
    st.session_state.page12 = 0
# 左侧内容标题
if "leftTabs" not in st.session_state:
    st.session_state["leftTabs"] = ['原始数据']

# 设置网页标题
st.title('多场景病虫害预测系统')


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
        pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"]),
        pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"]),
        pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"]),
        pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"]),
        pd.DataFrame(columns=["上级单位", "测报站点", "年", "DayOfYear"])]

    # 预处理界面初始化(使用系统界面右上角界面clear cache自动清空)
    # st.session_state["preMethodName"] = {'checkBox': None}
    # st.session_state["DPVisualInformation"] = []
    # st.session_state["leftTabs"] = ['原始数据']
    # st.session_state.page12 = 0


if st.button('初始化数据', on_click=emptyValue):
    st.toast("初始化完毕", icon="ℹ️️")


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


# st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=100)
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


@st.experimental_dialog("有效值提取", width='large')
def vote():
    isExtract = st.checkbox('提取有效值')
    # 分组并提取每个分组的第一个非空值
    # a = st.data_editor(pd.DataFrame([]), num_rows="dynamic", width=700, height=300)

    # 选择后变化
    if st.button("Submit"):
        if isExtract:
            print('开始')
        st.rerun()


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
    if st.button(f"调用API:{name}"):
        vote()
        st.markdown(link)
    # st.text("[调用该接口](%s)" % repo_link)

    st.write("")


category("🗣️ 各项特征计算方法API")
col1, col2, col3 = st.columns(3)
with col1:
    app("pages/images/GPTLab.png",
        '#',
        "降雨日数计算",
        "基于特定时间段内降雨量和阈值及连续时长计算有效降雨日数",
        "Vagrant",
        "https://github.com/Marvelss",
        )

with col2:
    app("pages/images/AskMyPDF.png",
        '#',
        "降水累积量计算",
        "累加某个时间段内降雨量以计算降水累积量",
        "Vagrant",
        "https://github.com/Marvelss",
        )
with col3:
    app("pages/images/HugChat.png",
        '#',
        "基于活动积温的生育期计算",
        "基于每日累积温度达到特定积温阈值的时间即为相应生育期",
        "Vagrant",
        "https://github.com/Marvelss",
        )
col21, col22, col23 = st.columns(3)
with col21:
    app("pages/images/KnowledgeGPT.png",
        '#',
        "时空抽取",
        "待补充",
        "Vagrant",
        "https://github.com/Marvelss",
        )

with col22:
    app("pages/images/NYC.png",
        '#',
        "植被指数计算",
        "待补充",
        "Vagrant",
        "https://github.com/Marvelss",
        )
with col23:
    app("pages/images/Roadmap.png",
        '#',
        "景观指数计算",
        "待补充",
        "Landscapemetrics",
        "https://github.com/r-spatialecology/landscapemetrics",
        )
