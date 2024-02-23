import datetime

import numpy as np
import pandas as pd
import streamlit as st

import pages_utils

if 'page13' not in st.session_state:
    st.session_state.page13 = 0

checkBoxNum = 5
if "featureMethodName" not in st.session_state:
    st.session_state["featureMethodName"] = {
        'checkBox': None
    }


def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '时间(温度)分辨率转换'
    elif checkbox == 'checkbox1':
        return '降雨日数计算'
    elif checkbox == 'checkbox2':
        return '降水累积量计算'
    elif checkbox == 'checkbox3':
        return '基于活动期积温的生育期计算'
    elif checkbox == 'checkbox4':
        return '时空抽取'


def mergeArray(list1, list2, list3):
    return list(set().union(*[list1, list2, list3]))


# def simulate_temperature_data():
#     # 模拟生成温度数据
#     data = {
#         'City': ['City1', 'City2', 'City3'],
#         'Temperature': np.append([
#             np.random.normal(25, 5, 10),
#             np.random.normal(20, 3, 10),
#             np.random.normal(30, 7, 10)
#         ])
#     }
#     df = pd.DataFrame(data)
#     return df


# 取消所有选项按钮
def clear_all():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["featureMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    return


# 取消其他选项按钮
def clear_other(key):
    for h in range(checkBoxNum):
        if h != key:
            st.session_state[f'checkbox{h}'] = False
    return


def firstPage(): st.session_state.page13 = 0


# 降水累积量计算
def precipitationAccumulation(dataFrame, fieldName):
    dataFrame['降水累积量'] = dataFrame[fieldName].sum()

    # 单独计算插补所用的总和
    sum_value = dataFrame[fieldName].sum()
    # print(f"均值为: {sum_value}")
    dataFrame['降水累积量'].fillna(sum_value, inplace=True)

    tempData = dataFrame[['上级单位', '测报站点', "年", "DayOfYear",
                          fieldName, '降水累积量', '预测病株率']]
    return tempData


def getFeatureName(processName):
    if processName == '时间(温度)分辨率转换':
        return ''
    elif processName == '降雨日数计算':
        return '降雨日数'
    elif processName == '降水累积量计算':
        return '降水累积量'
    elif processName == '基于活动期积温的生育期计算':
        return '生育期'
    elif processName == '时空抽取':
        return '时空抽取'


def onRun():
    if '被选特征' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('被选特征')
    st.session_state.page13 += 1

    # 调用数据和各类方法
    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[2]["编号"].tolist()
    fields = pages_utils.TempDataSetField[2]["输入特征"].tolist()
    # methodNames = pages_utils.TempDataSetField[2]["特征计算方法"].tolist()

    # ===============根据名称匹配调用并执行各个处理方法===============
    afterHandleData = precipitationAccumulation(
        pages_utils.TempDataSet[1], fields[0][0])
    row_size = len(afterHandleData)
    # print('-------特征-------')
    # print(pages_utils.TempDataSet[2])
    # print('-------特征-------')
    intersection_cols = pages_utils.getIntersectionCols(
        pages_utils.TempDataSet[2], afterHandleData
    )
    pages_utils.TempDataSet[2] = pd.merge(
        afterHandleData, pages_utils.TempDataSet[2],
        on=intersection_cols, how="left")

    print('======================被选特征======================')
    print(pages_utils.TempDataSet[2])

    # 更新记录
    update_values = {
        # "数据类型": "气象数据", "输入特征": fields[0],
        # "被选特征": getFeatureName(st.session_state["featureMethodName"]['checkBox']),
        "大小": '1*' + str(row_size),
        # "特征计算方法": st.session_state["featureMethodName"]['checkBox'],
        "时间": datetime.datetime.now().time()}
    # 查找要更新的数据记录
    for index, row in pages_utils.TempDataSetField[2].iterrows():
        if row["编号"] == idNumber[0]:
            for key, value in update_values.items():
                pages_utils.TempDataSetField[2].loc[index, key] = value
                # 根据字段名和索引来更新字段值


featureCCV, featureCCM = st.columns([0.5, 0.7])
with featureCCV:
    st.markdown("##### 数据与特征")
    # st.data_editor(pages_utils.TempDataSet[0])
    # st.markdown(pages_utils.TempDataSet[1])
    # st.markdown(pages_utils.TempDataSet[2])
    # st.markdown(pages_utils.TempDataSet[3])
    # =======================左侧数据与特征显示=======================
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        with placeholder1.container():
            tt1 = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt1[i]:
                    if st.session_state["leftTabs"][i] == '原始数据':
                        column = ['数据类型', '字段', '上传时间']
                    elif st.session_state["leftTabs"][i] == '预处理后数据集':
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '被选特征':
                        column = ["数据类型", "被选特征", "大小", "特征计算方法", '时间', "下载数据集"]
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)

    if st.session_state.page12 == 1:
        with placeholder1.container():
            tt = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt[i]:
                    if st.session_state["leftTabs"][i] == '原始数据':
                        column = ['数据类型', '字段', '上传时间']
                    elif st.session_state["leftTabs"][i] == '预处理后数据集':
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '被选特征':
                        column = ["数据类型", "被选特征", "大小", "特征计算方法", '时间', "下载数据集"]
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)
    # =======================选择数据集=======================
    a = st.selectbox(
        '选择数据集',
        ('原始数据集', '预处理后数据集', '被选特征', '优选特征'))

    # =======================获取数据集字段=======================
    # 预处理后数据集表信息
    weatherNameT, plantNameT, agricultureNameT = pages_utils.getDataFiled(a)
    # 数组元素去重
    weatherName, plantName, agricultureName = list(set(weatherNameT)), list(set(plantNameT)), list(
        set(agricultureNameT))
    result1 = pages_utils.multiselect_all(
        st, '全选-气象数据', weatherName,
        'temp', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-植保数据', plantName,
        'temp', 'collapsed')
    result3 = pages_utils.multiselect_all(
        st, '全选-农学数据', agricultureName,
        'temp', 'collapsed')
