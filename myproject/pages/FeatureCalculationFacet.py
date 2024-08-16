"""
@Author : SakuraFox
@Time: 2024-06-30 13:48
@File : FeatureCalculationFacet.py
@Description : 面状数特征计算界面
"""
import datetime
import os
from collections import deque

import pandas as pd
import streamlit as st
from st_pages import hide_pages
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap
from pages import pages_utils
from pages.modelmethodfacet.FeatureCalculationMethodFacet import FeatureCalculationMethodFacet

# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据",
        "数据预处理",
        "特征计算",
        "特征优选",
        "模型构建",
    ]
)

tempRP = os.path.join(os.getcwd(),
                      'resource', 'uploadFileDir')


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

# 显示地图图层,创建一个最大长度为5的队列
if 'fCMapLayer' not in st.session_state:
    st.session_state.fCMapLayer = deque(maxlen=5)


# 根据特征名称查找所有对应文件
def findFeatureFile(featureList, fileList):
    # 创建一个字典来存储特征名称及其对应的文件
    feature_files = {}

    # 遍历每个特征名称
    for feature in featureList:
        # 找出所有文件名中包含特征名称的文件
        matched_files = [file for file in fileList if feature in file]

        # 将结果存储在字典中
        feature_files[feature] = matched_files
    matched_files = [file for files in feature_files.values() for file in files]
    return matched_files


# 添加图层
def addLayer(mapTemp, filePath):
    fileName = os.path.basename(filePath)
    print('============')
    print(filePath)
    print(fileName)
    if 'tif' in fileName:
        mapTemp.add_raster(filePath,
                           layer_name=fileName.split('.')[0])
    elif 'shp' in fileName:
        mapTemp.add_shp(filePath,
                        layer_name=fileName.split('.')[0])
    elif 'json' in fileName:
        mapTemp.add_json(filePath,
                         layer_name=fileName.split('.')[0])


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


# dataframe转为json
def df_to_geojson(dfT, properties_columns, lon_column='经度', lat_column='纬度'):
    # 初始化GeoJSON字典
    geojson = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": []
    }

    # 遍历DataFrame的每一行
    for _, row in dfT.iterrows():
        feature = {
            "type": "Feature",
            "properties": {col: row[col] for col in properties_columns},
            "geometry": {
                "type": "Point",
                "coordinates": [row[lon_column], row[lat_column], 0]
            }
        }
        geojson["features"].append(feature)

    return geojson


emptyHead = st.empty()
colFCF1, colFCF2, colFCF3 = st.columns([0.2, 0.7, 0.3])
with colFCF1:
    st.markdown("##### 数据与特征")
    with st.container(height=750, border=False):
        if len(pages_utils.RawDataSetFieldFacet['编号']) == 0:
            leftBarsRawData = [{"label": "原始数据集", "value": "原始数据集"}]
        else:
            leftBarsRawData = tree_select(nodes=updateLeftBars(pages_utils.RawDataSetFieldFacet))
        if len(pages_utils.PreprocessedDataSetFieldFacet['编号']) == 0:
            leftBarsPreData = [{"label": "预处理后数据", "value": "预处理后数据"}]
        else:
            leftBarsPreData = tree_select(nodes=updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet))
        leftBarsFCalData = tree_select(nodes=updateLeftBars(pages_utils.FeatureDataSetFieldFacet))
with colFCF2:
    onFC = st.toggle(label="选中文件时自动显示对应图层", help='图层加载时间较长')
    # 初始化地图
    pe = st.empty()
    with pe:
        m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
        with st.status('加载数据中...'):
            if len(pages_utils.RawDataSetFieldFacet['编号']) != 0:
                tempList = leftBarsRawData['checked'] + leftBarsPreData['checked'] if len(leftBarsPreData) != 1 else \
                    leftBarsRawData['checked']
                for name in tempList:
                    if '.' in name and name.split('.')[0] in pages_utils.TempDataSetFieldFacet[0]['文件名称']:
                        st.session_state.fCMapLayer.append(name)
                if not onFC:
                    st.session_state.fCMapLayer.clear()
                for layer in st.session_state.fCMapLayer:
                    path = os.path.join(
                        os.getcwd(),
                        'resource',
                        'uploadFileDir', layer)
                    addLayer(m, path)
                    st.header(f'{layer}加载完成')
        m.to_streamlit()
