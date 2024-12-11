import streamlit as st
import pandas as pd
import numpy as np
import leafmap.foliumap as leafmap

from streamlit import switch_page
from streamlit_tree_select import tree_select
import extra_streamlit_components as stx
import itertools
from pages import ui
# add_page_title()
# st.header('模型评估')
# st.markdown('---')
import streamlit.components.v1 as components

if 'm2' not in st.session_state:
    st.session_state.m2 = leafmap.Map(center=st.session_state.areaCenter, zoom_start=16)
colDPF1, colDPF21, colDPF22, colDPF3 = st.columns([0.2, 0.4, 0.4, 0.3])
with colDPF21:
    colDPF21col1, colDPF21col2 = st.columns([3, 10])
    with colDPF21col1:
        st.markdown("##### 原始数据")
    with colDPF21col2:
        onDP1 = st.toggle(label="自动显示对应图层-左侧", help='图层加载时间较长')

    # 初始化地图
    placeHolderDPF = st.empty()
    with placeHolderDPF:
        m1 = leafmap.Map(zoom_start=16)
        m1.add_basemap('SATELLITE')
        # m1.to_streamlit()

# dem = "https://github.com/opengeos/datasets/releases/download/raster/srtm90.tif"
dem = r'E:\a_python\program\diseaseForecastStreamlit\myproject\resource\tempdir\CHN_Wheat_2010.tif'
m = leafmap.Map(zoom_start=16)
m.add_basemap('SATELLITE')

m.add_raster(dem, cmap='RdYlGn', layer_name="DEM", nodata=0, attribution='由杭电数字农业团队提供')
m.add_colorbar(
    cmap="terrain",
    vmin=0,
    vmax=1,
    label="Elevation (m)",
    position="bottom-right",
    width=1,
    height=3,
    orientation="vertical", colors=["red", 'yellow', 'blue']
)
m.to_streamlit()


# with colDPF22:
#     colDPF21col3, colDPF21col4 = st.columns([4, 10])
#     with colDPF21col3:
#         st.markdown("##### 预处理后数据")
#     with colDPF21col4:
#         onDP2 = st.toggle(label="自动显示对应图层-右侧", help='图层加载时间较长')
#     # 初始化地图
#     placeHolderDPF2 = st.empty()
@st.fragment
def my_fragment():
    # with placeHolderDPF2:
    st.session_state.m2.to_streamlit()


# btn = st.button('添加图层')
# if btn:
#     st.session_state.m2.add_basemap('SATELLITE')
#     st.session_state.m2.to_streamlit()

# # Read file and keep in variable
# with open(r"E:\a_python\program\diseaseForecastStreamlit\mymap.html", "r") as f:
#     html_data = f.read()

## Show in webpage
# st.header("Show an external HTML")
# st.components.v1.html(html_data, height=200)

nodes1 = [
    {"label": "气象数据", "value": "气象数据"},
    {
        "label": "植保数据",
        "value": "植保数据",
        "children": [
            {"label": "feature1", "value": "sub_a"},
            {"label": "feature2", "value": "sub_b"},
            {"label": "feature3", "value": "sub_c"},
        ],
    },
    {
        "label": "地理遥感数据",
        "value": "folder_c",
        "children": [
            {"label": "晚稻移栽期", "value": "sub_d"},
            {
                "label": "预测峰值",
                "value": "sub_e",
                "children": [
                    {"label": "测报站点", "value": "sub_sub4"},
                    {"label": "生化指标", "value": "sub_s5"},
                ],
            },
            {"label": "生化指标", "value": "sub_f"},
        ],
    },
]


# import folium

