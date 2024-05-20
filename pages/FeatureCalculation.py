import datetime

import numpy as np
import pandas as pd
import streamlit as st
from streamlit import switch_page

import pages_utils
from modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    layout="wide"
)

if 'page13' not in st.session_state:
    st.session_state.page13 = 0

checkBoxNum = 5
if "featureMethodName" not in st.session_state:
    st.session_state["featureMethodName"] = {
        'checkBox': None
    }


def mergeArray4(list1, list2, list3, list4):
    return list(set().union(*[list1, list2, list3, list4]))


# 模拟月降水量数据
def simulate_month_precipitation():
    # 生成一个包含一整年每个月第一天的日期时间序列
    months = pd.date_range(start='2023-01-01', end='2023-12-01', freq='MS')

    # 生成12个随机的降水量数据
    precipitation = np.random.uniform(0, 100, size=12)

    # 创建包含月份和降水量的数据框
    data = {'Month': months, 'Precipitation': precipitation}
    df = pd.DataFrame(data)
    return df


# 获取选项值对应名称
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


# 获取输出特征名称
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
    if '备选特征' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('备选特征')
    st.session_state.page13 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[2]["编号"].tolist()
    fields = pages_utils.TempDataSetField[2]["输入特征"].tolist()
    outFields = pages_utils.TempDataSetField[2]["备选特征"].tolist()
    methodParam = pages_utils.TempDataSetField[2]["方法参数"].tolist()
    methodList = pages_utils.TempDataSetField[2]["特征计算方法"].tolist()
    isHandledFlags = pages_utils.TempDataSetField[2]["处理状态"].tolist()
    print('===============获取任务清单内容===============')
    print(methodParam)
    print(methodList)

    afterHandleData = None
    newColumn = '错误'
    # ===============根据名称匹配调用并执行各个处理方法===============
    # 初始化特征计算方法
    # methodTool = FeatureCalculationMethod(
    #     pages_utils.TempDataSet[1],
    #     reservedField + outFields)
    for indexT, (tempMethod, isHandled) in enumerate(zip(methodList, isHandledFlags)):
        # 检查方法是否已执行
        if isHandled:
            continue
        # 使用处理后最新的字段内容
        reservedField = pages_utils.TempDataSet[1].columns.tolist()
        print(f'=============测试保留字段-{reservedField}=============')
        if tempMethod == '时间(温度)分辨率转换':
            pass
        elif tempMethod == '降雨日数计算':
            afterHandleData = FeatureCalculationMethod(
                pages_utils.TempDataSet[1], reservedField).rainfallDaysAccumulation(
                fields[indexT], methodParam[indexT])
        elif tempMethod == '降水累积量计算':
            afterHandleData, newColumn = FeatureCalculationMethod(
                pages_utils.TempDataSet[1], reservedField).precipitationAccumulation(
                fields[indexT], methodParam[indexT])
        elif tempMethod == '基于活动期积温的生育期计算':
            afterHandleData, newColumn = FeatureCalculationMethod(
                pages_utils.TempDataSet[1], reservedField).growthPeriodCalculation(
                fields[indexT], methodParam[indexT])
        elif tempMethod == '时空抽取':
            return '时空抽取'

        # ===============合并处理后数据集===============
        row_size = len(afterHandleData)
        intersection_cols = pages_utils.getIntersectionCols(
            pages_utils.TempDataSet[2], afterHandleData
        )
        pages_utils.TempDataSet[2] = pd.merge(
            afterHandleData, pages_utils.TempDataSet[2],
            on=intersection_cols, how="left")

        print('======================备选特征======================')
        print(pages_utils.TempDataSet[2])

        # pages_utils.TempDataSet[2].to_excel(
        #     r'E:\a_python\program\testPlatform\demo\demo109\a' + str(indexT) + '.xlsx', index=False)

        # ===============更新左侧显示内容===============
        update_values = {
            # "数据类型": "气象数据", "输入特征": fields[0],
            # "备选特征": getFeatureName(st.session_state["featureMethodName"]['checkBox']),
            "大小": '1*' + str(row_size),
            "备选特征": newColumn,
            # "特征计算方法": st.session_state["featureMethodName"]['checkBox'],
            "时间": datetime.datetime.now().time(),
            "处理状态": True}
        # 查找要更新的数据记录
        for index, row in pages_utils.TempDataSetField[2].iterrows():
            if row["编号"] == idNumber[0]:
                for key, value in update_values.items():
                    pages_utils.TempDataSetField[2].loc[index, key] = value
                    # 根据字段名和索引来更新字段值
    # ======================特征计算-保留字段======================
    print('======================特征计算-保留字段======================')
    tempReserved = afterHandleData.columns
    pages_utils.TempDataSet[2] = pages_utils.TempDataSet[2][tempReserved]