with colFCF3:
    st.markdown("##### 特征计算方法")
    col1, col2 = st.columns(2)
    with col1:
        option21 = st.checkbox('植被指数计算', key='checkbox1', on_change=clear_other, args=[1])
        option20 = st.checkbox('景观指数计算', key='checkbox2', on_change=clear_other, args=[2])

    with col2:
        option18 = st.checkbox('时空抽取', key='checkbox0', on_change=clear_other, args=[0])
        option22 = st.checkbox('空间点提取', key='checkbox3', on_change=clear_other, args=[3])

    st.markdown('---')
    # ===============显示和处理右中各个处理方法设置参数===============
    # 处理输入文件
    unique_first_elements = set()
    tempList = leftBarsRawData['checked'] + leftBarsPreData['checked'] if len(leftBarsPreData) != 1 else \
        leftBarsRawData['checked']
    for item in tempList:
        # 分割元素并获取第一个元素
        first_element = item.split('.')[0].split('_')[0]
        # 将第一个元素添加到集合中
        unique_first_elements.add(first_element)
        # 转换集合为列表
    unique_first_elements_list = list(unique_first_elements)
    if option20:
        optionInputFile = st.selectbox(
            '输入文件',
            tempList)
        landscapemetricsPattern = st.selectbox(
            '景观水平类型',
            ('景观水平', '斑块类别水平', '斑块水平'))
        landscapemetricsFunction = st.multiselect(
            '景观水平类型',
            ('lpi', 'pd'))
        optionOutput1 = st.text_input(
            label='输出文件名称',
            value='默认')
        st.session_state["featureMethodFacetName"]['param1'] = optionInputFile
        st.session_state["featureMethodFacetName"]['param2'] = landscapemetricsPattern
        st.session_state["featureMethodFacetName"]['param3'] = str(landscapemetricsFunction)
        st.session_state["featureMethodFacetName"]['param4'] = optionOutput1

    if option21:
        optionVegetationIndex = st.selectbox(
            '植被指数',
            ('NDVI', 'EVI'))
        optionInputFile = st.selectbox(
            '输入文件',
            tempList)
        optionRed = st.number_input(label='红波段对应的波段数', value=3)
        optionNir = st.number_input(label='近红波段对应的波段数', value=2)
        optionOutput = st.text_input(
            label='输出文件名称',
            value=optionInputFile)

        st.session_state["featureMethodFacetName"]['param1'] = optionVegetationIndex
        st.session_state["featureMethodFacetName"]['param2'] = os.path.join(tempRP, optionInputFile)
        st.session_state["featureMethodFacetName"]['param3'] = optionRed
        st.session_state["featureMethodFacetName"]['param4'] = optionNir
        st.session_state["featureMethodFacetName"]['param5'] = os.path.join(tempRP, optionOutput)

    if option22:
        shp_files = [item for item in leftBarsRawData['checked'] if item.endswith('.shp')]
        extractFileList = pages_utils.multiselect_all(
            st, '全选-待提取特征文件',
            shp_files + leftBarsFCalData['checked'],
            'tempModels', 'collapsed')
        # 获取年和day of year
        # numDate = st.date_input(label='日期')
        # 过滤以 .shp 结尾的元素
        standardFile = st.selectbox(
            '基准文件',
            options=shp_files
        )
        extractMethod = st.selectbox(
            '提取方法',
            ('最近邻插值法', '双线性插值法'))
        # 联合特征计算表格放入methodParam
        # methodParam[4]
        # print(extractFileList)
        if extractFileList:
            for temp in extractFileList:
                tempPath = os.path.join(
                    os.getcwd(),
                    'resource',
                    'uploadFileDir', temp)
                st.session_state.fCMapLayer.append(tempPath)
        with pe:
            mapTemp1 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
            with st.status('加载数据中...'):
                for layerTemp in st.session_state.fCMapLayer:
                    addLayer(mapTemp1, layerTemp)
            mapTemp1.to_streamlit()

        if standardFile:
            tempPath = os.path.join(
                os.getcwd(),
                'resource',
                'uploadFileDir', standardFile)
            st.session_state.fCMapLayer.append(tempPath)
            # 可读取数据格式: excel, csv, shp, geojson
            # 读取含经纬度excel表格
            with pe:
                mapTemp2 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
                with st.status('加载数据中...'):
                    for layerTemp in st.session_state.fCMapLayer:
                        addLayer(mapTemp2, layerTemp)
                mapTemp2.to_streamlit()
            st.session_state["featureMethodFacetName"]['param1'] = str(extractFileList)
            st.session_state["featureMethodFacetName"]['param2'] = str(standardFile)
            st.session_state["featureMethodFacetName"]['param3'] = str(extractMethod)
            st.session_state["featureMethodFacetName"]['param4'] = 'spatialPointFile.xlsx'
    if option18:
        # 注意:温度文件名称按照实际day of year顺序排序从小到大即可
        weatherDataDir = st.selectbox(
            '选择温度文件',
            unique_first_elements_list,
            help='以特征名称筛选选中所以文件')
        extractDataFile = st.multiselect(
            '待抽取特征文件',
            unique_first_elements_list,
            help='以特征名称筛选选中所以文件')
        templateFile = st.selectbox(
            '模板文件',
            ('模板文件.tif', 'e.tif'),
            help='默认取各特征第一个时间文件作为模板用于输出结果')
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
            help='每个特征计算结果文件名称格式为:特征+年份',
            placeholder='LAI_2016_SEResult.tif')

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
        # print(f'=====测试跳过处理=====\n{pages_utils.TempDataSetFieldFacet[1]}')
        tempMethod = getCheckboxName(st.session_state.nowFFacetMethodName)
        methodParam = [value for key, value in st.session_state["featureMethodFacetName"].items() if
                       key != 'checkBox']
        handledFile = None
        fcTool = FeatureCalculationMethodFacet()
        if tempMethod == '时空抽取':
            with emptyHead:
                with st.spinner('正在计算时空抽取,预计耗时1分半'):
                    paramT = [value for key, value in st.session_state["featureMethodFacetName"].items() if
                              key != 'checkBox']
                    # print(f'========测试参数======={paramT}')
                    resultFilePathList = FeatureCalculationMethodFacet().spatiotemporalExtraction(tempList, paramT)
                    handledFile = resultFilePathList
                    # 添加记录时该处需要修改
                    # handledFile = ' '.join()
                    for tempH in resultFilePathList:
                        st.session_state.fCMapLayer.append(tempH)

        elif tempMethod == '植被指数计算':
            resultFilePathList = fcTool.onNDVI(methodParam)
            handledFile = resultFilePathList
            st.session_state.fCMapLayer.append(handledFile)

        elif tempMethod == '景观指数计算':
            resultFilePathList = fcTool.onLandscapeIndex(methodParam)
            handledFile = resultFilePathList
            for tempH in resultFilePathList:
                st.session_state.fCMapLayer.append(tempH)

        elif tempMethod == '空间点提取':
            with emptyHead:
                with st.spinner('正在进行空间点提取'):
                    handledFile = FeatureCalculationMethodFacet().onSpatialPointExtract(
                        methodParam)
                    # 根据参数内容存入表
                    # 待提取字段名称、年、DayOfYear、基准文件
                    # st.session_state.fCMapLayer.append(handledFile)

                    pages_utils.TempDataSetFacet[2] = pd.read_excel(handledFile)
                    print('----------------特征优选数据集----------------')
                    print(pages_utils.TempDataSetFacet[2])
            st.toast("空间点提取执行完毕", icon="ℹ️️")

        with pe:
            afterPreMap = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
            with st.status('加载数据中...'):
                if len(pages_utils.RawDataSetFieldFacet['编号']) != 0:
                    for name in leftBarsFCalData['checked']:
                        if '.' in name and name.split('.')[0] in pages_utils.TempDataSetFieldFacet[0]['文件名称']:
                            st.session_state.dPLeftMapLayer.append(name)
                    # print(st.session_state.fCMapLayer)
                for layerPath in st.session_state.fCMapLayer:
                    addLayer(afterPreMap, layerPath)
                    st.header(f'{layerPath}加载完成')
            afterPreMap.to_streamlit()

        # 若返回值为数组
        if isinstance(handledFile, list):
            for tempEntry in handledFile:
                tempEntryT = os.path.basename(tempEntry)
                new_entry = {
                    "编号": pages_utils.generateID(),
                    "数据类型": '气象数据',
                    "根节点": '备选特征集',
                    "子节点": '气象数据',
                    "文件名称": tempEntryT.split('.')[0],
                    "数据格式": tempEntryT.split('.')[1],
                    "输入文件": None,
                    "特征计算方法": tempMethod,
                    "方法参数": [value for key, value in st.session_state["featureMethodFacetName"].items() if
                                 key != 'checkBox'],
                    "时间": datetime.datetime.now().time(),
                    "处理状态": False}
                print('======================特征计算-添加任务清单记录======================')
                print(new_entry)

                for key in pages_utils.TempDataSetFieldFacet[2].keys():
                    pages_utils.TempDataSetFieldFacet[2][key].append(new_entry[key])

        else:
            tempEntryT = os.path.basename(handledFile)
            new_entry = {
                "编号": pages_utils.generateID(),
                "数据类型": '气象数据',
                "根节点": '备选特征集',
                "子节点": '气象数据',
                "文件名称": tempEntryT.split('.')[0],
                "数据格式": tempEntryT.split('.')[1],
                "输入文件": None,
                "特征计算方法": tempMethod,
                "方法参数": [value for key, value in st.session_state["featureMethodFacetName"].items() if
                             key != 'checkBox'],
                "时间": datetime.datetime.now().time(),
                "处理状态": False}
            print('======================特征计算-添加任务清单记录======================')
            print(new_entry)

            for key in pages_utils.TempDataSetFieldFacet[2].keys():
                pages_utils.TempDataSetFieldFacet[2][key].append(new_entry[key])

        # 合并原始和预处理数据集记录

        # featureCalculation_data_structure = updateLeftBars(pages_utils.FeatureDataSetFieldFacet)
        # preprocessed_data_structure = updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet)
        # preprocessed_data_structure.extend(featureCalculation_data_structure)
        #
        # st.session_state.leftBars = preprocessed_data_structure
        # st.session_state.leftBars = updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet)
        # 更新左侧目标显示
        # st.markdown(st.session_state.leftBars)
