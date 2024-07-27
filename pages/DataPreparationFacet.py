"""
@Author : SakuraFox
@Time: 2024-06-27 21:10
@File : DataPreparationFacet.py
@Description : 面状数据预处理界面
"""
import datetime
import os
from collections import deque
import streamlit as st
from st_pages import hide_pages
from streamlit_tree_select import tree_select
import leafmap.foliumap as leafmap

import pages_utils
from modelmethodfacet.PretreatmentMethodFacet import PretreatmentMethodFacet

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
if 'dPmap' not in st.session_state:
    st.session_state.dPmap = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)

# 显示地图图层,创建一个最大长度为5的队列
if 'dPLeftMapLayer' not in st.session_state:
    st.session_state.dPLeftMapLayer = deque(maxlen=5)
# 显示右侧预处理地图图层,创建一个最大长度为5的队列
if 'dPRightMapLayer' not in st.session_state:
    st.session_state.dPRightMapLayer = deque(maxlen=5)


# 添加图层
def addLayer(mapTemp, filePath):
    fileName = os.path.basename(filePath)
    if 'tif' in fileName:
        mapTemp.add_raster(filePath,
                           layer_name=fileName.split('.')[0])
    elif 'shp' in fileName:
        mapTemp.add_shp(filePath,
                    layer_name=fileName.split('.')[0])
    elif 'json' in fileName:
        mapTemp.add_json(filePath,
                         layer_name=fileName.split('.')[0])


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
    st.session_state.nowPFacetMethodName = f'checkbox{key}'
    for h in range(checkBoxNum):
        if h != key:
            st.session_state[f'checkbox{h}'] = False
    return


def find_parent_value(data, targetValue):
    for item in data:
        if 'children' in item:
            for child in item['children']:
                if child['value'] == targetValue:
                    return item['value']
            parentValue = find_parent_value(item['children'], targetValue)
            if parentValue:
                return parentValue
    return None


if "preMethodFacetName" not in st.session_state:
    st.session_state["preMethodFacetName"] = {
        'checkBox': None
    }
# 获取当前选中的方法名称
if "nowPFacetMethodName" not in st.session_state:
    st.session_state.nowPFacetMethodName = ''

emptyHead = st.empty()
colDPF1, colDPF21, colDPF22, colDPF3 = st.columns([0.2, 0.7, 0.7, 0.3])
with colDPF1:
    st.markdown("##### 数据与特征")
    with st.container(height=750, border=False):
        leftBarsRawData = tree_select(nodes=updateLeftBars(pages_utils.RawDataSetFieldFacet))
        leftBarsPreData = tree_select(nodes=updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet))

with colDPF21:
    st.markdown("##### 原始数据集")
    # 初始化地图
    placeHolderDPF = st.empty()
    with placeHolderDPF:
        m1 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
        with st.status('加载数据中...'):
            for name in leftBarsRawData['checked']:
                if '.' in name and name.split('.')[0] in pages_utils.TempDataSetFieldFacet[0]['文件名称']:
                    st.session_state.dPLeftMapLayer.append(name)
            print(st.session_state.dPLeftMapLayer)
            for layer in st.session_state.dPLeftMapLayer:
                path = os.path.join(
                    os.getcwd(),
                    'resource',
                    'uploadFileDir', layer)
                addLayer(m1, path)
                st.header(f'{layer}加载完成')
        m1.to_streamlit()
with colDPF22:
    st.markdown("##### 预处理后数据")
    # 初始化地图
    placeHolderDPF2 = st.empty()
    with placeHolderDPF2:
        # st.session_state.dPmap = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
        # with st.status('加载数据中...'):
        #     for name in temp['checked']:
        #         if '.' in name and name.split('.')[0] in pages_utils.TempDataSetFieldFacet[1]['文件名称']:
        #             path = os.path.join(
        #                 os.getcwd(),
        #                 'resource',
        #                 'uploadFileDir', name)
        #             print('=============')
        #             print(path)
        #             # m1.add_raster(path, layer_name=name.split('.')[0])
        #             m2.add_shp(path, layer_name=name.split('.')[0])
        #             st.header(f'{name}加载完成')
        st.session_state.dPmap.to_streamlit()
