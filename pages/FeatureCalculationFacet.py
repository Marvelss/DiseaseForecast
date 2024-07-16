"""
@Author : SakuraFox
@Time: 2024-06-30 13:48
@File : FeatureCalculationFacet.py
@Description : 面状数特征计算界面
"""
import datetime

import pandas as pd
import streamlit as st
from st_pages import hide_pages
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap
import pages_utils
from modelmethodfacet.FeatureCalculationMethodFacet import FeatureCalculationMethodFacet

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


if "featureMethodFacetName" not in st.session_state:
    st.session_state["featureMethodFacetName"] = {
        'checkBox': None
    }
# 获取当前选中的方法名称
if "nowFFacetMethodName" not in st.session_state:
    st.session_state.nowFFacetMethodName = ''

checkBoxNum = 4


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '时空抽取'
    elif checkbox == 'checkbox1':
        return '植被指数计算'
    elif checkbox == 'checkbox2':
        return '景观指数计算'
    elif checkbox == 'checkbox3':
        return '空间点提取'


# 取消其他选项按钮
def clear_other(key):
    st.session_state.nowFFacetMethodName = f'checkbox{key}'
    for h in range(checkBoxNum):
        if h != key:
            st.session_state[f'checkbox{h}'] = False
    return


# 取消所有选项按钮
def clear_all():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["featureMethodFacetName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    return


colFCF1, colFCF2,  colFCF3 = st.columns([0.2,  0.7, 0.3])
with colFCF1:
    st.markdown("##### 数据与特征")
    temp = tree_select(st.session_state.leftBars)
with colFCF2:
    # 初始化地图
    pe = st.empty()
    with pe:
        m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
        m.to_streamlit()
with colFCF3:
    st.markdown("##### 特征计算方法")
    col1, col2 = st.columns(2)
    with col1:
        option21 = st.checkbox('植被指数计算(待发布)', key='checkbox1', on_change=clear_other, args=[1])
        option20 = st.checkbox('景观指数计算(待发布)', key='checkbox2', on_change=clear_other, args=[2])

    with col2:
        option18 = st.checkbox('时空抽取(待发布)', key='checkbox0', on_change=clear_other, args=[0])
        option22 = st.checkbox('空间点提取', key='checkbox3', on_change=clear_other, args=[3])

    st.markdown('---')
    # ===============显示和处理右中各个处理方法设置参数===============
    if option22:
        extractFileList = pages_utils.multiselect_all(
            st, '全选-待提取文件',
            ['遥感数据', '气象数据'],
            'tempModels', 'collapsed')
        extractValue = st.selectbox(
            '待提取字段名称',
            ('value', 'value1'))
        # 获取年和day of year
        numDate = st.date_input(label='日期')
        standardFile = st.selectbox(
            '基准文件',
            ('野外调查数据', '专业植保站调查数据'))
        extractMethod = st.selectbox(
            '提取方法',
            ('最近邻插值法', '双线性插值法', '三次样条插值法'))
    if option18:
        # 注意:温度文件名称按照实际day of year顺序排序从小到大即可
        weatherDataDir = st.selectbox(
            '选择含温度文件夹',
            ('气象数据', '植保数据', '农学数据'))
        extractDataFile = st.selectbox(
            '待抽取特征文件',
            ('待抽取特征文件.tif', 'b.tif', 'c.tif'))
        templateFile = st.selectbox(
            '模板文件',
            ('模板文件.tif', 'e.tif'))
        accumulatedTemperatureThreshold = st.number_input(
            "积温阈值温度(50-300℃)", value=50, step=50,
            min_value=50, max_value=300)
        duration = st.number_input(
            "持续时间长度(天)", value=1, min_value=1, max_value=365)
        computeMode = st.selectbox(
            '计算方式',
            ('平均值', '累计值'))
        savedFile = st.text_input(
            label='保存文件名称',
            value='spatiotemporalExtraction.tif')

        st.session_state["featureMethodFacetName"]['param1'] = str(weatherDataDir)
        st.session_state["featureMethodFacetName"]['param2'] = str(extractDataFile)
        st.session_state["featureMethodFacetName"]['param3'] = str(templateFile)
        st.session_state["featureMethodFacetName"]['param4'] = str(accumulatedTemperatureThreshold)
        st.session_state["featureMethodFacetName"]['param5'] = str(duration)
        st.session_state["featureMethodFacetName"]['param6'] = str(computeMode)
        st.session_state["featureMethodFacetName"]['param7'] = str(savedFile)

    # =======================添加处理至任务清单=======================
    interval_col1, interval_col2 = st.columns([1.5, 1])
    # btn = interval_col2.button('添加处理', on_click=clear_all)
    btn = interval_col2.button('预览并添加处理', on_click=clear_all)
    FTool = FeatureCalculationMethodFacet()

    if btn:
        tempMethod = getCheckboxName(st.session_state.nowFFacetMethodName)
        methodParam = [value for key, value in st.session_state["featureMethodFacetName"].items() if
                       key != 'checkBox']
        if tempMethod == '时空抽取':
            with st.spinner('正在计算时空抽取,预计耗时1分半'):
                resultFilePathList = FTool.spatiotemporalExtraction(
                    methodParam)
                print(resultFilePathList)
            with pe:
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
        elif tempMethod == '空间点提取':
            # 根据参数内容存入表
            # 待提取字段名称、年、DayOfYear、基准文件
            pages_utils.TempDataSetFacet[
                2] = pd.read_excel(
                r'E:\a_python\program\diseaseForecastStreamlit\resource\预测病害峰值 - 测试模型构建\2024-05-06T01-24_export.xlsx')
            st.toast("空间点提取执行完毕", icon="ℹ️️")
        # 测试特征方法名称正确性
        for key11, value11 in st.session_state["featureMethodFacetName"].items():
            pass
            # print('============测试方法参数正确性============')
            # print(f"Key: {key11}, Value: {value11}")
        new_entry = {
            "编号": pages_utils.generateID(),
            "数据类型": '气象数据',
            "根节点": '备选特征集',
            "子节点": 'test1',
            "文件名称": 'testName1' + pages_utils.generateID()[-4:],
            "数据格式": 'testFormat1',
            "备选特征": None,
            "大小": 'testSize1',
            "输入特征": None,
            "特征计算方法": getCheckboxName(st.session_state["featureMethodFacetName"]['checkBox']),
            "方法参数": [value for key, value in st.session_state["featureMethodFacetName"].items() if
                         key != 'checkBox'],
            "时间": datetime.datetime.now().time(),
            "处理状态": False}
        print('======================特征计算-添加任务清单记录======================')
        print(new_entry)

        for key in pages_utils.TempDataSetFieldFacet[2].keys():
            pages_utils.TempDataSetFieldFacet[2][key].append(new_entry[key])

        # 合并原始和预处理数据集记录

        featureCalculation_data_structure = updateLeftBars(pages_utils.FeatureDataSetFieldFacet)
        preprocessed_data_structure = updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet)
        preprocessed_data_structure.extend(featureCalculation_data_structure)

        st.session_state.leftBars = preprocessed_data_structure
        # st.session_state.leftBars = updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet)
        # 更新左侧目标显示
        # st.markdown(st.session_state.leftBars)