# from streamlit_folium import st_folium
#
# col1, col2, col3 = st.columns([0.2, 0.9, 0.3])
# with col1:
#     st.markdown("##### 数据")
#     nodes1 = [
#         {"label": "气象数据", "value": "气象数据"},
#         {
#             "label": "植保数据",
#             "value": "植保数据",
#             "children": [
#                 {"label": "feature1", "value": "sub_a"},
#                 {"label": "feature2", "value": "sub_b"},
#                 {"label": "feature3", "value": "sub_c"},
#             ],
#         },
#         {
#             "label": "地理遥感数据",
#             "value": "folder_c",
#             "children": [
#                 {"label": "晚稻移栽期", "value": "sub_d"},
#                 {
#                     "label": "预测峰值",
#                     "value": "sub_e",
#                     "children": [
#                         {"label": "测报站点", "value": "sub_sub4"},
#                         {"label": "生化指标", "value": "sub_s5"},
#                     ],
#                 },
#                 {"label": "生化指标", "value": "sub_f"},
#             ],
#         },
#     ]
#     temp = tree_select(nodes1)
# with col2:
#     m = folium.Map(location=st.session_state.areaCenter, zoom_start=16)
#     folium.Marker(
#         st.session_state.areaCenter, popup="Liberty Bell", tooltip="Liberty Bell"
#     ).add_to(m)
#
#     # call to render Folium map in Streamlit
#     st_data = st_folium(m, width=950, height=600)
# with col3:
#     st.markdown("##### 预处理方法")
#     col12, col22 = st.columns(2)
#     with col12:
#         agree = st.checkbox('剔除异常值', key='checkbox0', args=[0])
#         agree11 = st.checkbox("空间数据重采样(待发布)", key='checkbox2', args=[2], disabled=True)
#         agree12 = st.checkbox("点面数据转化(待发布)", key='checkbox3', args=[3], disabled=True)
#     with col22:
#         agree10 = st.checkbox("缺失值插补", key='checkbox1', args=[1])
#         agree13 = st.checkbox("点面数据关联(待发布)", key='checkbox4', args=[4], disabled=True)
#     st.markdown('---')
#
#     # ===============显示和处理右中各个处理方法设置参数===============
#     if agree10:
#         # 显示缺失值信息
#         info = '缺失字段个数及占比:\n'
#         flag = False
#         # 统计缺失值信息
#         for column in pages_utils.TempDataSet[0].columns:
#             # 获取每个字段的非缺失值数量
#             non_missing_values = pages_utils.TempDataSet[0][column].count()
#             total_rows = len(pages_utils.TempDataSet[0])
#             # 计算缺失值数量
#             missing_values = total_rows - non_missing_values
#             # 计算缺失值占比
#             missing_percentage = (missing_values / total_rows) * 100
#             # 将每个字段的缺失值占比保存到信息中
#             if missing_values:
#                 info += f"* {column}:{missing_values} {missing_percentage:.2f}%\n"
#                 flag = True
#         if not flag:
#             info = '无缺失字段\n'
#             st.info(f"{info}\n", icon="ℹ️️")
#         else:
#             st.warning(f"{info}\n", icon="⚠️")
#         coll11, coll22 = st.columns([0.3, 0.6])
#         with coll11:
#             option = st.selectbox(
#                 '插补方法',
#                 options=('线性插值', '自定义'))
#             if option == '自定义':
#                 num = st.text_input('缺失值', value=np.nan)
#                 num1 = st.text_input('插补值')
#         with coll22:
#             latext = '* 公式:' + r'''
#             $$
#             y = y_0 + (y_1 - y_0) \frac{(x - x_0)}{(x_1 - x_0)}
#             $$
#             '''
#             st.info('插补方法介绍\n'
#                     '* 描述:使用缺失值前后最近的两个非缺失值填充\n' +
#                     latext, icon="ℹ️")
#         # st.markdown('---')
#     if agree:
#         coll11, coll22 = st.columns([0.3, 0.6])
#         with coll11:
#             number2 = st.text_input("剔除大于", value=0.1)
#             number3 = st.text_input("剔除小于", value=0.1)
#         with coll22:
#             st.info('剔除方法介绍\n'
#                     '* 描述:剔除最大值和最小值区域外的异常值\n', icon="ℹ️")
#
#     # =======================添加处理至任务清单=======================
#     interval_col1, interval_col2 = st.columns([1.5, 1])
#     btn = interval_col2.button('添加处理')


# center on Liberty Bell, add marker


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


@st.dialog("有效值提取", width='large')
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


