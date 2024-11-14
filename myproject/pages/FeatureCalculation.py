import datetime
import os

import pandas as pd
import streamlit as st
from PIL import Image
from st_pages import hide_pages

from lib.share import RESOURCE_IMAGES_PATH
from lib.utils import filterUnique, mergeExcludeArray
from pages import pages_utils
from pages.modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    layout="wide"
)
# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据-面状",
        "数据预处理-面状",
        "特征计算-面状",
        "特征优选-面状",
        "模型构建-面状",
        "基于天气情景生成器的模型评价-面状",
        "建模报告-面状",
        "模型应用-面状",
        "数据下载中心-面状",
    ]
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr2 {display: none;}
    </style>
    """, unsafe_allow_html=True)
st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)
if 'page13' not in st.session_state:
    st.session_state.page13 = 0
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")
    st.switch_page("app.py")
# 判断首次加载页面
if 'initFlagNum' not in st.session_state:
    st.session_state.initFlagNum = 0

# 检测预处理数据是否符合日值且无缺失值
if st.session_state.timeResolution and not st.session_state.initFlagNum:
    print('首次加载计算')
    st.session_state.initFlagNum += 1
    # 计算旬、月、年内日期和日期字段
    tempDataSet1 = pages_utils.TempDataSet[1]
    tempDataSet1['日期'] = pd.to_datetime(
        tempDataSet1['年'].astype(str) + tempDataSet1['DayOfYear'].astype(str), format='%Y%j')
    tempDataSet1['年内日期'] = tempDataSet1['日期'].dt.strftime('%m-%d')
    # 提取月份
    tempDataSet1['月'] = tempDataSet1['日期'].dt.month
    # 计算每天所在的旬，假设1-10日为第一旬，11-20日为第二旬，21日至月末为第三旬
    tempDataSet1['旬'] = tempDataSet1['日期'].dt.day.apply(FeatureCalculationMethod.get_decade)
    # pages_utils.TempDataSet[1] = tempDataSet1
    # pages_utils.TempDataSet[1].to_excel('计算预处理.xlsx')
    # 分辨率统一
    if st.session_state.timeResolution == '日值':
        pass
    elif st.session_state.timeResolution == '每5天':
        # 1. 每5天的降水累积量
        # 添加一个5天分组列
        tempDataSet1['5天组'] = (tempDataSet1['DayOfYear'] - 1) // 5 + 1
        # 删除闰年 2 月 29 日的行
        tempDataSet1 = tempDataSet1[~((tempDataSet1['年'] % 4 == 0) & (tempDataSet1['年'] % 100 != 0) | (
                tempDataSet1['年'] % 400 == 0) & (tempDataSet1['DayOfYear'] == 60))]
        # tempDataSet1['5天组'] = (tempDataSet1['DayOfYear'] - 1) // 5 + 1  # 创建一个按5天分组的标识
        pages_utils.TempDataSet[1] = tempDataSet1.groupby(['经度', '纬度', '年', '5天组']).mean(
            numeric_only=True).reset_index()
    elif st.session_state.timeResolution == '旬值':
        # 2. 每旬的降水累积量
        pages_utils.TempDataSet[1] = tempDataSet1.groupby(['经度', '纬度', '年', '月', '旬']).mean(
            numeric_only=True).reset_index()
    elif st.session_state.timeResolution == '月值':
        # 3. 每月的降水累积量
        pages_utils.TempDataSet[1] = tempDataSet1.groupby(['经度', '纬度', '年', '月']).mean(
            numeric_only=True).reset_index()

st.markdown(
    """
    <style>
    h2 {
        margin-top: -100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.header('多场景作物病虫害快速预测建模系统')
emptyHeadFCP = st.empty()

checkBoxNum = 4
if "featureMethodName" not in st.session_state:
    st.session_state["featureMethodName"] = {
        'checkBox': None
    }
if 'FCVisualInformation' not in st.session_state:
    st.session_state["FCVisualInformation"] = []
plt.rc("font", family='Microsoft YaHei')


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '活动积温计算'
    elif checkbox == 'checkbox1':
        return '降雨日数计算'
    elif checkbox == 'checkbox2':
        return '降水累积量计算'
    elif checkbox == 'checkbox3':
        return '基于活动积温的生育期计算'


# 取消所有选项按钮
def clear_all():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["featureMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    # 若已经在可视化展示状,则默认返回任务清单
    st.session_state.page13 = 0
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
    if processName == '活动积温计算':
        return '活动积温'
    elif processName == '降雨日数计算':
        return '降雨日数'
    elif processName == '降水累积量计算':
        return '降水累积量'
    elif processName == '基于活动积温的生育期计算':
        return '生育期'


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
    with emptyHeadFCP:
        with st.spinner('处理数据中...'):
            # 若为空则跳过该步骤
            if not idNumber:
                pages_utils.TempDataSet[2] = pages_utils.TempDataSet[1]
                # print('---测试跳转---')
                # print(st.session_state["leftTabs"])
                # st.session_state["leftTabs"].pop(0)
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
                elif tempMethod == '活动积温计算':
                    afterHandleData, newColumn = FeatureCalculationMethod(
                        dataFrameTemp, reservedField).activeAccumulatedTemperature(
                        fields[indexT], methodParam[indexT])

                # ===============合并处理后数据集===============
                row_size = len(afterHandleData)
                print(afterHandleData)
                intersection_cols = pages_utils.getIntersectionCols(
                    pages_utils.TempDataSet[2], afterHandleData
                )
                pages_utils.TempDataSet[2] = pd.merge(
                    afterHandleData, pages_utils.TempDataSet[2],
                    on=intersection_cols, how="left")

                # print('======================备选特征======================')
                # print(pages_utils.TempDataSet[2])
                # ===============更新左侧显示内容===============
                # 区分计算如旬多个特征值或单个特征值
                # if len(newColumn) == 1:
                # 若计算多个特征值只显示第一个
                newColumnTR1 = newColumn.split(',')
                if '错误' in newColumnTR1:
                    st.toast('基于活动积温计算的生育期出错，请重新设定积温阈值', icon="⚠️")
                    st.session_state["FCVisualInformation"].append({})
                    continue
                FCVisualInformationTemp = {
                    'before': None,
                    'name': tempMethod,
                    'column': newColumnTR1[0],
                    'after': afterHandleData[[newColumnTR1[0], '经度', '纬度', '年']]}
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
                # else:
                #     for indexTTT1, tempNewColumn in enumerate(newColumn):
                #         # 只展示第一个旬、月特征值
                #         FCVisualInformationTemp = {
                #             'before': None,
                #             'name': tempMethod,
                #             'column': tempNewColumn,
                #             'after': afterHandleData[[tempNewColumn, '经度', '纬度', '年']]}
                #         # 可视化信息添加
                #         st.session_state["FCVisualInformation"].append(FCVisualInformationTemp)
                #         # print(st.session_state["FCVisualInformation"])
                #         update_values = {
                #             "大小": '1*' + str(row_size),
                #             "备选特征": tempNewColumn,
                #             "时间": datetime.datetime.now().time(),
                #             "处理状态": True}
                #         # print('更新内容')
                #         # print(update_values)
                #         # 根据字段名和索引来更新字段值
                #         for index, row in pages_utils.TempDataSetField[2].iterrows():
                #             print(row["编号"])
                #             print(idNumber[indexTTT1])
                #             if row["编号"] == idNumber[indexTTT1]:
                #                 for key, value in update_values.items():
                #                     pages_utils.TempDataSetField[2].loc[index, key] = value
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
            if pages_utils.TempDataSet[2].columns.tolist() == pages_utils.TempDataSet[1].columns.tolist():
                tt = st.tabs(['预处理后数据集'])
                with tt[0]:
                    st.data_editor(
                        pages_utils.TempDataSet[1],
                        height=220, width=800, )
            else:
                tt = st.tabs(['预处理后数据集', '备选特征'])
                with tt[0]:
                    # column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
                    st.data_editor(
                        pages_utils.TempDataSet[1],
                        height=220, width=800, )
                with tt[1]:
                    st.data_editor(
                        pages_utils.TempDataSet[2],
                        height=220, width=800, )
            # with tt1[i]:
            #     # if tempLefTabs[i] == '原始数据':
            #     #     column = ['数据类型', '字段', '上传时间']
            #     if tempLefTabs[i] == '预处理后数据集':
            #
            #     elif tempLefTabs[i] == '备选特征':
            #         column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
            #     st.data_editor(
            #         pages_utils.TempDataSet[i],
            #         height=220, width=800, )
            # column_order=column)

    if st.session_state.page12 == 1:
        with placeholder1.container():
            if pages_utils.TempDataSet[2].columns.tolist() == pages_utils.TempDataSet[1].columns.tolist():
                tt = st.tabs(['备选特征'])
                with tt[0]:
                    st.data_editor(
                        pages_utils.TempDataSet[2],
                        height=220, width=800, )
            else:
                tt = st.tabs(['预处理后数据集', '备选特征'])
                with tt[0]:
                    st.data_editor(
                        pages_utils.TempDataSet[1],
                        height=220, width=800, )
                with tt[1]:
                    st.data_editor(
                        pages_utils.TempDataSet[2],
                        height=220, width=800, )
    # ===============显示左下字段或特征及获取===============
    # weatherNameList, plantNameList, agricultureNameList = ['无1'], ['无2'], ['无3']
    # if not pages_utils.TempDataSetField[1].empty:
    weatherNameT0, plantNameT0, agricultureNameT0 = pages_utils.getDataFiled(0, pages_utils.TempDataSetField[0])
    weatherNameT1, plantNameT1, agricultureNameT1 = pages_utils.getDataFiled(1, pages_utils.TempDataSetField[1])
    # weatherNameList = weatherNameT1 + weatherNameT0
    # plantNameList = plantNameT1 + plantNameT1
    # agricultureNameList = agricultureNameT1 + agricultureNameT1
    # if not pages_utils.TempDataSetField[2].empty:
    weatherNameT2, plantNameT2, agricultureNameT2 = pages_utils.getDataFiled(2, pages_utils.TempDataSetField[2])
    # print('获取多个特征')
    # print(weatherNameT2)
    weatherNameT2H = []
    for weatherNameT22 in weatherNameT2:
        # print(weatherNameT22)
        if isinstance(weatherNameT22, str):
            weatherNameT2H += weatherNameT22.split(',')
    weatherNameList = weatherNameT1 + weatherNameT2H + weatherNameT0
    plantNameList = plantNameT1 + plantNameT2 + plantNameT1 + plantNameT0
    agricultureNameList = agricultureNameT1 + agricultureNameT0
    # 按照数据类型显示左侧字段或特征
    result1 = pages_utils.multiselect_all(
        st, '全选-气象数据', filterUnique(weatherNameList, pages_utils.reservedField),
        'tempTemperature', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-植保特征', filterUnique(plantNameList, pages_utils.reservedField),
        'tempPlant', 'collapsed')
    result3 = pages_utils.multiselect_all(
        st, '全选-地理遥感数据', filterUnique(agricultureNameList, pages_utils.reservedField),
        'tempAgriculture', 'collapsed')

# ===============显示右上处理方法选项===============
with (featureCCM):
    st.markdown("##### 特征计算方法")
    col1, col2 = st.columns(2)
    with col1:
        option15 = st.checkbox('降雨日数计算', key='checkbox1', on_change=clear_other, args=[1])
        option16 = st.checkbox('降水累积量计算', key='checkbox2', on_change=clear_other, args=[2])
    with col2:
        option17 = st.checkbox('基于活动积温的生育期计算', key='checkbox3', on_change=clear_other, args=[3])
        option14 = st.checkbox('活动积温计算', key='checkbox0', on_change=clear_other, args=[0])

    st.markdown('---')
    # ===============显示和处理右中各个处理方法设置参数===============
    if option14:
        colFC31, colFC32 = st.columns([0.3, 0.6])
        with colFC31:
            d1 = st.date_input("开始时间(默认处理各年数据集)",
                               value=datetime.date(2024, 1, 1),
                               format='MM/DD/YYYY',
                               )
            d2 = st.date_input("结束时间", format='MM/DD/YYYY', value=datetime.date(2024, 8, 9))
            st.session_state["featureMethodName"]['param1'] = str(d1)
            st.session_state["featureMethodName"]['param2'] = str(d2)
        with colFC32:
            st.info('方法描述\n'
                    '* 积累加某个时间段内活动温度以计算积温\n', icon="ℹ️")
            img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'featureP3.png'))
            st.image(img)
    if option15:
        colFC11, colFC12 = st.columns([0.3, 0.6])
        with colFC11:
            d1 = st.date_input("开始时间(默认处理各年数据集)",
                               value=datetime.date(2024, 1, 1),
                               format='MM/DD/YYYY',
                               )
            d2 = st.date_input("结束时间", format='MM/DD/YYYY', value=datetime.date(2024, 1, 1))
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
        with colFC12:
            st.info('方法描述\n'
                    '* 基于特定时间段内降雨量和阈值及连续时长计算有效降雨日数\n', icon="ℹ️")
            img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'featureP1.png'))
            st.image(img)
    if option16:
        colFC21, colFC22 = st.columns([0.3, 0.6])
        with colFC21:

            option3 = st.selectbox(
                '降水累积量计算',
                ('指定日期', '月累积降水量', '旬累积降水量'))
            st.session_state["featureMethodName"]['param1'] = option3

            if option3 == '指定日期':
                sd1 = st.date_input("开始时间", value=datetime.date(2024, 7, 1))
                ed1 = st.date_input("结束时间", value=datetime.date(2024, 8, 1))
                st.session_state["featureMethodName"]['param2'] = sd1.strftime('%m-%d')
                st.session_state["featureMethodName"]['param3'] = ed1.strftime('%m-%d')
        with colFC22:
            st.info('方法描述\n'
                    '* 积累某个时间段内降雨量以计算降水累量\n', icon="ℹ️")
            img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'featureP2.png'))
            st.image(img)
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

    # =======================添加处理至任务清单=======================
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clear_all)
    if btn:
        # 检测用户行为-数据中含缺失值
        tempMissingColumn = []
        for column in pages_utils.TempDataSet[1].columns:
            # 获取每个字段的非缺失值数量
            if pages_utils.TempDataSet[1][column].isnull().any():
                tempMissingColumn.append(column)
        if len(tempMissingColumn):
            infoMissingColumn = ' '.join(tempMissingColumn)
            # st.toast(f'数据集中以下字段含缺失值,请进行缺失值插补  \n{infoMissingColumn}', icon="⚠️")
            # time.sleep(1)
        # 测试特征方法名称正确性
        for key11, value11 in st.session_state["featureMethodName"].items():
            pass
            # print('============测试方法参数正确性============')
            # print(f"Key: {key11}, Value: {value11}")
        modelP = [value for key, value in st.session_state["featureMethodName"].items() if key != 'checkBox']
        # print(modelP)
        # if '月' in modelP[0]:
        #     print('月下载')
        #     for _ in range(12):
        #         new_data = {
        #             "编号": pages_utils.generateID(),
        #             "数据类型": '气象数据',
        #             "输入特征": mergeExcludeArray(result1, result2, result3, pages_utils.reservedField),
        #             "特征计算方法": getCheckboxName(st.session_state["featureMethodName"]['checkBox']),
        #             "方法参数": modelP,
        #             "时间": datetime.datetime.now().time(),
        #             "处理状态": False}
        #         print('======================特征计算-添加任务清单记录======================')
        #         print(new_data)
        #         pages_utils.TempDataSetField[2].loc[len(pages_utils.TempDataSetField[2])] = new_data
        # elif '旬' in modelP[0]:
        #     for _ in range(36):
        #         new_data = {
        #             "编号": pages_utils.generateID(),
        #             "数据类型": '气象数据',
        #             "输入特征": mergeExcludeArray(result1, result2, result3, pages_utils.reservedField),
        #             "特征计算方法": getCheckboxName(st.session_state["featureMethodName"]['checkBox']),
        #             "方法参数": modelP,
        #             "时间": datetime.datetime.now().time(),
        #             "处理状态": False}
        #         print('======================特征计算-添加任务清单记录======================')
        #         print(new_data)
        #         pages_utils.TempDataSetField[2].loc[len(pages_utils.TempDataSetField[2])] = new_data
        # else:
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": '气象数据',
            "输入特征": mergeExcludeArray(result1, result2, result3, pages_utils.reservedField),
            "特征计算方法": getCheckboxName(st.session_state["featureMethodName"]['checkBox']),
            "方法参数": modelP,
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
                pages_utils.TempDataSetField[2], height=190, width=900,
                column_order=["编号", "数据类型", "输入特征", "备选特征", "特征计算方法", '时间', '处理状态'],
                disabled=["数据类型", "时间", '处理状态'], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])
            btn2 = interval_col33.button('运行', on_click=onRun)
    elif st.session_state.page13 == 1:
        # =======================显示右下可视化图表=======================
        with placeholder.container():
            st.markdown('##### 可视化')
            idFMethods = pages_utils.TempDataSetField[2]["特征计算方法"].tolist()
            # inputFields = pages_utils.TempDataSetField[2]["输入特征"].tolist()

            # 若无方法处理,则直接跳过该环节
            if len(idFMethods):
                # 创建新的从 1 开始的编号列表
                new_ids = list(range(0, len(idFMethods)))
                # 创建标签页并重新命名记录
                new_ids = [f'记录编号_{h}' for h in new_ids]

                tt1 = st.tabs(new_ids)
                print(st.session_state["FCVisualInformation"])
                for o in range(len(idFMethods)):
                    with tt1[o]:
                        if not st.session_state["FCVisualInformation"][o]:
                            st.warning('计算错误出错', icon="⚠️")
                            continue
                        # 创建DataFrame
                        data_after = st.session_state["FCVisualInformation"][o]['after']
                        # 特征名称
                        dataColumn = st.session_state["FCVisualInformation"][o]['column']
                        # 删除含有缺失值的行
                        data_after = data_after.dropna()
                        # 去除重复值
                        data_after = data_after.drop_duplicates()

                        if idFMethods[o] == '基于活动积温的生育期计算':
                            # 选择最多8个纬度
                            top_stations = data_after['纬度'].value_counts().nlargest(8).index
                            df_filtered_stations = data_after[data_after['纬度'].isin(top_stations)]

                            # 选择最多3个年份
                            top_years = data_after['年'].value_counts().nlargest(3).index
                            df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                            df_filtered['地区'] = df_filtered['纬度'].astype(str) + " " + df_filtered['经度'].astype(
                                str)

                            # 绘制折线图
                            plt.figure(figsize=(10, 6))
                            sns.lineplot(
                                data=df_filtered,
                                x="地区",
                                y=dataColumn,
                                hue="年",
                                marker="o"
                            )
                            # 设置标签和标题
                            plt.gca().set_xlabel("")  # 隐藏x轴标题
                            plt.xticks(rotation=30)  # x轴标签旋转65度
                            plt.ylabel(f'{dataColumn}(Day Of Year)')
                            # 设置整数天
                            plt.gca().yaxis.get_major_locator().set_params(integer=True)
                            plt.figtext(0.5, -0.1,
                                        f'图{st.session_state.IMAGECOUNT} 部分地区各年份{dataColumn}',
                                        ha='center', fontsize=16)
                            st.pyplot(plt)
                        elif idFMethods[o] == '降水累积量计算':

                            # 时期范围名称修剪
                            if '-' in dataColumn:
                                integratedDataColumnT = dataColumn.split('_')
                                integratedDataColumn = integratedDataColumnT[0] + '至' + integratedDataColumnT[1] + \
                                                       integratedDataColumnT[2]
                            else:
                                integratedDataColumnT = dataColumn.split('_')
                                integratedDataColumn = integratedDataColumnT[0] + integratedDataColumnT[1]
                            # 选择最多8个纬度
                            top_stations = data_after['纬度'].value_counts().nlargest(8).index
                            df_filtered_stations = data_after[data_after['纬度'].isin(top_stations)]
                            # 选择最多5个年份
                            top_years = data_after['年'].value_counts().nlargest(5).index
                            df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                            df_filtered['地区'] = df_filtered['纬度'].astype(str) + " " + df_filtered['经度'].astype(
                                str)
                            # 绘制柱状图
                            plt.figure(figsize=(10, 6))
                            sns.barplot(
                                data=df_filtered,
                                x="地区",
                                y=dataColumn,
                                hue="年",
                                dodge=True,
                                saturation=1
                            )
                            # 设置标签和标题
                            plt.gca().set_xlabel("")  # 隐藏x轴标题
                            plt.xticks(rotation=30)  # x轴标签旋转65度
                            plt.ylabel("降水累积量(mm)")
                            plt.figtext(0.5, -0.1,
                                        f'图{st.session_state.IMAGECOUNT} 部分地区各年份{integratedDataColumn}图',
                                        ha='center', fontsize=16)
                            st.pyplot(plt)
                            st.session_state.IMAGECOUNT += 1
                        elif idFMethods[o] == '降雨日数计算':
                            # 时期范围名称修剪
                            integratedDataColumnRT = dataColumn.split('_')
                            integratedDataColumnR = integratedDataColumnRT[0] + '至' + integratedDataColumnRT[1] + \
                                                    integratedDataColumnRT[2]
                            # 选择最多8个纬度
                            top_stations = data_after['纬度'].value_counts().nlargest(8).index
                            df_filtered_stations = data_after[data_after['纬度'].isin(top_stations)]

                            # 选择最多5个年份
                            top_years = data_after['年'].value_counts().nlargest(5).index
                            df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                            # 创建一个新的列，将纬度和经度组合成一个标签
                            df_filtered['地区'] = df_filtered['纬度'].astype(str) + " " + df_filtered['经度'].astype(
                                str)
                            # 绘制折线图
                            plt.figure(figsize=(10, 6))
                            sns.lineplot(
                                data=df_filtered,
                                x="地区",
                                y=dataColumn,
                                hue="年",
                                marker="o"
                            )
                            # 设置标签和标题
                            # plt.xlabel("地区")
                            plt.ylabel("降雨日数(天)")
                            plt.gca().set_xlabel("")  # 隐藏x轴标题
                            plt.xticks(rotation=30)  # x轴标签旋转65度
                            plt.figtext(0.5, -0.1,
                                        f'图{st.session_state.IMAGECOUNT} 部分地区各年份{integratedDataColumnR}',
                                        ha='center', fontsize=16)
                            st.pyplot(plt)
                            st.session_state.IMAGECOUNT += 1
                        elif idFMethods[o] == '活动积温计算':
                            st.info('该功能优化中', icon="ℹ️️")

            else:
                st.info('跳过特征计算', icon="ℹ️️")
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('返回', on_click=firstPage)
