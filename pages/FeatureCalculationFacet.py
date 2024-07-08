"""
@Author : SakuraFox
@Time: 2024-06-30 13:48
@File : FeatureCalculationFacet.py
@Description : 面状数特征计算界面
"""
import datetime

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

checkBoxNum = 7
if "featureMethodFacetName" not in st.session_state:
    st.session_state["featureMethodFacetName"] = {
        'checkBox': None
    }
# 获取当前选中的方法名称
if "nowFFacetMethodName" not in st.session_state:
    st.session_state.nowFFacetMethodName = ''


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '时间(温度)分辨率转换'
    elif checkbox == 'checkbox1':
        return '降雨日数计算'
    elif checkbox == 'checkbox2':
        return '降水累积量计算'
    elif checkbox == 'checkbox3':
        return '基于活动积温的生育期计算'
    elif checkbox == 'checkbox4':
        return '时空抽取'
    elif checkbox == 'checkbox5':
        return '遥感指数计算'
    elif checkbox == 'checkbox6':
        return '景观指数计算'


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


colFCF1, colFCF2, colFCF3 = st.columns([0.2, 0.9, 0.3])
with colFCF1:
    st.markdown("##### 数据与特征")
    nodes1 = [
        {"label": "植保数据", "value": "气象数据"},
        {
            "label": "气象数据",
            "value": "气象数据文件夹",
            "children": [
                {"label": "temperature_1", "value": "temperature_1_2024"},
                {"label": "temperature_2", "value": "temperature_2_2024"},
                {"label": "temperature_3", "value": "temperature_3_2024"},
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
        {"label": "其他",
         "value": "其他",
         "children": [
             {"label": "模板文件", "value": "模板文件"},
             {"label": "待提取特征文件", "value": "待提取特征文件"},
         ],
         },
    ]
    temp = tree_select(nodes1)
    st.markdown(temp)
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
        option21 = st.checkbox('植被指数计算(待发布)', key='checkbox5', on_change=clear_other, args=[5])
        option20 = st.checkbox('景观指数计算(待发布)', key='checkbox6', on_change=clear_other, args=[6])

    with col2:
        option18 = st.checkbox('时空抽取(待发布)', key='checkbox4', on_change=clear_other, args=[4])
        option22 = st.checkbox('空间点提取(待发布)', key='checkbox7', on_change=clear_other, args=[7])

    st.markdown('---')
    # ===============显示和处理右中各个处理方法设置参数===============
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

        # 测试特征方法名称正确性
        for key11, value11 in st.session_state["featureMethodFacetName"].items():
            pass
            # print('============测试方法参数正确性============')
            # print(f"Key: {key11}, Value: {value11}")
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": '气象数据',
            "输入特征": None,
            "特征计算方法": getCheckboxName(st.session_state["featureMethodFacetName"]['checkBox']),
            "方法参数": [value for key, value in st.session_state["featureMethodFacetName"].items() if
                         key != 'checkBox'],
            "时间": datetime.datetime.now().time(),
            "处理状态": False}
        print('======================特征计算-添加任务清单记录======================')
        print(new_data)
        # pages_utils.TempDataSetField[2].loc[len(pages_utils.TempDataSetField[2])] = new_data
        # st.rerun()
