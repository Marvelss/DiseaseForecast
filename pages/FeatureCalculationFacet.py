"""
@Author : SakuraFox
@Time: 2024-06-30 13:48
@File : FeatureCalculationFacet.py
@Description : 面状数特征计算界面
"""
import streamlit as st
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap

checkBoxNum = 3


# 取消其他选项按钮
def clear_other(key):
    for h in range(checkBoxNum):
        if h != key:
            st.session_state[f'checkbox{h}'] = False
    return


on = st.toggle("面状", help='点面数据界面切换', value=True)
if not on:
    st.switch_page('FeatureCalculation.py')
col1, col2, col3 = st.columns([0.2, 0.9, 0.3])
with col1:
    st.markdown("##### 数据与特征")
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
            "label": "农学数据",
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
    temp = tree_select(nodes1)
with col2:
    # 初始化地图
    m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

    # in_geojson = "https://raw.githubusercontent.com/opengeos/leafmap/master/examples/data/cable_geo.geojson"
    in_geojsonP = r'E:\a_python\program\diseaseForecastStreamlit\resource\a_test_resource\SpatiotemporalExtractionResult.json'
    in_geojsonP1 = r'E:\a_python\program\diseaseForecastStreamlit\resource\a_test_resource\test.json'
    import json

    # 打开并读取JSON文件
    with open(in_geojsonP, 'r', encoding='utf-8') as file:
        in_geojson = json.load(file)
    # 打开并读取JSON文件
    with open(in_geojsonP1, 'r', encoding='utf-8') as file:
        in_geojson2 = json.load(file)

        # 加载json格式的矢量数据
    m.add_geojson(in_geojson, layer_name="Cable points")
    m.add_geojson(in_geojson2, layer_name="Cable lines")

    m.add_layer_control()

    params = {
        "width": 2,
        "height": 0.3,
        "vmin": 0,
        "vmax": 100,
        "cmap": "terrain",
        "label": "Elevation (m)",
        "orientation": "horizontal",
        "transparent": True,
    }
    m.add_colormap(position=(75, 5), **params)

    # 或通过图片添加色带
    image = "https://i.imgur.com/SpmE7Cs.png"
    # m.add_image(image, position="bottomright")
    m.to_streamlit()

with col3:
    st.markdown("##### 特征计算方法")
    col1, col2 = st.columns(2)
    with col1:
        option21 = st.checkbox('植被指数计算(待发布)', key='checkbox5', on_change=clear_other, args=[5])
    with col2:
        option18 = st.checkbox('时空抽取(待发布)', key='checkbox4', on_change=clear_other, args=[4])
        option20 = st.checkbox('景观指数计算(待发布)', key='checkbox6', on_change=clear_other, args=[6])
    st.markdown('---')
    # ===============显示和处理右中各个处理方法设置参数===============
    if option18:
        growthPeriod = st.selectbox(
            '选择文件',
            ('a.tif', 'b.tif', 'c.tif'))
    # =======================添加处理至任务清单=======================
    interval_col1, interval_col2 = st.columns([1.5, 1])
    btn = interval_col2.button('添加处理')