# category("🗣️ 各项特征计算方法API")
# col1, col2, col3 = st.columns(3)
# with col1:
#     app("pages/images/GPTLab.png",
#         '#',
#         "降雨日数计算",
#         "基于特定时间段内降雨量和阈值及连续时长计算有效降雨日数",
#         "Vagrant",
#         "https://github.com/Marvelss",
#         )
#
# with col2:
#     app("pages/images/AskMyPDF.png",
#         '#',
#         "降水累积量计算",
#         "累加某个时间段内降雨量以计算降水累积量",
#         "Vagrant",
#         "https://github.com/Marvelss",
#         )
# with col3:
#     app("pages/images/HugChat.png",
#         '#',
#         "基于活动积温的生育期计算",
#         "基于每日累积温度达到特定积温阈值的时间即为相应生育期",
#         "孙轨迹",
#         "https://github.com/Marvelss",
#         )
# col21, col22, col23 = st.columns(3)
# with col21:
#     app("pages/images/KnowledgeGPT.png",
#         '#',
#         "时空抽取",
#         "基于特定时间段内降雨量和阈值及连续时长计算有效降雨日数",
#         "Vagrant",
#         "https://github.com/Marvelss",
#         )
#
# with col22:
#     app("pages/images/NYC.png",
#         '#',
#         "植被指数计算",
#         "累加某个时间段内降雨量以计算降水累积量",
#         "Vagrant",
#         "https://github.com/Marvelss",
#         )
# with col23:
#     app("pages/images/Roadmap.png",
#         '#',
#         "景观指数计算",
#         "基于每日累积温度达到特定积温阈值的时间即为相应生育期",
#         "Landscapemetrics",
#         "https://github.com/r-spatialecology/landscapemetrics",
#         )

