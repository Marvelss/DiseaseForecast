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

from lib.share import RESOURCE_TEMPLATE_PATH, RESOURCE_TEMPDIR_PATH
from pages import pages_utils
from pages.modelmethodfacet.PretreatmentMethodFacet import PretreatmentMethodFacet

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
        "建模报告",
        "模型应用",
        "数据下载中心",
    ]
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

# 显示地图图层,创建一个最大长度为5的队列
if 'dPLeftMapLayer' not in st.session_state:
    st.session_state.dPLeftMapLayer = deque(maxlen=2)
# 显示右侧预处理地图图层,创建一个最大长度为5的队列
if 'dPRightMapLayer' not in st.session_state:
    st.session_state.dPRightMapLayer = deque(maxlen=1)
# 资源路径
tempRP = RESOURCE_TEMPDIR_PATH


# 添加图层
def addLayer(mapTemp, filePath):
    fileNameT = os.path.basename(filePath)
    if 'tif' in fileNameT:
        mapTemp.add_raster(filePath,
                           layer_name=fileNameT.split('.')[0])
    elif 'shp' in fileNameT:
        mapTemp.add_shp(filePath,
                        layer_name=fileNameT.split('.')[0])
    elif 'json' in fileNameT:
        mapTemp.add_json(filePath,
                         layer_name=fileNameT.split('.')[0])


checkBoxNum = 3


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '重采样'
    elif checkbox == 'checkbox1':
        return '空间插值'
    elif checkbox == 'checkbox2':
        return '裁剪'


# 取消其他选项按钮
def clear_other(key):
    st.session_state.nowPFacetMethodName = f'checkbox{key}'
    for h in range(checkBoxNum):
        if h != key:
            st.session_state[f'checkbox{h}'] = False
    return


def find_subnodes(file_dict, file_name):
    # 检查文件名称是否在字典中
    if file_name in file_dict["文件名称"]:
        # 获取对应的下标
        index = file_dict["文件名称"].index(file_name)
        # 返回对应的子节点
        print(file_dict["子节点"][index])
        return file_dict["子节点"][index]
    else:
        return None  # 如果文件名称不存在


def find_parent_value(data, targetValue):
    for item in data:
        if 'children' in item:
            for child in item['children']:
                if child['value'] == targetValue:
                    return item['value']
            parentValue = find_parent_value(item['children'], targetValue)
            if parentValue:
                return parentValue


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
        if len(pages_utils.RawDataSetFieldFacet['编号']) == 0:
            leftBarsRawData = [{"label": "原始数据集", "value": "原始数据集"}]
        else:
            leftBarsRawData = tree_select(nodes=pages_utils.updateLeftBars(pages_utils.RawDataSetFieldFacet))
        leftBarsPreData = tree_select(nodes=pages_utils.updateLeftBars(pages_utils.PreprocessedDataSetFieldFacet))

with colDPF21:
    colDPF21col1, colDPF21col2 = st.columns([3, 10])
    with colDPF21col1:
        st.markdown("##### 原始数据")
    with colDPF21col2:
        onDP1 = st.toggle(label="选中文件时自动显示对应图层-左侧", help='图层加载时间较长')

    # 初始化地图
    placeHolderDPF = st.empty()
    with placeHolderDPF:
        m1 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
        with st.status('加载数据中...'):
            if len(pages_utils.RawDataSetFieldFacet['编号']) != 0:
                for name in leftBarsRawData['checked'] + leftBarsPreData['checked']:
                    if '.' in name and name.split('.')[0] in pages_utils.TempDataSetFieldFacet[0]['文件名称'] or \
                            name.split('.')[0] in pages_utils.TempDataSetFieldFacet[1]['文件名称']:
                        st.session_state.dPLeftMapLayer.append(name)
                print(st.session_state.dPLeftMapLayer)
                if not onDP1:
                    st.session_state.dPLeftMapLayer.clear()
                for layer in st.session_state.dPLeftMapLayer:
                    path = os.path.join(RESOURCE_TEMPDIR_PATH, layer)
                    addLayer(m1, path)
                    st.header(f'{layer}加载完成')
        m1.to_streamlit()
