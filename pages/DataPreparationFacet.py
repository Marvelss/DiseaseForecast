"""
@Author : SakuraFox
@Time: 2024-06-27 21:10
@File : DataPreparationFacet.py
@Description : 面状数据预处理界面
"""
import datetime

import folium
import numpy as np
import streamlit as st
from st_pages import hide_pages
from streamlit_folium import st_folium
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap

import pages_utils
from modelmethodfacet.PretreatmentMethodFacet import PretreatmentMethodFacet
from modelmethodfacet.FeatureCalculationMethodFacet import FeatureCalculationMethodFacet

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
    ]
)


# 更新左侧目标显示(可添加至pages_utils)
def updateLeftBars(raw_data_facet):
    # 初始化 leftBars 从 RawDataSetFieldFacet 获取数据
    left_bars = []
    structure = {}

    for i in range(len(raw_data_facet["编号"])):
        root = raw_data_facet["根节点"][i]
        child = raw_data_facet["子节点"][i]
        file_name1 = raw_data_facet["文件名称"][i]
        file_value = f"{file_name1}.{raw_data_facet['数据格式'][i]}"

        if root not in structure:
            structure[root] = {}

        if child not in structure[root]:
            structure[root][child] = []

        structure[root][child].append({"label": file_name1, "value": file_value})

    for root, children in structure.items():
        root_node = {"label": root, "value": root, "children": []}
        for child, files in children.items():
            child_node = {"label": child, "value": child, "children": files}
            root_node["children"].append(child_node)
        left_bars.append(root_node)

    return left_bars


checkBoxNum = 2


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '重采样'
    elif checkbox == 'checkbox1':
        return '空间插值'


# 取消其他选项按钮
def clear_other(key):
    for h in range(checkBoxNum):
        if h != key:
            st.session_state[f'checkbox{h}'] = False
    return


if "preMethodFacetName" not in st.session_state:
    st.session_state["preMethodFacetName"] = {
        'checkBox': None
    }
# 获取当前选中的方法名称
if "nowPFacetMethodName" not in st.session_state:
    st.session_state.nowPFacetMethodName = ''

col1, col2, col3 = st.columns([0.2, 0.9, 0.3])
with col1:
    st.markdown("##### 数据与特征")
    temp = tree_select(st.session_state.leftBars)
with col2:
    # 初始化地图
    placeHolderDPF = st.empty()
    with placeHolderDPF:
        m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

        # in_geojson = "https://raw.githubusercontent.com/opengeos/leafmap/master/examples/data/cable_geo.geojson"
        in_geojsonP = r'E:\a_python\program\diseaseForecastStreamlit\resource\a_test_resource\SpatiotemporalExtractionResult.json'
        in_geojsonP1 = r'E:\a_python\program\diseaseForecastStreamlit\resource\a_test_resource\test.json'
        in_geojsonP2 = r'E:\a_python\program\diseaseForecastStreamlit\resource\a_test_resource\test2.json'
        import json

        # 打开并读取JSON文件
        with open(in_geojsonP, 'r', encoding='utf-8') as file:
            in_geojson = json.load(file)
        # 打开并读取JSON文件
        with open(in_geojsonP1, 'r', encoding='utf-8') as file:
            in_geojson2 = json.load(file)
        with open(in_geojsonP2, 'r', encoding='utf-8') as file:
            in_geojson3 = json.load(file)
        # 加载json格式的矢量数据
        # m.add_geojson(in_geojson, layer_name="Cable points")
        # m.add_geojson(in_geojson2, layer_name="Cable lines")
        m.add_geojson(in_geojson3, layer_name="Cable lines")

        # 加载栅格数据
        DOY = r'E:\a_python\program\diseaseForecastStreamlit\resource\a_test_resource\DayOfYear-ActiveAccumulatedTemperature.tif'
        SET = r'E:\a_python\program\testPlatform\demo\demo111-112\T51RTP_20240303T023611_TCI_10m_NDVI.tif'
        resample = r'E:\a_python\program\testPlatform\demo\demo136\output_resample.tif'
        resampleGRA_Average = r'E:\a_python\program\testPlatform\demo\demo136\outputResampleGRA_Average.tif'
        m.add_raster(DOY, colormap="RdYlGn_r", layer_name="DOY", nodata=0)
        # m.add_raster(SET, colormap="RdYlGn_r", layer_name="NDVI", nodata=0)
        # m.add_raster(resample, colormap="RdYlGn_r", layer_name="resample", nodata=0)
        # m.add_raster(resampleGRA_Average, colormap="RdYlGn_r", layer_name="resampleGRA_Average", nodata=0)
        # m.add_shp(r'E:\a_python\program\testPlatform\demo\demo137\test3\02_05shp.shp', layer_name="point")
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
        # m.add_colormap(position=(75, 5), **params)

        # 或通过图片添加色带
        image = "https://i.imgur.com/SpmE7Cs.png"
        # m.add_image(image, position="bottomright")
        m.to_streamlit()