# col1, col2, col3 = st.columns(3)
# with col1:
#     app(
#         "KnowledgeGPT",
#         "Make data apps to interactively explore data. In this case, check out NYC Uber pickups.",
#         "images/KnowledgeGPT.png",
#         "https://knowledgegpt.streamlit.app/",
#         "https://github.com/mmz-001/knowledge_gpt",
#     )
# with col2:
#     app(
#         "rephraise",
#         "Explore data from a CSV by uploading the CSV and converting it into an interactive dataframe.",
#         "images/rephraise.png",
#         "https://stefanrmmr-gpt3-email-generator-streamlit-app-ku3fbq.streamlit.app/",
#         "https://github.com/stefanrmmr/GPT_email_generator",
#
#     )
# with col3:
#     app(
#         "GPT-4 Auto Coder",
#         "Look at live data and compare trends. This app uses the Binance API to explore crypto data.",
#         "images/gpt-4-auto-coder.png",
#         "https://gpt4autocoder.streamlit.app/",
#         "https://github.com/echohive42/gpt4_autocoder",
#     )
#
# category("❄️ Snowflake Powered")
# col1, col2, col3 = st.columns(3)
# with col1:
#     app(
#         "CSV Snowpark Uploader",
#         "Visualize your model to debug the output. This app uses Tensorflow and GAN to generate photorealistic images.",
#         "images/SnowparkUploader.png",
#         "https://snowpark-python-loader.streamlit.app/",
#         "https://github.com/mellymel-appdev4ever/snowloader2",
#     )
# with col2:
#     app(
#         "DCR Setup Assistant",
#         "Create machine learning tools for others to use your models. This app generates images using the Deep Dream technique.",
#         "images/DCRSetup.png",
#         "https://snowflake-labs-sfquickstart-data-cle-dcr-setup-assistant-bkx7gg.streamlit.app/",
#         "demo1-deepdream",
#     )
# with col3:
#     app(
#         "Snowflake Table Catalog",
#         "Explore large datasets for input into ML models. This app displays self-driving car data and does real-time detection using YOLO.",
#         "images/SnowflakeTable.png",
#         "https://snow-table-catalog.streamlit.app/",
#         "https://github.com/mydgd/snowflake-table-catalog",
#     )
#
# category("🏆 Summit Hackathon Winners")
# col1, col2, col3 = st.columns(3)
# with col1:
#     app(
#         "First Place: snowChat",
#         "Easily collect data from users and write to a database.",
#         "images/snowChat.png",
#         "https://snowchat.streamlit.app/",
#         "https://github.com/kaarthik108/snowchat/blob/main/main.py",
#     )
# with col2:
#     app(
#         "Second Place: the Oracle of Omaha",
#         "Quickly generate a PDF file using data collected from user input.",
#         "images/Oracle.png",
#         "https://jrpettus-streamlit-buffett-buffett-app-hqw5pq.streamlit.app/",
#         "https://github.com/jrpettus/streamlit-buffett/blob/main/buffett_app.py",
#     )
# with col3:
#     app(
#         "Third Place: Instant Insight",
#         "Allow viewers of your app to collaborate via a commenting feature.",
#         "images/InstantInsight.png",
#         "https://arsentievalex-instant-insight-web-app-main-gz753r.streamlit.app/",
#         "https://github.com/arsentievalex/instant-insight-web-app/blob/main/main.py",
#     )
#
# category("📊 Other Awesome Apps")
# col1, col2, col3 = st.columns(3)
# with col1:
#     app(
#         "Fidelity Account Overview",
#         "Upload your experiment results to explore the statistical significance of an A/B test.",
#         "images/Fidelity.png",
#         "https://gerardrbentley-fidelity-account-overview-app-ezld5n.streamlit.app/",
#         "https://github.com/gerardrbentley/fidelity-account-overview/blob/main/app.py",
#     )
# with col2:
#     app(
#         "Lord of the Rings Text Generator",
#         "Upload your experiment results to explore the statistical significance of an A/B test.",
#         "images/LOTR.png",
#         "https://christian-doucette-tolkein-text-streamlit-app-mf2i7g.streamlit.app/",
#         "https://github.com/christian-doucette/tolkein_text",
#     )
# with col3:
#     app(
#         "Music through the Ages",
#         "Share data or information with others. This app pulls Streamlit's roadmap via the Notion API.",
#         "images/Music.png",
#         "https://tanul-mathur-music-through-the-ages-appfinal-g5rb85.streamlit.app/",
#         "https://github.com/tanul-mathur/music-through-the-ages",
#     )
# col1, col2, col3 = st.columns(3)
# with col1:
#     app(
#         "Roadmap",
#         "Upload your experiment results to explore the statistical significance of an A/B test.",
#         "images/Roadmap.png",
#         "https://roadmap.streamlit.app/",
#         "https://github.com/streamlit/roadmap/blob/master/streamlit_app.py",
#     )
# with col2:
#     app(
#         "Components Hub",
#         "Share data or information with others. This app pulls Streamlit's roadmap via the Notion API.",
#         "images/Components.png",
#         "https://components.streamlit.app/",
#         "https://github.com/jrieke/components-hub/blob/main/streamlit_app.py",
#     )
# with col3:
#     app(
#         "Face-GAN Explorer",
#         "Upload your experiment results to explore the statistical significance of an A/B test.",
#         "images/FaceGAN.png",
#         "https://streamlit-demo-face-gan-streamlit-app-v2nxgz.streamlit.app/",
#         "https://github.com/streamlit/demo-face-gan",
#     )
# col1, col2, col3 = st.columns(3)
# with col1:
#     app(
#         "Summit Trading Card Generator",
#         "Upload your experiment results to explore the statistical significance of an A/B test.",
#         "images/TradingCard.png",
#         "https://tradingcardapp.streamlit.app/",
#         "https://github.com/sfc-gh-tkipkemboi/trading-card-generator/blob/main/streamlit_app.py",
#     )
# with col2:
#     app(
#         "Invoice PDF Generator",
#         "Share data or information with others. This app pulls Streamlit's roadmap via the Notion API.",
#         "images/PDFGenerator.png",
#         "https://github.com/streamlit/example-app-invoice-generator",
#         "https://github.com/streamlit/example-app-pdf-report/blob/main/streamlit_app.py",
#     )
# with col3:
#     app(
#         "NYC Uber Data Explorer",
#         "Upload your experiment results to explore the statistical significance of an A/B test.",
#         "images/NYC.png",
#         "https://streamlit-demo-uber-nyc-pickups-streamlit-app-456wus.streamlit.app/",
#         "https://github.com/streamlit/demo-uber-nyc-pickups/blob/main/streamlit_app.py",
#     )
#
# st.header("🤩 Want more apps?")
# gallery_link = "https://streamlit.io/gallery"
# st.write("[Check out our app gallery!](%s)" % gallery_link)
# 模拟气温和降水数据
# def simulate_weather_data():
#     np.random.seed(42)
#     date_range = pd.date_range(start='2024-01-01', end='2024-02-20')
#     temperature = np.random.normal(loc=15, scale=5, size=len(date_range))
#     precipitation = np.random.normal(loc=5, scale=2, size=len(date_range))
#     continuous_rain_days = np.random.randint(0, 10, size=len(date_range))
#
#     data = pd.DataFrame({
#         'Date': date_range,
#         '温度': temperature,
#         'Precipitation': precipitation,
#         '01-21_01-31_降雨日数': continuous_rain_days
#     })
#     return data
#
#
# # 生成累计降水量特征
# def generate_cumulative_precipitation_features(df):
#     df['01-21_01-31_累计降水量'] = df['Precipitation'].rolling(window=11, min_periods=1).sum()
#     df['01-01_01-20_累计降水量'] = df['Precipitation'].rolling(window=20, min_periods=1).sum()
#     df['02-01_02-20_累计降水量'] = df['Precipitation'].rolling(window=20, min_periods=1).sum()
#     return df
#
#
# # 模拟气温和降水数据
# df = simulate_weather_data()
# plt.rcParams['font.sans-serif'] = 'SimHei'
#
# # 生成累计降水量特征
# df = generate_cumulative_precipitation_features(df)
#
# # 随机生成目标变量
# df['Target'] = np.random.choice([0, 1], size=len(df))
#
# # 划分特征和目标
# X = df.drop(['Date', 'Precipitation', 'Target'], axis=1)
# y = df['Target']
#
# # 使用随机森林模型拟合数据
# rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
# rf_model.fit(X, y)
#
# # 获取特征重要性
# feature_importance = rf_model.feature_importances_
#
# # 创建特征重要性数据框
# feature_importance_df = pd.DataFrame(
#     {'Feature': X.columns,
#      'Importance': feature_importance})
#
# # 排序特征重要性
# feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
#
# # 创建子图和轴
# fig, ax = plt.subplots(figsize=(10, 6))
#
# # 使用Seaborn的barplot生成特征重要性图
# sns.barplot(x='Feature', y='Importance', data=feature_importance_df, ax=ax)
#
# # 设置图形标题和轴标签
# plt.title('基于Relief-F算法的各特征因子权值排序图', fontsize=16)
# plt.xlabel('')
# plt.ylabel('特征权值')
# plt.xticks(rotation=90)
# st.pyplot(plt)