with colDPF22:
    colDPF21col3, colDPF21col4 = st.columns([4, 10])
    with colDPF21col3:
        st.markdown("##### 预处理后数据")
    with colDPF21col4:
        onDP2 = st.toggle(label="自动显示对应图层-右侧", help='图层加载时间较长')
    # 初始化地图
    placeHolderDPF2 = st.empty()
    with placeHolderDPF2:
        m2 = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
        m2.to_streamlit()
with colDPF3:
    st.markdown("##### 预处理方法")
    col12, col22 = st.columns(2)
    with col12:
        agree11 = st.checkbox("重采样", key='checkbox0', on_change=clear_other, args=[0])
        agree12 = st.checkbox("空间插值", key='checkbox1', on_change=clear_other, args=[1])
    with col22:
        agree13 = st.checkbox("裁剪", key='checkbox2', on_change=clear_other, args=[2])

    st.markdown('---')

    # ===============显示和处理右中各个处理方法设置参数===============
    if agree11:
        onlyFile = []
        for temp in leftBarsRawData['checked'] + leftBarsPreData['checked']:
            if '.tif' in temp:
                onlyFile.append(temp)
        optionResample = st.selectbox(
            '待重采样文件',
            options=onlyFile)
        optionInterpolationMethod = st.selectbox(
            '重采样方法',
            options=('最近邻插值', '双线性插值', '立方卷积逼近',
                     '三次样条线逼近', '均值', '众数'))
        optionTemplateFile = st.selectbox(
            '模板文件',
            options=(leftBarsRawData['checked']),
            help='参考坐标系及投影数等')
        tempName = '文件名称_年_DOY.tif'
        if '_' in optionResample:
            tempName = optionResample.split('_')
        optionOutputFile = st.text_input(
            label='输出文件名称',
            value=f'{tempName[0]}-重采样_{tempName[1]}_{tempName[2]}')

        st.session_state["preMethodFacetName"]['param1'] = os.path.join(tempRP, optionResample)
        st.session_state["preMethodFacetName"]['param2'] = optionInterpolationMethod
        st.session_state["preMethodFacetName"]['param3'] = os.path.join(tempRP, optionTemplateFile)
        st.session_state["preMethodFacetName"]['param4'] = os.path.join(tempRP, optionOutputFile)

    if agree12:
        optionPoint = st.selectbox(
            '点数据',
            options=(leftBarsRawData['checked']))
        textAN = st.text_input(
            label='点属性字段名称',
            placeholder='value',
            help='可在arcgis中查看属性表获取')
        optionIM = st.selectbox(
            '插值方法',
            options=('反距离权重法', '克里金插值'))
        if optionIM == '克里金插值':
            templateFile = st.selectbox(
                '模板文件(.tif)',
                options=(leftBarsRawData['checked']))
        textLL = st.text_input(
            label='经纬度范围',
            placeholder='118.053 31.086 121.953 27.286',  # 可在原始数据时规定范围,在这默认输入
            help='经纬度按左边 底部 右边 顶部顺序且空格分隔填入')
        textSN = st.text_input(
            label='保存输出文件名称',
            value='02_05_预处理.tif')
        if textSN:
            st.session_state["preMethodFacetName"]['param1'] = os.path.join(tempRP, optionPoint)
            st.session_state["preMethodFacetName"]['param2'] = textAN
            st.session_state["preMethodFacetName"]['param3'] = optionIM
            st.session_state["preMethodFacetName"]['param4'] = textLL
            st.session_state["preMethodFacetName"]['param5'] = os.path.join(tempRP, textSN)
            st.session_state["preMethodFacetName"]['param6'] = os.path.join(tempRP, templateFile)
    if agree13:
        temp13List = []
        temp13 = leftBarsRawData['checked']
        for tep in temp13:
            if tep.endswith('tif'):
                temp13List.append(tep)
        optionClip = st.selectbox(
            '待裁剪文件',
            options=temp13List)
        optionTemplateFileClip = st.selectbox(
            '模板文件',
            options=(leftBarsRawData['checked']),
            help='参考坐标系及投影数等')
        tempName1 = optionClip.split('_')
        optionOutputFileClip = st.text_input(
            label='输出文件名称',
            value=f'{tempName1[0]}-裁剪_{tempName1[1]}_{tempName1[2]}')

        st.session_state["preMethodFacetName"]['param1'] = os.path.join(tempRP, optionClip)
        st.session_state["preMethodFacetName"]['param2'] = os.path.join(tempRP, optionTemplateFileClip)
        st.session_state["preMethodFacetName"]['param3'] = os.path.join(tempRP, optionOutputFileClip)

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
            print(f'=====测试===={methodParam}')
            handledFile = None
            if tempMethod == '空间插值':
                with emptyHead:
                    # for _ in stqdm(range(5), desc="This is a slow task", mininterval=1):
                    #     time.sleep(0.5)
                    with st.spinner('数据处理中...'):
                        # time.sleep(5)
                        # methodParam = [
                        #     '02_05.shp',
                        #     'atemp',
                        #     '反距离权重法',
                        #     '118.053330 31.086861 121.953330 27.286861',
                        #     '02_05_预处理.tif']
                        handledFile = FTool.spatialInterpolation(methodParam)
                        # os.path.join(tempRP, handledFile)
                        st.session_state.dPRightMapLayer.append(handledFile)
                    st.toast("空间插值完毕", icon="ℹ️️")
            elif tempMethod == '重采样':
                with emptyHead:
                    with st.spinner('数据处理中...'):
                        handledFile = PretreatmentMethodFacet().onResample(methodParam)
                        # os.path.join(tempRP, handledFile)
                        st.session_state.dPRightMapLayer.append(handledFile)
                    st.toast("重采样完毕", icon="ℹ️️")
                print(handledFile)

            elif tempMethod == '裁剪':
                with emptyHead:
                    with st.spinner('数据处理中...'):
                        handledFile = PretreatmentMethodFacet().onClipRaster(methodParam)
                        # os.path.join(tempRP, handledFile)
                        st.session_state.dPRightMapLayer.append(handledFile)
                    st.toast("裁剪完毕", icon="ℹ️️")
                # os.path.join(tempRP, handledFile)
                print(handledFile)
            with placeHolderDPF2:
                with st.status('加载数据中...'):
                    afterPreMap = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
                    if not onDP2:
                        st.session_state.dPRightMapLayer.clear()
                    for layerPath in st.session_state.dPRightMapLayer:
                        addLayer(afterPreMap, layerPath)
                        st.header(f'{layerPath}加载完成')
                afterPreMap.to_streamlit()
            tempEntryT = os.path.basename(handledFile)
            fileName = tempEntryT.split('.')[0]
            fileFormat = tempEntryT.split('.')[1]
            # 输入文件
            # print('找父节点')
            dataTypeList = []
            inputFileList = [item for item in leftBarsRawData['checked'] if '.' in item]
            for tempNameT in inputFileList:
                tempName = tempNameT.split('.')[0]
                a = find_subnodes(pages_utils.TempDataSetFieldFacet[0], tempName)
                dataTypeList.append(a)
            new_entry = {
                "编号": pages_utils.generateID(),
                "数据类型": dataTypeList,
                "根节点": '预处理后数据集',
                "子节点": '遥感数据',
                "字段": fileName.split('_')[0] if '_' in fileName else "其他",
                "文件名称": fileName,
                "数据格式": fileFormat,
                "输入文件": inputFileList,
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