with col3:
    st.markdown("##### 预处理方法")
    col12, col22 = st.columns(2)
    with col12:
        # agree = st.checkbox('剔除异常值', key='checkbox0', args=[0])
        agree11 = st.checkbox("重采样(待发布)", key='checkbox0', on_change=clear_other, args=[0])
    with col22:
        agree12 = st.checkbox("空间插值(待发布)", key='checkbox1', on_change=clear_other, args=[1])
        # agree10 = st.checkbox("缺失值插补", key='checkbox1', args=[1])
        # agree13 = st.checkbox("点面数据关联(待发布)", key='checkbox4', args=[4], disabled=True)
    st.markdown('---')

    # ===============显示和处理右中各个处理方法设置参数===============
    if agree11:
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
    if agree12:
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

    FTool = PretreatmentMethodFacet()

    if btn:
        tempMethod = getCheckboxName(st.session_state.nowPFacetMethodName)
        methodParam = [value for key, value in st.session_state["preMethodFacetName"].items() if
                       key != 'checkBox']
        if tempMethod == 'a':
            with st.spinner('正在计算时空抽取,预计耗时1分半'):
                resultFilePathList = FTool.spatiotemporalExtraction(
                    methodParam)
                print(resultFilePathList)
            with placeHolderDPF:
                m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

                m.add_raster(resultFilePathList[1], colormap="RdYlGn_r", layer_name="DOY", nodata=0)
                m.add_raster(resultFilePathList[0], colormap="RdYlGn_r", layer_name="SET", nodata=0)

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

                m.to_streamlit()

        # 测试特征方法名称正确性
        for key11, value11 in st.session_state["preMethodFacetName"].items():
            pass
            # print('============测试方法参数正确性============')
            # print(f"Key: {key11}, Value: {value11}")
        new_entry = {
            "编号": pages_utils.generateID(),
            "数据类型": '气象数据',
            "根节点": '预处理后数据集',
            "子节点": 'test',
            "文件名称": 'testName',
            "数据格式": 'testFormat',
            "预处理后字段": None,
            "大小": 'testSize',
            "输入字段": None,
            "预处理方法": getCheckboxName(st.session_state["preMethodFacetName"]['checkBox']),
            "方法参数": [value for key, value in st.session_state["preMethodFacetName"].items() if
                         key != 'checkBox'],
            "时间": datetime.datetime.now().time(),
            "处理状态": False}
        print('======================预处理方法-添加任务清单记录======================')
        print(new_entry)
        # 添加到TempDataSetFieldFacet[1]
        for key in pages_utils.TempDataSetFieldFacet[1].keys():
            pages_utils.TempDataSetFieldFacet[1][key].append(new_entry[key])

        # 合并原始和预处理数据集记录
        preprocessed_data_structure = updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet)
        row_data_structure = updateLeftBars(pages_utils.RawDataSetFieldFacet)
        row_data_structure.extend(preprocessed_data_structure)
        st.session_state.leftBars = row_data_structure
        # st.session_state.leftBars = updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet)
        # 更新左侧目标显示
        # st.markdown(st.session_state.leftBars)