# 创建DataFrame
# df = pd.read_excel(r'E:\a_python\program\diseaseForecastStreamlit\tests\test26\2024-05-22T11-04_export.xlsx')

# 删除含有缺失值的行
# df = df.dropna()

# 去除重复值
# df = df.drop_duplicates()
# plt.rcParams['font.sans-serif'] = 'SimHei'

# 选择最多8个测报站点
# top_stations = df['测报站点'].value_counts().nlargest(8).index
# df_filtered_stations = df[df['测报站点'].isin(top_stations)]
#
# 选择最多3个年份
# top_years = df['年'].value_counts().nlargest(3).index
# df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]

# # 绘制柱状图
# plt.figure(figsize=(12, 8))
# sns.lineplot(
#     data=df_filtered,
#     x="测报站点",
#     y="移栽期",
#     hue="年",
#     marker="o"
# )
# # 设置标签和标题
# plt.xlabel("测报站点")
# plt.ylabel("移栽期")
# plt.title("部分县市不同年份移栽期", fontsize=16)
#
# st.pyplot(plt)

# # 创建DataFrame
# df = pd.read_excel(
#     r'E:\a_python\program\diseaseForecastStreamlit\tests\test26\预测病害峰值-降水累积量.xlsx')
#
# # 删除含有缺失值的行
# df = df.dropna()
#
# # 去除重复值
# df = df.drop_duplicates()
# plt.rcParams['font.sans-serif'] = 'SimHei'
#
# # 选择最多8个测报站点
# top_stations = df['测报站点'].value_counts().nlargest(8).index
# df_filtered_stations = df[df['测报站点'].isin(top_stations)]
#
# # 选择最多5个年份
# top_years = df['年'].value_counts().nlargest(5).index
# df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
#
# # 绘制柱状图
# plt.figure(figsize=(10, 6))
# sns.barplot(
#     data=df_filtered,
#     x="测报站点",
#     y="01-01_01-20_降水累积量",
#     hue="年",
#     dodge=True,
#     saturation=1
# )
# # 设置标签和标题
# plt.xlabel("测报站点")
# plt.ylabel("降水累积量")
# plt.title("部分县市不同年份01-01至01-20降水累积量")
# st.pyplot(plt)