# ==============================界面==============================
featureCCV, featureCCM = st.columns([0.5, 0.7])
with featureCCV:
    st.markdown("##### 数据与特征")
    # =======================显示左侧数据与特征表格=======================
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        with placeholder1.container():
            tempLefTabs = st.session_state["leftTabs"][1:]
            if not tempLefTabs:
                tempLefTabs = ['待进行数据预处理']
                column = ['空']
            tt1 = st.tabs(tempLefTabs)
            for i in range(len(tempLefTabs)):
                with tt1[i]:
                    if tempLefTabs[i] == '原始数据':
                        column = ['数据类型', '字段', '上传时间']
                    elif tempLefTabs[i] == '预处理后数据集':
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
                    elif tempLefTabs[i] == '备选特征':
                        column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
                    st.data_editor(
                        pages_utils.TempDataSetField[i + 1],
                        height=220, width=800,
                        column_order=column)

    if st.session_state.page12 == 1:
        with placeholder1.container():
            tempLefTabs = st.session_state["leftTabs"][1:]
            tt = st.tabs(tempLefTabs)
            for i in range(len(tempLefTabs)):
                with tt[i]:
                    if tempLefTabs[i] == '原始数据':
                        column = ['数据类型', '字段', '上传时间']
                    elif tempLefTabs[i] == '预处理后数据集':
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
                    elif tempLefTabs[i] == '备选特征':
                        column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
                    st.data_editor(
                        pages_utils.TempDataSetField[i + 1],
                        height=220, width=800,
                        column_order=column)
    # ===============显示左下字段或特征及获取===============
    # a = st.selectbox(
    #     '选择数据集',
    #     ('原始数据集', '预处理后数据集', '备选特征', '优选特征'))

    # 预处理后数据集表信息
    # weatherNameT, plantNameT, agricultureNameT = pages_utils.getDataFiled()
    weatherNameT, plantNameT, agricultureNameT = pages_utils.TempDataSet[1].columns.tolist(), ['无1'], ['无2']
    # 数组元素去重
    weatherName, plantName, agricultureName = list(set(weatherNameT)), list(set(plantNameT)), list(
        set(agricultureNameT))
    result1 = pages_utils.multiselect_all(
        st, '全选-特征', weatherName,
        'temp', 'collapsed')
    st.checkbox('全选-植保数据', disabled=True)
    st.checkbox('全选-农学数据', disabled=True)
    result2 = []
    result3 = []
    # result2 = pages_utils.multiselect_all(
    #     st, '全选-植保数据', plantName,
    #     'temp', 'collapsed')
    # result3 = pages_utils.multiselect_all(
    #     st, '全选-农学数据', agricultureName,
    #     'temp', 'collapsed')