with featureCCM:
    st.markdown("##### 特征计算方法")
    col1, col2 = st.columns(2)
    with col1:
        option14 = st.checkbox('时间(温度)分辨率转换', key='checkbox0', on_change=clear_other, args=[0])
        option15 = st.checkbox('降雨日数计算', key='checkbox1', on_change=clear_other, args=[1])
        option16 = st.checkbox('降水累积量计算', key='checkbox2', on_change=clear_other, args=[2])
    with col2:
        option17 = st.checkbox('基于活动积温的生育期计算', key='checkbox3', on_change=clear_other, args=[3])
        option18 = st.checkbox('时空抽取', key='checkbox4', on_change=clear_other, args=[4])

    st.markdown('---')
    if option14:
        option1 = st.selectbox(
            '分辨率转换',
            ('日值温度', '旬平均温度', '月平均温度'))
    if option15:
        d1 = st.date_input("开始时间", value=None)
        d2 = st.date_input("结束时间", value=None)
        option = st.selectbox(
            '计算阈值方式',
            ('总降水量', '单日降水量'))
        if option == '总降水量':
            number1 = st.number_input("总降水量数值(mm)", value=100)
        if option == '单日降水量':
            number2 = st.text_input("单日降水量数值(mm)", value=0.1)
        number1 = st.number_input("连续降雨日数时长(天数)", value=1, min_value=1)
    if option16:
        option3 = st.selectbox(
            '降水累积量计算',
            ('日累积降水量', '旬累积降水量', '月累积降水量'))
        st.session_state["featureMethodName"]['param1'] = option3
    if option17:
        d1 = st.date_input("开始时间", value=None)
        d2 = st.date_input("结束时间", value=None)
        j4 = st.selectbox(
            '生育期',
            ('抽穗期', '孕穗期'))
        if j4 == '抽穗期':
            number = st.number_input(
                "积温阈值温度(50-300℃)", value=50, step=50,
                min_value=50, max_value=300)
        if j4 == '孕穗期':
            number = st.number_input(
                "积温阈值温度(50-300℃)", value=100, step=50,
                min_value=50, max_value=300)

    if option18:
        option = st.selectbox(
            '抽取因子',
            ('降水', '温度'))
        option4 = st.selectbox(
            '计算方式',
            ('平均值', '累积值'))
        j3 = st.selectbox(
            '起始日期',
            ('基于活动积温的生育期计算', '指定日期'))
        if j3 == '指定日期':
            d3 = st.date_input("起始日期", value=None, label_visibility='collapsed')
        if j3 == '基于活动积温的生育期计算':
            pass
        d4 = st.date_input("结束日期", value=None)
        number1 = st.number_input("步长(天)", value=1, min_value=1)
        # st.markdown('---')
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clear_all)
    # =======================执行任务清单=======================
    if btn:
        for key11, value11 in st.session_state["featureMethodName"].items():
            pass
            # print(f"Key: {key11}, Value: {value11}")
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": '气象数据',
            "输入特征": mergeArray(result1, result2, result3),
            "被选特征": getFeatureName(getCheckboxName(st.session_state["featureMethodName"]['checkBox'])),
            "特征计算方法": getCheckboxName(st.session_state["featureMethodName"]['checkBox']),
            "方法参数": [value for key, value in st.session_state["featureMethodName"].items() if key != 'checkBox'],
            "时间": datetime.datetime.now().time(),
            "下载数据集": False}
        print('======================特征计算-添加任务清单记录======================')
        print(new_data)
        pages_utils.TempDataSetField[2].loc[len(pages_utils.TempDataSetField[2])] = new_data
        st.rerun()
    st.markdown('---')

    # =======================显示任务清单=======================
    placeholder = st.empty()
    if st.session_state.page13 == 0:
        with placeholder.container():
            st.markdown('##### 任务清单')
            edited_df28 = st.data_editor(
                pages_utils.TempDataSetField[2], height=190, width=800,
                column_order=["编号", "数据类型", "输入特征", "被选特征", "特征计算方法", '时间'],
                disabled=["数据类型", "时间"], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])
            btn2 = interval_col33.button('运行', on_click=onRun)
    elif st.session_state.page13 == 1:
        with placeholder.container():
            st.markdown('##### 可视化')
            tab1, tab2 = st.tabs(["1", "2"])
            with tab1:
                precipitation_data = np.random.normal(50, 10, 20)
                chart_data = pd.DataFrame({
                    "Precipitation": precipitation_data,
                    "月份": np.arange(1, 21),  # 月份从1到20
                    "图例": np.random.randint(1, 5, 20)  # 随机生成图例数据
                })
                st.vega_lite_chart(
                    chart_data,
                    {
                        "mark": {"type": "circle", "tooltip": True},
                        "encoding": {
                            "x": {"field": "月份", "type": "quantitative"},
                            "y": {"field": "Precipitation", "type": "quantitative"},
                            "size": {"field": "图例", "type": "quantitative"},
                            "color": {"field": "图例", "type": "quantitative"},
                        },
                    },
                )
            with tab2:
                pass
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('返回', on_click=firstPage)