# np.random.seed(0)
# days = np.arange(1, 31)  # 一个月的数据，1到30天
# precipitation = np.random.rand(30)  # 随机生成0到1之间的降水量
#
# # 引入一些缺失值
# precipitation[[5, 15, 18, 25]] = np.nan
#
# # 创建DataFrame
# data = pd.DataFrame({
#     'dayofyear': days,
#     'precipitation': precipitation
# })
#
# # 创建插补前的数据副本
# data_before = data.copy()
#
# # 查找缺失值的索引
# missing_indices = data[data['precipitation'].isna()].index
#
# # 定义一个函数，用于插补缺失值
# def interpolate_precipitation(series, index):
#     start = max(index - 3, 0)
#     end = min(index + 4, len(series))
#     valid_values = series[start:end].dropna()
#     if len(valid_values) > 0:
#         return valid_values.mean()
#     else:
#         return None
#
#
# # 对每个缺失值进行插补
# for index in missing_indices:
#     data.loc[index, 'precipitation'] = interpolate_precipitation(data['precipitation'], index)
# plt.rcParams['font.sans-serif'] = 'SimHei'
#
# # 绘制对比折线图
# plt.figure(figsize=(10, 6))
#
# # 绘制插补前的折线图
# plt.plot(data_before['dayofyear'], data_before['precipitation'], label='原始数据', color='black',
#          linestyle='-', marker='o')
#
# # 绘制插补后的折线图
# plt.plot(data['dayofyear'], data['precipitation'], label='插补后数据', color='blue', linestyle='--',
#          marker='o', alpha=0.3)
# plt.xlabel('Day of Year')
# plt.ylabel('降水')
# plt.title('湖南省湘阴县部分降水数据插补前后对比图', fontsize=16)
# plt.legend()
# # plt.grid(True)
# st.pyplot(plt)

# # 示例数据
# data_before = st.session_state["DPVisualInformation"][o]['before']
# data_after = st.session_state["DPVisualInformation"][o]['after']
# # 创建两个子图
# fig, axes = plt.subplots(1, 2, figsize=(12, 6))
# # 绘制处理前的箱线图
# sns.boxplot(y=data_before, ax=axes[0])
# axes[0].set_ylabel(data_before.name)
# axes[0].set_title('预处理后')
# # axes[0].axhline(max_value, color='r', linestyle='--', linewidth=1, label=f'Max Value: {max_value}')
# # axes[0].axhline(min_value, color='b', linestyle='--', linewidth=1, label=f'Min Value: {min_value}')
# # axes[0].legend(loc='upper left')
#
# # 绘制处理后的箱线图
# sns.boxplot(y=data_after, ax=axes[1])
# axes[1].set_ylabel(data_after.name)
# axes[1].set_title('预处理后')
# # axes[1].axhline(max_value, color='r', linestyle='--', linewidth=1, label=f'Max Value: {max_value}')
# # axes[1].axhline(min_value, color='b', linestyle='--', linewidth=1, label=f'Min Value: {min_value}')
# # axes[1].legend(loc='upper left')
# # 设置主标题
# fig.suptitle(f'{data_before.name}数据剔除前后对比箱型图',
#              fontsize=16)
# st.pyplot(fig)
# # temperature_data = simulate_temperature_data()