# ===============显示右上处理方法选项===============
with featureCCM:
    st.markdown("##### 特征计算方法")
    col1, col2 = st.columns(2)
    with col1:
        # option14 = st.checkbox('时间(温度)分辨率转换', key='checkbox0', on_change=clear_other, args=[0], disabled=True)
        option15 = st.checkbox('降雨日数计算', key='checkbox1', on_change=clear_other, args=[1])
        option16 = st.checkbox('降水累积量计算', key='checkbox2', on_change=clear_other, args=[2])
        option14 = st.checkbox('待添加', key='checkbox0', on_change=clear_other, args=[0], disabled=True)

    with col2:
        option17 = st.checkbox('基于活动积温的生育期计算', key='checkbox3', on_change=clear_other, args=[3])
        option18 = st.checkbox('时空抽取(待面状建模系统发布)', key='checkbox4', on_change=clear_other, args=[4], disabled=True)
    st.markdown('---')
    # ===============显示和处理右中各个处理方法设置参数===============
    # if option14:
    #     option1 = st.selectbox(
    #         '分辨率转换',
    #         ('日值温度', '旬平均温度', '月平均温度'))
    if option15:
        d1 = st.date_input("开始时间", value=None)
        d2 = st.date_input("结束时间", value=None)
        option = st.selectbox(
            '计算阈值方式',
            ('总降水量', '单日降水量'))
        st.session_state["featureMethodName"]['param1'] = str(d1)
        st.session_state["featureMethodName"]['param2'] = str(d2)
        st.session_state["featureMethodName"]['param3'] = option
        if option == '总降水量':
            number11 = st.number_input("总降水量数值(mm)", value=100)
            st.session_state["featureMethodName"]['param4'] = str(number11)
        if option == '单日降水量':
            number2 = st.text_input("单日降水量数值(mm)", value=0.1)
            st.session_state["featureMethodName"]['param4'] = str(number2)
        number1 = st.number_input("连续降雨日数时长(天数)", value=1, min_value=1)
        st.session_state["featureMethodName"]['param5'] = str(number1)

    if option16:
        option3 = st.selectbox(
            '降水累积量计算',
            ('月累积降水量', '指定日期', '旬累积降水量'))
        st.session_state["featureMethodName"]['param1'] = option3

        if option3 == '指定日期':
            sd1 = st.date_input("开始时间", value='today')
            ed1 = st.date_input("结束时间", value='today')
            st.session_state["featureMethodName"]['param2'] = sd1.strftime('%m-%d')
            st.session_state["featureMethodName"]['param3'] = ed1.strftime('%m-%d')

    if option17:
        growthPeriod = st.selectbox(
            '生育期',
            ('抽穗期', '孕穗期', '移栽期'))
        growthPeriodStartDate = st.date_input("开始时间", value='today')
        growthPeriodEndDate = st.date_input("结束时间", value='today')
        # 积温阈值默认为50
        threshold = 50
        if growthPeriod == '抽穗期':
            threshold = 50
        elif growthPeriod == '孕穗期':
            threshold = 100
        elif growthPeriod == '移栽期':
            threshold = 150
        growthPeriodNumber = st.number_input(
            "积温阈值温度(50-300℃)", value=threshold, step=50,
            min_value=50, max_value=300)

        st.session_state["featureMethodName"]['param1'] = growthPeriod
        st.session_state["featureMethodName"]['param2'] = growthPeriodStartDate.strftime('%m-%d')
        st.session_state["featureMethodName"]['param3'] = growthPeriodEndDate.strftime('%m-%d')
        st.session_state["featureMethodName"]['param4'] = str(growthPeriodNumber)
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

    # =======================添加处理至任务清单=======================
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clear_all)
    if btn:
        # 测试特征方法名称正确性
        for key11, value11 in st.session_state["featureMethodName"].items():
            pass
            # print('============测试方法参数正确性============')
            # print(f"Key: {key11}, Value: {value11}")
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": '气象数据',
            "输入特征": mergeArray(result1, result2, result3),
            "特征计算方法": getCheckboxName(st.session_state["featureMethodName"]['checkBox']),
            "方法参数": [value for key, value in st.session_state["featureMethodName"].items() if key != 'checkBox'],
            "时间": datetime.datetime.now().time(),
            "处理状态": False}
        print('======================特征计算-添加任务清单记录======================')
        print(new_data)
        pages_utils.TempDataSetField[2].loc[len(pages_utils.TempDataSetField[2])] = new_data
        st.rerun()
    st.markdown('---')

    # =======================显示右下内容=======================
    placeholder = st.empty()
    if st.session_state.page13 == 0:
        # =======================显示右下任务清单表格=======================
        with placeholder.container():
            st.markdown('##### 任务清单')
            pages_utils.TempDataSetField[2] = st.data_editor(
                pages_utils.TempDataSetField[2], height=190, width=800,
                column_order=["编号", "数据类型", "输入特征", "备选特征", "特征计算方法", '时间', '处理状态'],
                disabled=["数据类型", "时间", '处理状态'], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])

            # with interval_col33:
            #     with st.popover("准备运行"):
            #         st.markdown('保留字段选择')
            #         residualField = [arr for arr in pages_utils.TempDataSet[1].columns if
            #                          arr not in mergeArray4(
            #                              ['上级单位', '测报站点',
            #                               "年", "DayOfYear"], result1, result2, result3)]
            #         # print(f'剩余字段{residualField}')
            #         reservedFiled = pages_utils.multiselect_all(
            #             st, '全选',
            #             residualField,
            #             'temp2', 'collapsed')
            #         btn = st.button('运行', on_click=onRun, args=[reservedFiled])
            btn2 = interval_col33.button('运行', on_click=onRun)
    elif st.session_state.page13 == 1:
        # =======================显示右下可视化图表=======================
        with placeholder.container():
            st.markdown('##### 可视化')
            plt.rc("font", family='Microsoft YaHei')
            tab1, tab2 = st.tabs(["1", "2"])
            with tab1:
                # 模拟降水数据
                precipitation_data = simulate_month_precipitation()
                # 绘制最高温度和最低温度的折线图
                plt.figure(figsize=(10, 5))
                sns.lineplot(data=precipitation_data, x="Month", y="Precipitation", label="降水量")
                plt.xlabel('日期')
                plt.ylabel('降水累积量(mm)')
                plt.title('降水累积量特征')
                plt.legend()
                st.pyplot(plt)
            with tab2:
                pass
            interval_col34, interval_col33 = st.columns([5, 1])
            want_to_contribute = interval_col34.button("跳转至可视化界面")
            if want_to_contribute:
                switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\Visualization.py")
            btn3 = interval_col33.button('返回', on_click=firstPage)
