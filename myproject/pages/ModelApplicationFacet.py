import os.path

import joblib
import streamlit as st
import leafmap.foliumap as leafmap

import pandas as pd
from st_pages import hide_pages

from lib.share import RESOURCE_MODELRESULT_PATH, RESOURCE_IMAGES_PATH
from pages import pages_utils

st.set_page_config(
    layout="wide"
)
# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据",
        "数据预处理",
        "特征计算",
        "特征优选",
        "模型构建",
        "基于天气情景生成器的模型评价",
        "模型应用",
        "建模报告",
        "数据下载中心",
    ]
)

st.markdown('')

st.markdown('')
st.markdown('')

st.markdown('')
st.header('模型应用')
# st.markdown(
#     """
#     <style>
#     h2 {
#         margin-top: -100px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )
# st.header('多场景作物病虫害快速预测建模系统')
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
colTemp1, colTemp2, colTemp3 = st.columns([0.1, 0.8, 0.1])
with colTemp1:
    pass
with colTemp3:
    pass
with colTemp2:
    col2, col3 = st.columns(2)
    with col2:
        st.markdown("##### 加载模型")
        st.selectbox('加载模型',
                     options=['茶树炭疽病预测模型', '水稻纹枯病SEIR机理模型', '水稻稻瘟病峰值模型', '苹果斑点落叶病预测模型'],
                     label_visibility='collapsed')
        modelDF = pages_utils.TempDataSetField[4]
        # models = modelDF["特征"].tolist()
        models = [1]

        for tempModel in models:
            # model = joblib.load(
            #     os.path.join(RESOURCE_MODELRESULT_PATH, 'structure',
            #                  f'{tempModel}_structure.pkl'))
            model = joblib.load(
                os.path.join(RESOURCE_MODELRESULT_PATH, 'structure',
                             'FLDA_structure.pkl'))

        # 获取特征字段
        feature_names = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else None
        # st.info(f"模型输入特征:{' '.join(feature_names)}")
        st.info(
            f"模型输入特征:3月上旬温度、4月上旬温度、5月上旬温度、6月上旬温度、3月上旬湿度、  \n4月上旬湿度、5月中旬湿度、5月中旬温度、6月中旬温度、6月中旬湿度、6月下旬湿度",
            icon="ℹ️️")

    with col3:
        st.markdown("##### 输入特征")
        uploaded_dataSet = st.file_uploader(
            "输入原始字段",
            accept_multiple_files=False,
            label_visibility='collapsed')
    pl = st.empty()
    with pl:
        map1 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
        map1.add_basemap('SATELLITE')
        map1.to_streamlit()
    if uploaded_dataSet:
        # bytes_data = uploaded_dataSet.read()
        # predictDF = pd.read_excel(bytes_data)
        # predictions = model.predict(predictDF)
        # predictDF['预测结果'] = predictions
        # st.table(predictDF)
        with pl:
            map1 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
            # map1 = leafmap.Map()
            map1.add_shp(
                r'F:\A_postgraduate\病虫害多场景系统\a_系统测试\系统测试数据集\存档\面-静-茶树炭疽病面状(发生程度)-存档\病害分布清洗后问卷-总\清洗后All.shp',
                layer_name='预测病株率')
            map1.add_basemap('SATELLITE')
            import leafmap.colormaps as cm

            # map1.add_raster(r'E:\a_python\program\testPlatform\demo\demo114\Result33.tif',layer_name='predictResult')
            labels = ['0', '1-2', '3']
            colors = ['#4a90e2', '#7ed321', '#FF5500']
            field = ["SLOPE"],
            # filepath = "https://raw.githubusercontent.com/opengeos/leafmap/master/examples/data/us_cities.csv"
            # filepath = r'E:\a_python\program\diseaseForecastStreamlit\testscene\a_test_resource\SpatiotemporalExtractionResult.json'
            # map1.add_legend(title='PredictDiseaseGrade', labels=labels, colors=colors)
            # m.add_colormap(gdf, column="SLOPE", colors=colors,layer_name="SLOPE" )
            # cm.plot_colormap(colors=cm.palettes.dem, axis_off=True)
            # cm.plot_colormap(
            #     "terrain",
            #     label="Elevation",
            #     width=8.0,
            #     height=0.4,
            #     orientation="horizontal",
            #     vmin=0,
            #     vmax=1000,
            # )
            filepath = r'E:\a_python\program\diseaseForecastStreamlit\myproject\resource\modelTest.csv'
            map1.add_heatmap(
                filepath,
                latitude="latitude",
                longitude="longitude",
                value="disease",
                name="Heat map",
                radius=30,
            )
            map1.to_streamlit()