nodes2 = [
    {"label": "气象数据", "value": "气象数据"},
    {
        "label": "植保数据",
        "value": "植保数据",
        "children": [
            {"label": "feature1", "value": "sub_4"},
            {"label": "feature2", "value": "sub_3"},
            {"label": "feature3", "value": "sub_2"},
        ],
    },
    {
        "label": "地理遥感数据",
        "value": "folder_c",
        "children": [
            {"label": "晚稻移栽期", "value": "sub_d"},
            {
                "label": "预测峰值",
                "value": "sub_e",
                "children": [
                    {"label": "测报站点", "value": "sub_sub_a"},
                    {"label": "生化指标", "value": "sub_sub_b"},
                ],
            },
            {"label": "生化指标", "value": "sub_f"},
        ],
    },
]
mainIndex, tempIndex = st.columns([0.9, 0.2])
with mainIndex:
    val = stx.stepper_bar(steps=["数据集", "气象数据预处理", "特征计算", "特征优选", "模型构建"])
    st.info(f"Phase #{val}")
    if val == 1:
        switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\DataPreparation.py")
    nodes = [
        {"label": "机器学习", "value": "folder_a",
         "children": [{"label": "SVM", "value": "folder_b", },
                      {"label": "FLDA", "value": "FLDA", },
                      {"label": "KNN", "value": "KNN", }]
         },
        {"label": "统计类", "value": "folder_a1",
         "children": [{"label": "Logistic回归", "value": "folder_b1", },
                      {"label": "贝叶斯统计", "value": "FLDA1", },
                      {"label": "模糊综合评价", "value": "KNN1", }]
         },
    ]
    modelECV, modelECM, modelECR = st.columns([0.3, 0.7, 0.7])
    with modelECV:
        st.markdown("##### 数据与特征")
        st.markdown("###### 原始数据")
        # temp = tree_select(nodes)
        st.markdown('---')
        st.markdown("###### 预处理数据")
        temp1 = tree_select(nodes1)
        st.markdown('---')
        st.markdown("###### 特征")
        temp2 = tree_select(nodes2)
    with modelECM:
        # tab1, tab2 = st.tabs(["处理", " "])
        st.markdown("##### 模型评估展示")
        # with tab1:
        # colOption1, colOption2 = st.columns(2)
        # with colOption1:
        agree = st.checkbox('展示模型精度')
        # with colOption2:
        agree2 = st.checkbox('比较模型精度')
        # with colOption3:
        #     pass
        # with tab2:
        #     agree6 = st.checkbox('OA')
        #     agree7 = st.checkbox('Kappa')
        st.markdown('---')
        st.markdown("##### 参数设置")
        if agree:
            st.data_editor(['a', 'b'])
        # col1333, col2333 = st.columns([5, 1])
        # with col2333:
        #     st.button('运行')

    with modelECR:
        st.markdown('##### 结果')
        tabb1, tabb2 = st.tabs(['评价指标', '可视化'])
        with tabb1:
            st.metric("OA", "0.36", "+8%")
            # col2, col3 = st.columns(2)
            # oa = col2.metric("OA", "0.36", "+8%")
            # pa = col3.metric("Kappa", "0.5", "-8%")

        with tabb2:
            chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
            st.line_chart(chart_data)
        # with tabb3:
with tempIndex:
    st.markdown('##### 历史记录及数据下载')
    df = pd.DataFrame(
        {
            "名称": ["温度", "降雨日数", "降水"],
            "大小": ["1*3", "1*6", "1*5"],
            '处理方法': ['t检验', 'Person相关性分析', 'Person相关性分析'],
            "添加特征": [False, False, False],
        }
    )
    edited_df = st.data_editor(df)
    st.button("下载模型训练结果")
    st.button("下载模型结构和参数")
    st.button("下载模型输入参数格式")
# Add a title

# st.title("Use Pygwalker In Streamlit")
#
#
# # Get an instance of pygwalker's renderer. You should cache this instance to effectively prevent the growth of in-process memory.
# @st.cache_resource
# def get_pyg_renderer() -> "StreamlitRenderer":
#     df = pd.read_csv("https://kanaries-app.s3.ap-northeast-1.amazonaws.com/public-datasets/bike_sharing_dc.csv")
#     # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
#     return StreamlitRenderer(df, spec="./gw_config.json", debug=False)
#
#
# renderer = get_pyg_renderer()
#
# # Render your data exploration interface. Developers can use it to build charts by drag and drop.
# renderer.render_explore()
