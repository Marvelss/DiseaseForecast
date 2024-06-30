"""
@Author : SakuraFox
@Time: 2024-06-27 21:10
@File : DataPreparationFacet.py
@Description : 面状数据预处理界面
"""
import folium
import numpy as np
import streamlit as st
from streamlit_folium import st_folium
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap

import pages_utils

on = st.toggle("面状", help='点面数据界面切换', value=True)
if not on:
    st.switch_page('DataPreparation.py')
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
        # m.add_geojson(in_geojson, layer_name="Cable points")
        # m.add_geojson(in_geojson2, layer_name="Cable lines")

        # 加载栅格数据
    DOY = r'E:\a_python\program\diseaseForecastStreamlit\resource\a_test_resource\DayOfYear-ActiveAccumulatedTemperature.tif'
    SET = r'E:\a_python\program\diseaseForecastStreamlit\resource\a_test_resource\SpatiotemporalExtractionResult.tif'

    m.add_raster(DOY, colormap="RdYlGn_r", layer_name="DOY", nodata=0)
    m.add_raster(SET, colormap="RdYlGn_r", layer_name="SET", nodata=0)

    m.add_layer_control()

    # 图例
    # 定义图例标签和颜色（从最大值到最小值）
    # labels = ["10", "8", "6", "4", "2", "0"]
    # colors = ["#8DD3C7", "#FFFFB3", "#BEBADA", "#FB8072", "#80B1D3", "#4DAF4A"]
    #
    # m.add_legend(title="Legend", labels=labels, colors=colors)

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
    st.markdown("##### 预处理方法")
    col12, col22 = st.columns(2)
    with col12:
        agree = st.checkbox('剔除异常值', key='checkbox0', args=[0])
        agree11 = st.checkbox("空间数据重采样(待发布)", key='checkbox2', args=[2], disabled=True)
        agree12 = st.checkbox("点面数据转化(待发布)", key='checkbox3', args=[3], disabled=True)
    with col22:
        agree10 = st.checkbox("缺失值插补", key='checkbox1', args=[1])
        agree13 = st.checkbox("点面数据关联(待发布)", key='checkbox4', args=[4], disabled=True)
    st.markdown('---')

    # ===============显示和处理右中各个处理方法设置参数===============
    if agree10:
        # 显示缺失值信息
        info = '缺失字段个数及占比:\n'
        flag = False
        # 统计缺失值信息
        for column in pages_utils.TempDataSet[0].columns:
            # 获取每个字段的非缺失值数量
            non_missing_values = pages_utils.TempDataSet[0][column].count()
            total_rows = len(pages_utils.TempDataSet[0])
            # 计算缺失值数量
            missing_values = total_rows - non_missing_values
            # 计算缺失值占比
            missing_percentage = (missing_values / total_rows) * 100
            # 将每个字段的缺失值占比保存到信息中
            if missing_values:
                info += f"* {column}:{missing_values} {missing_percentage:.2f}%\n"
                flag = True
        if not flag:
            info = '无缺失字段\n'
            st.info(f"{info}\n", icon="ℹ️️")
        else:
            st.warning(f"{info}\n", icon="⚠️")
        coll11, coll22 = st.columns([0.3, 0.6])
        with coll11:
            option = st.selectbox(
                '插补方法',
                options=('线性插值', '自定义'))
            if option == '自定义':
                num = st.text_input('缺失值', value=np.nan)
                num1 = st.text_input('插补值')
        with coll22:
            latext = '* 公式:' + r'''
            $$
            y = y_0 + (y_1 - y_0) \frac{(x - x_0)}{(x_1 - x_0)}
            $$
            '''
            st.info('插补方法介绍\n'
                    '* 描述:使用缺失值前后最近的两个非缺失值填充\n' +
                    latext, icon="ℹ️")
        # st.markdown('---')
    if agree:
        coll11, coll22 = st.columns([0.3, 0.6])
        with coll11:
            number2 = st.text_input("剔除大于", value=0.1)
            number3 = st.text_input("剔除小于", value=0.1)
        with coll22:
            st.info('剔除方法介绍\n'
                    '* 描述:剔除最大值和最小值区域外的异常值\n', icon="ℹ️")

    # =======================添加处理至任务清单=======================
    interval_col1, interval_col2 = st.columns([1.5, 1])
    btn = interval_col2.button('添加处理')
