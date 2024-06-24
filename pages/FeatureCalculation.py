import datetime

import numpy as np
import pandas as pd
import streamlit as st

import pages_utils
from modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    layout="wide"
)

if 'page13' not in st.session_state:
    st.session_state.page13 = 0
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")
checkBoxNum = 5
if "featureMethodName" not in st.session_state:
    st.session_state["featureMethodName"] = {
        'checkBox': None
    }
if 'FCVisualInformation' not in st.session_state:
    st.session_state["FCVisualInformation"] = []


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
        return '基于活动积温的生育期计算'
    elif checkbox == 'checkbox4':
        return '时空抽取'
    elif checkbox == 'checkbox5':
        return '遥感指数计算'
    elif checkbox == 'checkbox6':
        return '景观指数计算'


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
    elif processName == '基于活动积温的生育期计算':
        return '生育期'
    elif processName == '时空抽取':
        return '时空抽取'
    elif processName == '遥感指数计算':
        return '遥感指数计算'
    elif processName == '景观指数计算':
        return '景观指数计算'


def onRun():
    if '备选特征' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('备选特征')
    st.session_state.page13 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[2]["编号"].tolist()
    fields = pages_utils.TempDataSetField[2]["输入特征"].tolist()
    # outFields = pages_utils.TempDataSetField[2]["备选特征"].tolist()
    methodParam = pages_utils.TempDataSetField[2]["方法参数"].tolist()
    methodList = pages_utils.TempDataSetField[2]["特征计算方法"].tolist()
    isHandledFlags = pages_utils.TempDataSetField[2]["处理状态"].tolist()
    # print('===============获取任务清单内容===============')
    # print(methodParam)
    # print(methodList)

    # 若为空则跳过该步骤
    if not idNumber:
        pages_utils.TempDataSet[2] = pages_utils.TempDataSet[1]

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
        # 第一次使用预处理数据集,而后基于特征计算数据集多次处理
        if pages_utils.TempDataSet[2].shape[0] == 0:
            dataFrameTemp = pages_utils.TempDataSet[1]
        else:
            dataFrameTemp = pages_utils.TempDataSet[2]
        # 使用处理后最新的字段内容
        reservedField = pages_utils.TempDataSet[1].columns.tolist()
        # print(f'=============测试保留字段-{reservedField}=============')
        if tempMethod == '时间(温度)分辨率转换':
            pass
        elif tempMethod == '降雨日数计算':
            afterHandleData, newColumn = FeatureCalculationMethod(
                dataFrameTemp, reservedField).rainfallDaysAccumulation(
                fields[indexT], methodParam[indexT])
        elif tempMethod == '降水累积量计算':
            afterHandleData, newColumn = FeatureCalculationMethod(
                dataFrameTemp, reservedField).precipitationAccumulation(
                fields[indexT], methodParam[indexT])
        elif tempMethod == '基于活动积温的生育期计算':
            afterHandleData, newColumn = FeatureCalculationMethod(
                dataFrameTemp, reservedField).growthPeriodCalculation(
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

        # print('======================备选特征======================')
        # print(pages_utils.TempDataSet[2])
        # ===============更新左侧显示内容===============
        FCVisualInformationTemp = {
            'before': None,
            'name': tempMethod,
            'column': newColumn,
            'after': afterHandleData[[newColumn, '上级单位', '测报站点', '年']]}
        # 可视化信息添加
        st.session_state["FCVisualInformation"].append(FCVisualInformationTemp)
        # print(st.session_state["FCVisualInformation"])
        update_values = {
            "大小": '1*' + str(row_size),
            "备选特征": newColumn,
            "时间": datetime.datetime.now().time(),
            "处理状态": True}
        # 根据字段名和索引来更新字段值
        for index, row in pages_utils.TempDataSetField[2].iterrows():
            if row["编号"] == idNumber[indexT]:
                for key, value in update_values.items():
                    pages_utils.TempDataSetField[2].loc[index, key] = value

    print('===================特征计算数据集===================')
    print(pages_utils.TempDataSet[2])


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
with (featureCCM):
    st.markdown("##### 特征计算方法")
    col1, col2 = st.columns(2)
    with col1:
        # option14 = st.checkbox('时间(温度)分辨率转换', key='checkbox0', on_change=clear_other, args=[0], disabled=True)
        option15 = st.checkbox('降雨日数计算', key='checkbox1', on_change=clear_other, args=[1])
        option16 = st.checkbox('降水累积量计算', key='checkbox2', on_change=clear_other, args=[2])
        option21 = st.checkbox('植被指数计算(待发布)', key='checkbox5', on_change=clear_other, args=[5], disabled=True)
        option14 = st.checkbox('待添加', key='checkbox0', on_change=clear_other, args=[0], disabled=True,
                               label_visibility='hidden')
    with col2:
        option17 = st.checkbox('基于活动积温的生育期计算', key='checkbox3', on_change=clear_other, args=[3])
        option18 = st.checkbox('时空抽取(待发布)', key='checkbox4', on_change=clear_other, args=[4],
                               disabled=True)
        option20 = st.checkbox('景观指数计算(待发布)', key='checkbox6', on_change=clear_other, args=[6], disabled=True)

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
            ('单日降水量', '总降水量'))
        st.session_state["featureMethodName"]['param1'] = str(d1)
        st.session_state["featureMethodName"]['param2'] = str(d2)
        st.session_state["featureMethodName"]['param3'] = option
        if option == '总降水量':
            number11 = st.number_input("总降水量数值(mm)", value=100)
            st.toast('该方法未实现,请选择其他方法', icon="⚠️")
            st.session_state["featureMethodName"]['param4'] = str(number11)
        if option == '单日降水量':
            number2 = st.text_input("单日降水量数值(mm)", value=0.1)
            st.session_state["featureMethodName"]['param4'] = str(number2)
        number1 = st.number_input("连续降雨日数时长(天数)", value=1, min_value=1)
        st.session_state["featureMethodName"]['param5'] = str(number1)

    if option16:
        option3 = st.selectbox(
            '降水累积量计算',
            ('月累积降水量', '指定日期'))
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
            idFMethods = pages_utils.TempDataSetField[2]["特征计算方法"].tolist()
            # inputFields = pages_utils.TempDataSetField[2]["输入特征"].tolist()

            # 若无方法处理,则直接跳过该环节
            if len(idFMethods):
                # 创建新的从 1 开始的编号列表
                new_ids = list(range(0, len(idFMethods)))
                # 创建标签页并重新命名记录
                new_ids = [f'记录编号_{h}' for h in new_ids]

                tt1 = st.tabs(new_ids)
                for o in range(len(idFMethods)):
                    with tt1[o]:
                        # 创建DataFrame
                        data_after = st.session_state["FCVisualInformation"][o]['after']
                        # 特征名称
                        dataColumn = st.session_state["FCVisualInformation"][o]['column']
                        # 删除含有缺失值的行
                        data_after = data_after.dropna()
                        # 去除重复值
                        data_after = data_after.drop_duplicates()

                        if idFMethods[o] == '基于活动积温的生育期计算':
                            # 选择最多8个测报站点
                            top_stations = data_after['测报站点'].value_counts().nlargest(8).index
                            df_filtered_stations = data_after[data_after['测报站点'].isin(top_stations)]

                            # 选择最多3个年份
                            top_years = data_after['年'].value_counts().nlargest(3).index
                            df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]

                            # 绘制折线图
                            plt.figure(figsize=(10, 6))
                            sns.lineplot(
                                data=df_filtered,
                                x="测报站点",
                                y=dataColumn,
                                hue="年",
                                marker="o"
                            )
                            # 设置标签和标题
                            plt.xlabel("测报站点")
                            plt.ylabel(dataColumn)
                            plt.title(f"部分县市与各年份{dataColumn}", fontsize=16)
                            st.pyplot(plt)
                        elif idFMethods[o] == '降水累积量计算':
                            # 时期范围名称修剪
                            integratedDataColumnT = dataColumn.split('_')
                            integratedDataColumn = integratedDataColumnT[0] + '至' + integratedDataColumnT[1] + \
                                                   integratedDataColumnT[2]
                            # 选择最多8个测报站点
                            top_stations = data_after['测报站点'].value_counts().nlargest(8).index
                            df_filtered_stations = data_after[data_after['测报站点'].isin(top_stations)]
                            # 选择最多5个年份
                            top_years = data_after['年'].value_counts().nlargest(5).index
                            df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                            # 绘制柱状图
                            plt.figure(figsize=(10, 6))
                            sns.barplot(
                                data=df_filtered,
                                x="测报站点",
                                y=dataColumn,
                                hue="年",
                                dodge=True,
                                saturation=1
                            )
                            # 设置标签和标题
                            plt.xlabel("测报站点")
                            plt.ylabel("降水累积量")
                            plt.title(f"部分县市与各年份{integratedDataColumn}")
                            st.pyplot(plt)
                        elif idFMethods[o] == '降雨日数计算':
                            # 时期范围名称修剪
                            integratedDataColumnRT = dataColumn.split('_')
                            integratedDataColumnR = integratedDataColumnRT[0] + '至' + integratedDataColumnRT[1] + \
                                                    integratedDataColumnRT[2]
                            # 选择最多8个测报站点
                            top_stations = data_after['测报站点'].value_counts().nlargest(8).index
                            df_filtered_stations = data_after[data_after['测报站点'].isin(top_stations)]

                            # 选择最多3个年份
                            top_years = data_after['年'].value_counts().nlargest(3).index
                            df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                            # 绘制折线图
                            plt.figure(figsize=(10, 6))
                            sns.lineplot(
                                data=df_filtered,
                                x="测报站点",
                                y=dataColumn,
                                hue="年",
                                marker="o"
                            )
                            # 设置标签和标题
                            plt.xlabel("测报站点")
                            plt.ylabel("降雨日数")
                            plt.title(f"部分县市与各年份{integratedDataColumnR}")
                            st.pyplot(plt)
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('返回', on_click=firstPage)