with colDPF3:
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
        # if not flag:
        #     info = '无缺失字段\n'
        #     st.info(f"{info}\n", icon="ℹ️️")
        # else:
        #     st.warning(f"{info}\n", icon="⚠️")
        # coll11, coll22 = st.columns([0.3, 0.6])
        # with coll11:
        #     option = st.selectbox(
        #         '插补方法',
        #         options=('线性插值', '自定义'))
        #     if option == '自定义':
        #         num = st.text_input('缺失值', value=np.nan)
        #         num1 = st.text_input('插补值')
        # with coll22:
        #     latext = '* 公式:' + r'''
        #     $$
        #     y = y_0 + (y_1 - y_0) \frac{(x - x_0)}{(x_1 - x_0)}
        #     $$
        #     '''
        #     st.info('插补方法介绍\n'
        #             '* 描述:使用缺失值前后最近的两个非缺失值填充\n' +
        #             latext, icon="ℹ️")
        # st.markdown('---')
    if agree12:
        option = st.selectbox(
            '点数据',
            options=('02_05', '自定义'))
        textAN = st.text_input(
            label='点属性字段名称',
            placeholder='value',
            help='可在arcgis中查看属性表获取')
        optionIM = st.selectbox(
            '插值方法',
            options=('反距离权重法', '克里金插值'))
        textLL = st.text_input(
            label='经纬度范围',
            placeholder='118.053 31.086 121.953 27.286',  # 可在原始数据时规定范围,在这默认输入
            help='经纬度按左边 底部 右边 顶部顺序且空格分隔填入')
        textSN = st.text_input(
            label='保存输出文件名称',
            value='02_05_预处理.tif')

    # =======================添加处理至任务清单=======================
    interval_col1, interval_col2 = st.columns([1.5, 1])
    btn = interval_col2.button('添加或跳过处理')

    FTool = PretreatmentMethodFacet()

    if btn:
        tempMethod = getCheckboxName(st.session_state.nowPFacetMethodName)
        # print(f'========测试方法名========{tempMethod}')
        # # 暂时默认传递
        # pages_utils.PreprocessedDataSetFieldFacet = pages_utils.RawDataSetFieldFacet
        # print(f'=====预处理界面-测试跳过处理=====\n{pages_utils.PreprocessedDataSetFieldFacet}')

        # 若为空则跳过该步骤
        if tempMethod is None:
            pass
        else:
            methodParam = [value for key, value in st.session_state["preMethodFacetName"].items() if
                           key != 'checkBox']
            handledFile = None
            if tempMethod == '空间插值':
                with emptyHead:
                    # for _ in stqdm(range(5), desc="This is a slow task", mininterval=1):
                    #     time.sleep(0.5)
                    with st.spinner('数据处理中...'):
                        # time.sleep(5)
                        methodParam = [
                            '02_05.shp',
                            'atemp',
                            '反距离权重法',
                            '118.053330 31.086861 121.953330 27.286861',
                            '02_05_预处理.tif']
                        handledFile = FTool.spatialInterpolation(methodParam)
                        st.session_state.dPRightMapLayer.append(handledFile)
                    st.toast("空间插值完毕", icon="ℹ️️")
            elif tempMethod == '重采样':
                handledFile = '源文件名-重采样_2010_' + pages_utils.generateID()[:3] + '.tif'
                methodParam = [
                    '02_05.shp',
                    'atemp',
                    '反距离权重法',
                    '118.053330 31.086861 121.953330 27.286861',
                    '02_05_预处理.tif']
                # handledFile = FTool.spatialInterpolation(methodParam)
                st.session_state.dPRightMapLayer.append(handledFile)
            with placeHolderDPF2:
                with st.status('加载数据中...'):
                    afterPreMap = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
                    for layerPath in st.session_state.dPRightMapLayer:
                        addLayer(afterPreMap, layerPath)
                        st.header(f'{layerPath}加载完成')
                afterPreMap.to_streamlit()
            new_entry = {
                "编号": pages_utils.generateID(),
                "数据类型": '气象数据',
                "根节点": '预处理后数据集',
                "子节点": '气象数据',
                "文件名称": handledFile.split('.')[0],
                "数据格式": handledFile.split('.')[1],
                "输入文件": None,
                "预处理方法": tempMethod,
                "方法参数": [value for key, value in st.session_state["preMethodFacetName"].items() if
                             key != 'checkBox'],
                "时间": datetime.datetime.now().time(),
                "处理状态": True}
            print('======================预处理方法-添加任务清单记录======================')
            print(new_entry)
            # 添加到TempDataSetFieldFacet[1]
            for key in pages_utils.TempDataSetFieldFacet[1].keys():
                pages_utils.TempDataSetFieldFacet[1][key].append(new_entry[key])
