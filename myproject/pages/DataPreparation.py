import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from PIL import Image
from matplotlib.ticker import MaxNLocator
from st_pages import hide_pages
import streamlit_antd_components as sac
from streamlit import switch_page
from streamlit_pills import pills

from lib.share import RESOURCE_IMAGES_PATH, PAGES_PATH
from lib.utils import filterUnique
from pages import pages_utils
from pages.modelandmethod.PretreatmentMethod import PretreatmentMethod

st.set_page_config(
    layout="wide",
    initial_sidebar_state='collapsed'
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
# # 取消链接跳转
# st.markdown("""
#     <style>
#     .st-emotion-cache-gi0tri.e1nzilvr2 {display: none;}
#     </style>
#     """, unsafe_allow_html=True)
st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")
if 'pageDPIsInit' not in st.session_state:
    st.session_state.pageDPIsInit = 0

    # 检查异常值
    has_missing = pages_utils.TempDataSet[0].isnull().values.any()
    if not has_missing:
        st.toast("未发现缺失值", icon="ℹ️️")
    else:
        pass
        # st.toast('发现缺失值,已根据默认配置添加任务至清单', icon="ℹ️")


@st.dialog("气象数据预处理")
def timeResolutionUnification():
    # 检测预处理数据是否符合日值且无缺失值
    if pages_utils.TempDataSet[1].isnull().any().any():
        st.warning('数据集含缺失值，请进行缺失值插补', icon="⚠️")

    st.info('为了便于后续各环节数据处理，现对数据集时间分辨率进行统一', icon="ℹ️️")
    # 分辨率统一
    time = st.selectbox('选择时间分辨率', options=('日值', '每5天', '旬值', '月值'))
    if st.button("确认"):
        st.session_state.timeResolution = time
        st.rerun()


# 时间分辨率统一
if 'timeResolution' not in st.session_state:
    if st.session_state.modelingType == '动态模型':
        timeResolutionUnification()
    else:
        st.session_state.timeResolution = '日值'

# 处理方法内容记录(任务清单各项值)
if "preMethodName" not in st.session_state:
    st.session_state["preMethodName"] = {
        'checkBox': None
    }
if 'DPVisualInformation' not in st.session_state:
    st.session_state["DPVisualInformation"] = []
# 处理方法个数
checkBoxNum = 2
# 设置可视化图表中文
plt.rcParams['font.sans-serif'] = 'SimHei'
plt.rc("font", family='Microsoft YaHei')

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
# 隐藏markdown锚点链接
st.markdown("""
    <style>
    .stApp a:first-child {
        display: none;
    }

    .css-15zrgzn {display: none}
    .css-eczf16 {display: none}
    .css-jn99sy {display: none}
    </style>
    """, unsafe_allow_html=True)
st.header('气象数据预处理',
          help='清洗气象数据如异常和缺失值，以免影响建模', divider='grey', anchor=False)

sac.steps(
    items=[
        sac.StepsItem(title='原始建模数据', disabled=True),
        sac.StepsItem(title='气象数据预处理', disabled=True),
        sac.StepsItem(title='特征计算', disabled=True),
        sac.StepsItem(title='特征优选', disabled=True),
        sac.StepsItem(title='模型构建', disabled=True),
        sac.StepsItem(title='模型应用', disabled=True),
    ], index=1, color='#008000'
)

emptyHeadDPP = st.empty()


# 检测用户输入行为
def detectUserInput():
    # 1.添加处理
    # 1.1输入特征（空）
    # 1.2参数（空）
    # 1.3方法(空或对应方法无法处理)
    print()


# 获取选项值对应名称
def getCheckboxName(checkbox):
    # if checkbox == 'checkbox0':
    #     return '剔除异常值'
    if checkbox == 'checkbox0':
        return '剔除异常值及插补'
    elif checkbox == 'checkbox1':
        return '缺失值插补'


# 取消选中所有选项
def clearOption():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["preMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    # 若已经在可视化展示状,则默认返回任务清单
    # st.session_state.page12 = 0
    return


# 取消选中外其他所有选项
def clear_other(key1):
    # st.markdown(key)
    for h in range(checkBoxNum):
        if h != key1:
            st.session_state[f'checkbox{h}'] = False
    return


# 控制左侧表格不同数据集显示
def firstPage(): st.session_state.page12 = 0


# 控制左侧表格不同数据集显示
def nextPage(): st.session_state.page12 += 1


# 运行任务清单中所有方法
def onRun():
    if '预处理后数据集' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('预处理后数据集')
    st.session_state.page12 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[1]["编号"]
    fields = pages_utils.TempDataSetField[1]["输入字段"]
    methodParam = pages_utils.TempDataSetField[1]["方法参数"]
    isHandledFlags = pages_utils.TempDataSetField[1]["处理状态"]
    methodList = pages_utils.TempDataSetField[1]["预处理方法"]
    # ===============根据名称匹配调用并执行各个处理方法===============
    with emptyHeadDPP:
        with st.spinner('处理数据中...'):
            # 若为空则跳过该步骤
            if idNumber.empty:
                pages_utils.TempDataSet[1] = pages_utils.TempDataSet[0]
                st.session_state["leftTabs"].pop(0)

            afterHandleData = None
            for indexT, (tempMethod, isHandled) in enumerate(zip(methodList, isHandledFlags)):
                # 检查方法是否已执行
                if isHandled:
                    continue
                # 第一次使用原始数据集,而后基于预处理后数据集多次处理
                if pages_utils.TempDataSet[1].shape[0] == 0:
                    dataFrameTemp = pages_utils.TempDataSet[0]
                else:
                    dataFrameTemp = pages_utils.TempDataSet[1]

                try:
                    # 使用处理后最新的字段内容
                    reservedField = pages_utils.TempDataSet[0].columns.tolist()
                    # print(f'=============测试保留字段-{reservedField}=============')
                    newDataColumn = fields[indexT]

                    DPVisualInformationTemp = {'before': dataFrameTemp[newDataColumn[0]]}

                    if tempMethod == '缺失值插补':
                        (afterHandleData, missingValueBefore, missingValueAfter,
                         newDataColumn) = PretreatmentMethod(
                            dataFrameTemp,
                            fields[indexT], reservedField).linearInterpolation(methodParam[indexT])
                        # 显示填补信息
                        st.toast(
                            f'填补字段:{fields[indexT][0]}  \n填补缺失值:{str(missingValueBefore - missingValueAfter)}条  \n' +
                            f'剩余缺失值:{missingValueAfter}条', icon='✅')
                    elif tempMethod == '剔除异常值':
                        (afterHandleData, lengthBefore, lengthAfter,
                         newDataColumn) = PretreatmentMethod(
                            dataFrameTemp,
                            fields[indexT], reservedField).outlierEliminator(methodParam[indexT])
                        # 显示填补信息
                        st.toast(f'剔除异常值个数:{str(lengthBefore - lengthAfter)}' +
                                 '\n' +
                                 f'剩余条数:{lengthAfter}', icon='✅')
                    elif tempMethod == '剔除异常值及插补':
                        afterHandleData = PretreatmentMethod(
                            dataFrameTemp,
                            fields[indexT], reservedField).outlierEliminatorInterpolation(methodParam[indexT])
                        # 显示填补信息
                        st.toast(f'剔除异常值并插补完成', icon='✅')
                except BaseException as e:
                    st.toast(f'{tempMethod}运行失败  \n错误:{e}', icon="⚠️")
                    # 不自动跳转至可视化
                    st.session_state.page12 = 0
                    # 删除最后一条记录
                    pages_utils.TempDataSetField[1] = pages_utils.TempDataSetField[1].drop(
                        pages_utils.TempDataSetField[1].index[-1])
                # 若执行正确则合并数据
                else:
                    # ===============合并处理后数据集===============
                    intersection_cols = pages_utils.getIntersectionCols(
                        pages_utils.TempDataSet[1], afterHandleData
                    )

                    pages_utils.TempDataSet[1] = pd.merge(
                        afterHandleData, pages_utils.TempDataSet[1],
                        on=intersection_cols, how="left")
                    # print('======================预处理后数据集======================')

                    # ===============更新左侧显示内容===============
                    # print(f'更新左侧显示内容:{newDataColumn}')
                    DPVisualInformationTemp['name'] = tempMethod
                    DPVisualInformationTemp['after'] = pages_utils.TempDataSet[1][newDataColumn]
                    # 可视化信息添加
                    st.session_state["DPVisualInformation"].append(DPVisualInformationTemp)
                    # print('=====================展示可视化内容======================')
                    # print(st.session_state["DPVisualInformation"])
                    update_values = {
                        "预处理后字段": newDataColumn,
                        "大小": '1*' + str(len(afterHandleData[fields[indexT]])),
                        "时间": datetime.datetime.now().time(),
                        "处理状态": True
                    }
                    # 查找要更新的数据记录
                    for index, row in pages_utils.TempDataSetField[1].iterrows():
                        if row["编号"] == idNumber[indexT]:
                            for key1, value1 in update_values.items():
                                pages_utils.TempDataSetField[1].loc[index, key1] = value1
                print('===================预处理数据集===================')
                print(pages_utils.TempDataSet[1])

    # st.toast('本气象数据预处理环节的数据已保持至下一环节', icon="ℹ️")


# ==============================界面==============================
# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.7, 0.5])
with dataPCV:
    with st.container(border=True):
        # st.markdown("##### 数据与特征")
        # ===============显示左侧数据与特征表格===============
        # 根据st.session_state.page12的值刷新表格
        # placeholder1 = st.empty()
        # if st.session_state.page12 == 0:
        #     with placeholder1.container():
        #         tt1 = st.tabs(['原始数据'])
        #         with tt1[0]:
        #             st.data_editor(
        #                 pages_utils.TempDataSet[0],
        #                 height=220, width=800, )
        #
        # if st.session_state.page12 == 1:
        #     with placeholder1.container():
        #         if pages_utils.TempDataSet[0].columns.tolist() == pages_utils.TempDataSet[1].columns.tolist():
        #             tt = st.tabs(['预处理后数据集'])
        #             with tt[0]:
        #                 st.data_editor(
        #                     pages_utils.TempDataSet[1],
        #                     height=220, width=800, )
        #         else:
        #             tt = st.tabs(['原始数据', '预处理后数据集'])
        #             with tt[0]:
        #                 st.data_editor(
        #                     pages_utils.TempDataSet[0],
        #                     height=220, width=800, )
        #             with tt[1]:
        #                 st.data_editor(
        #                     pages_utils.TempDataSet[1],
        #                     height=220, width=800, )
        #                     column_order=column)

        # ===============显示左下字段或特征及获取===============
        # weatherNameList, plantNameList, agricultureNameList = ['无1'], ['无2'], ['无3']
        # if not pages_utils.TempDataSetField[0].empty:
        weatherNameT1, plantNameT1, agricultureNameT1 = pages_utils.getDataFiled(0, pages_utils.TempDataSetField[0])
        # weatherNameList = weatherNameT1
        # plantNameList = plantNameT1
        # agricultureNameList = agricultureNameT1
        # if not pages_utils.TempDataSetField[1].empty:
        # weatherNameT2, plantNameT2, agricultureNameT2 = pages_utils.getDataFiled(1, pages_utils.TempDataSetField[1])
        # weatherNameList = weatherNameT1 + weatherNameT2
        # plantNameList = plantNameT1 + plantNameT2
        # agricultureNameList = agricultureNameT1 + agricultureNameT2
        # 按照数据类型显示左侧字段或特征
        # result1 = pages_utils.multiselect_all(
        #     st, '全选-', filterUnique(weatherNameList, pages_utils.reservedField),
        #     'tempTemperature', 'collapsed')
        st.markdown("##### 原始建模数据集")
        st.data_editor(pages_utils.TempDataSet[0], height=247, width=800, )
        # st.markdown('---')
    with st.container(border=True):
        st.markdown("##### 气象数据字段选择")
        needHandledList = []
        fieldT = filterUnique(pages_utils.TempDataSet[0],
                              plantNameT1 + agricultureNameT1 + pages_utils.reservedField)
        if not st.session_state.pageDPIsInit:
            if len(fieldT) != 0:
                # 检查异常值
                for filedTTT1 in fieldT:
                    isNan = PretreatmentMethod.detectGeneralNumber(
                        pages_utils.TempDataSet[0], filedTTT1, 'nan')
                    if isNan:
                        needHandledList.append(filedTTT1)
                # if len(needHandledList) == 0:
                #     st.toast("未发现缺失值", icon="ℹ️️")

                # st.toast("检测到缺失值，已添加至任务清单", icon="ℹ️️")
            else:
                needHandledList = ['待原始建模数据上传']

        # result1 = st.multiselect("s", options=needHandledList,
        #                          default=needHandledList, label_visibility='collapsed')
        # if len(needHandledList) == 0:
        #     needHandledList = ['无缺失值']
        result1 = pills("", fieldT,
                        label_visibility='collapsed')

        result1 = [result1]
        # result2 = pages_utils.multiselect_all(
        #     st, '全选-植保数据', filterUnique(plantNameList, pages_utils.reservedField),
        #     'tempPlant', 'collapsed')
        # result3 = pages_utils.multiselect_all(
        #     st, '全选-地理遥感数据', filterUnique(agricultureNameList, pages_utils.reservedField),
        #     'tempAgriculture', 'collapsed')

        st.markdown('---')
        # ===============显示右上预处理方法选项===============
        st.markdown("##### 预处理方法")
        # with tab1:
        col1, col2 = st.columns(2)
        with col1:
            agree = st.checkbox('剔除异常值及插补', key='checkbox0', on_change=clear_other, args=[0])
        with col2:
            # agree10 = st.checkbox("缺失值插补", key='checkbox1', on_change=clear_other, args=[1])
            agree10 = None
        paramPlaceHolder = st.empty()
        # ===============显示和处理右中各个处理方法设置参数===============
        if agree10:
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
            st.markdown('---')

            coll11, coll22 = st.columns([0.3, 0.6])
            with coll11:
                option = st.selectbox(
                    '插补方法',
                    options=('线性插值', '自定义'))
                st.session_state["preMethodName"]['param1'] = option
                if option == '自定义':
                    num = st.text_input('缺失值', value=np.nan)
                    num1 = st.text_input('插补值')
                    st.session_state["preMethodName"]['param2'] = num
                    st.session_state["preMethodName"]['param3'] = num1
            with coll22:
                latext = '* 公式:' + r'''
                $$ 
                y = y_0 + (y_1 - y_0) \frac{(x - x_0)}{(x_1 - x_0)} 
                $$ 
                '''
                st.info('方法介绍\n'
                        '* 描述:使用缺失值前后最近的两个非缺失值填充\n' +
                        latext, icon="ℹ️")
                img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'Figure_5.png'))
                st.image(img)
            # st.markdown('---')
        if agree:
            # 异常值检测(温度和降水)
            # 显示缺失值信息
            # info = '疑似异常字段:\n'
            # 第一次使用原始数据集,而后基于预处理后数据集多次处理
            if pages_utils.TempDataSet[1].shape[0] == 0:
                dataFrameTemp = pages_utils.TempDataSet[0]
            else:
                dataFrameTemp = pages_utils.TempDataSet[1]

            # infoT1 = PretreatmentMethod.detectLinearInterpolationWeather(dataFrameTemp)
            # infoT2 = PretreatmentMethod.detectLinearInterpolationRain(dataFrameTemp)
            # columnList, lowNum, upNum, lowCount, upCount = PretreatmentMethod.detect_outliers_iqr(dataFrameTemp,
            #                                                                                       pages_utils.reservedField)
            # info1 = '无异常字段\n'
            # if not len(columnList):
            #     st.info(f"{info1}\n", icon="ℹ️️")
            # else:
            #     st.info(f"{info1}\n", icon="ℹ️️")

            # infoT1 = ''
            # for columnT, lowNumT, upNumT, lowCountT, upCountT in zip(columnList, lowNum, upNum, lowCount, upCount):
            #     infoT1 += f"* {columnT} 下限:{round(lowNumT, 3)} 个数:{lowCountT} 上限:{round(upNumT, 3)} 个数:{upCountT}\n"
            # st.warning(f"{info}  \n{infoT1}", icon="⚠️")
            # st.markdown('---')

            coll11, coll22 = st.columns([0.3, 0.6])
            with coll11:
                optionDP1 = st.selectbox(
                    '异常值查找方式',
                    ('具体数值', '范围数值'))

                if optionDP1 == '范围数值':
                    detectUp, detectLow = 0.1, 0.1
                    if '温度' == result1[0]:
                        detectUp, detectLow = 50, -30
                    elif '降水' == result1[0]:
                        detectUp, detectLow = 1500, 0
                    number2 = st.text_input("大于以下数值外的值", value=detectUp)
                    number3 = st.text_input("小于以下数值外的值", value=detectLow)
                    infoT1Low, infoT1Up = PretreatmentMethod.detectGeneralScope(dataFrameTemp, result1[0], float(number2),
                                                                                float(number3))
                    if infoT1Low or infoT1Up:
                        st.warning(f"存在异常数据:  \n超过上限数据:{infoT1Up}条  \n超过下限数据:{infoT1Low}条", icon="⚠️")
                    else:
                        st.info(f"无异常数据\n", icon="ℹ️️")
                    option = st.selectbox(
                        '插补方法',
                        options='线性插值')
                    st.session_state["preMethodName"]['param1'] = optionDP1
                    st.session_state["preMethodName"]['param2'] = number2
                    st.session_state["preMethodName"]['param3'] = number3
                    if number3:
                        # 检测剔除参数最小值>最大值
                        if PretreatmentMethod.detectLinearInterpolationParam([number2, number3]):
                            st.toast('剔除数据的最小值>最大值', icon="⚠️")
                elif optionDP1 == '具体数值':
                    num = st.text_input('异常值', value=np.nan)
                    infoT1 = PretreatmentMethod.detectGeneralNumber(dataFrameTemp, result1[0], num)
                    if infoT1:
                        st.warning(f"存在异常数据:{infoT1}条", icon="⚠️")
                    else:
                        st.info(f"无异常数据\n", icon="ℹ️️")
                    num1 = st.text_input('插补值')
                    st.session_state["preMethodName"]['param1'] = optionDP1
                    st.session_state["preMethodName"]['param2'] = num
                    st.session_state["preMethodName"]['param3'] = num1

            with coll22:
                st.info('方法介绍\n'
                        '* 描述:剔除单个数值或指定范围内的异常值，然后对其进行自定义插补或线性插值\n', icon="ℹ️")
                img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'Figure_5.png'))
                st.image(img)
        # =======================添加处理至任务清单=======================

        interval_col1, interval_col2 = st.columns([5, 1])
        btn = interval_col2.button('添加处理', on_click=clearOption)
        if btn:
            # 检测用户行为-输入特征为空(预处理方法空判定未添加)
            # if not len(result1 + result2 + result3):
            if not len(result1):

                st.toast('未选择特征  \n请重新添加处理', icon="⚠️")
            else:
                # 获取数据类型
                if result1:
                    dataType = '气象数据'
                # elif result2:
                #     dataType = '植保数据'
                # elif result3:
                #     dataType = '地理遥感数据'
                new_data = {
                    "编号": pages_utils.generateID(),
                    "数据类型": dataType,
                    "输入字段": filterUnique(result1, pages_utils.reservedField),
                    "预处理后字段": None,
                    "预处理方法": getCheckboxName(st.session_state["preMethodName"]['checkBox']),
                    "方法参数": [value for key, value in st.session_state["preMethodName"].items() if
                                 key != 'checkBox'],
                    "时间": datetime.datetime.now().time(), "处理状态": False}
                print('======================预处理-添加任务清单记录======================')
                print(new_data)
                pages_utils.TempDataSetField[1].loc[len(pages_utils.TempDataSetField[1])] = new_data
                st.rerun()

    # =======================添加处理至任务清单=======================
    # 自动添加
    # if not st.session_state.pageDPIsInit:
    #     st.session_state.pageDPIsInit += 1
    #     for fieldTT2 in needHandledList:
    #         if fieldTT2 == '无缺失值':
    #             continue
    #         new_dataT = {
    #             "编号": pages_utils.generateID(),
    #             "数据类型": '气象数据',
    #             "输入字段": [fieldTT2],
    #             "预处理后字段": None,
    #             "预处理方法": '剔除异常值及插补',
    #             "方法参数": ['具体数值', 'nan', ''],
    #             "时间": datetime.datetime.now().time(),
    #             "处理状态": False}
    #         # print('======================预处理-添加任务清单记录======================')
    #         # print(new_dataT)
    #         pages_utils.TempDataSetField[1].loc[len(pages_utils.TempDataSetField[1])] = new_dataT
    # interval_col1, interval_col2 = st.columns([5, 1])
    # btn = interval_col2.button('添加处理', on_click=clearOption)
    # btn = None

with dataPCM:
    # =======================显示右下内容=======================
    # placeholder = st.empty()
    # if st.session_state.page12 == 0:
    # pages_utils.TempDataSet[1] = pages_utils.TempDataSet[0].copy()
    # # 初始化添加旬、月字段
    # pages_utils.TempDataSet[1]['MonthOfYear'] = pages_utils.TempDataSet[1]['DayOfYear'].apply(
    #     lambda x: (x - 1) // 30 + 1)  # 简化的月份计算，实际应用中可能需要更精确的方法
    # pages_utils.TempDataSet[1]['DecadeOfYear'] = pages_utils.TempDataSet[1]['DayOfYear'].apply(
    #     lambda x: (x - 1) // 10 + 1)  # 计算旬

    # =======================显示右下任务清单表格=======================
    with st.container(border=True):
        st.markdown('##### 任务清单')
        # st.info('本环节已将含缺失值的字段添加至任务清单，待进行自动插补处理，用户也可自行定义异常值进行插补处理', icon="ℹ️")
        # want_to_contribute = st.button("跳转可视化")
        # if want_to_contribute:
        #     switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\ModelEvaluation.py")
        pages_utils.TempDataSetField[1] = st.data_editor(
            pages_utils.TempDataSetField[1], height=190, width=900,
            column_order=["数据类型", "输入字段", "预处理方法", '时间', '处理状态'],
            disabled=["数据类型", "输入字段", "预处理后字段", "时间", '处理状态'], num_rows="dynamic", )
        interval_col34, interval_col33 = st.columns([6, 1])
        with interval_col33:
            # residualField = [arr for arr in pages_utils.TempDataSet[0].columns if
            #                  arr not in mergeArray4(
            #                      ['经度', '纬度',
            #                       "年", "DayOfYear"], result1, result2, result3)]
            # print(f'剩余字段{residualField}')
            # 默认保留上一环节所有字段
            # reservedFiled = pages_utils.multiselect_all(
            #     st, '全选',
            #     residualField,
            #     'temp1', 'collapsed')
            btn2 = st.button('运行', on_click=onRun)

    # btn2 = interval_col33.button('运行', on_click=onRun)
    placeholder = st.empty()
    # =======================显示右下可视化图表=======================
    # elif st.session_state.page12 == 1:
    # 运行一次就一直显示结果

    if st.session_state.page12 >= 1:
        with placeholder.container(border=True):
            st.markdown('##### 预处理后数据集')
            # st.markdown("##### 原始建模")
            st.data_editor(
                data=pd.DataFrame(pages_utils.TempDataSet[1].columns.tolist(), columns=["预处理后数据字段"]),
                height=192, width=800, )

            # idPreMethods = pages_utils.TempDataSetField[1]["预处理方法"].tolist()
            # inputFields = pages_utils.TempDataSetField[1]["输入字段"].tolist()
            # # 若无方法处理,则直接跳过该环节
            # if len(idPreMethods):
            #     # 创建新的从 1 开始的编号列表
            #     new_ids = list(range(0, len(idPreMethods)))
            #
            #     # 创建标签页并重新命名记录
            #     new_ids = [f'记录编号_{h}' for h in new_ids]
            #
            #     # tt1 = st.tabs(new_ids)
            #     tt1 = st.tabs([' ', ' '])
            #
            #     for o in range(len(idPreMethods)):
            #         with tt1[o]:
            #             if idPreMethods[o] == '缺失值插补':
            #                 data_before_temp = st.session_state["DPVisualInformation"][o]['before']
            #                 data_after_temp = st.session_state["DPVisualInformation"][o]['after']
            #                 # print(inputFields[o][0])
            #                 data_before = pd.DataFrame({inputFields[o][0]: data_before_temp})
            #                 data_after = pd.DataFrame({inputFields[o][0]: data_after_temp})
            #                 # 查找缺失值的索引
            #                 missing_indices = data_before[data_before[inputFields[o][0]].isna()].index
            #                 # print(f'缺失索引:{missing_indices}')
            #                 # 获取第一个缺失值的索引
            #                 first_missing_index = missing_indices[0]
            #                 # 获取第一个缺失值的行号
            #                 # first_missing_index = 130
            #                 # print(f"第一个缺失值的行号: {first_missing_index}")
            #                 # 计算前5行和后5行的起始和结束索引
            #                 start_index = max(first_missing_index - 80, 0)
            #                 end_index = min(first_missing_index + 80 + 1, len(data_before))
            #                 # 取第一个缺失值对应前15行和后15行预处理数据
            #                 data_before_surrounding_data = data_before.iloc[start_index:end_index]
            #                 data_after_surrounding_data = data_after.iloc[start_index:end_index]
            #                 # 绘制对比折线图
            #                 fig, ax = plt.subplots(figsize=(10, 6))
            #                 # print(pages_utils.TempDataSet[1]['DayOfYear'])
            #                 # 取第一个缺失值对应前15行和后15行'经度', '纬度', '年'数据
            #                 missing_rows = \
            #                     pages_utils.TempDataSet[1].loc[
            #                         missing_indices, ['经度', '纬度', '年', 'DayOfYear']].to_dict(
            #                         'records')[0]
            #                 province, station, year = missing_rows['经度'], missing_rows['纬度'], missing_rows[
            #                     '年']
            #                 # print(missing_rows['DayOfYear'])
            #                 # 整理前后15天dayOfYear为x轴
            #                 # 提取数据列，获取从 start_index 到 end_index 范围内的行数
            #                 # 生成从 start_index 到 end_index 的数字序列
            #                 figure_x = pd.DataFrame({'row': list(range(start_index, end_index))})
            #                 # 绘制插补前的折线图
            #                 plt.plot(figure_x, data_before_surrounding_data[inputFields[o][0]],
            #                          label='原始数据',
            #                          color='black',
            #                          linestyle='-', marker='o')
            #                 # 绘制插补后的折线图
            #                 plt.plot(figure_x, data_after_surrounding_data[inputFields[o][0]],
            #                          label='插补后数据', color='blue',
            #                          linestyle='--',
            #                          marker='o', alpha=0.3)
            #                 plt.xlabel('行号')
            #                 ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            #                 plt.ylabel(inputFields[o][0])
            #                 plt.figtext(0.5, -0.01,
            #                             f'图{st.session_state.IMAGECOUNT} {inputFields[o][0]}字段部分数据插补前后对比图',
            #                             ha='center', fontsize=16)
            #                 plt.legend()
            #                 st.pyplot(fig)
            #                 st.session_state.IMAGECOUNT += 1
            #             elif idPreMethods[o] == '剔除异常值':
            #                 # 剔除异常值-箱型图
            #                 # 准备数据
            #                 data_before = st.session_state["DPVisualInformation"][o]['before'].reset_index(drop=True)
            #                 data_after = st.session_state["DPVisualInformation"][o]['after'].reset_index(drop=True)
            #
            #                 # 创建一个DataFrame，包含处理前和处理后的数据，增加状态列用于分类
            #                 df = pd.DataFrame({
            #                     '数值': pd.concat([data_before, data_after], ignore_index=True),
            #                     '处理状态': ['预处理前'] * len(data_before) + ['预处理后'] * len(data_after)
            #                 })
            #
            #                 # 绘制一个箱型图
            #                 fig, ax = plt.subplots(figsize=(8, 6))
            #                 sns.boxplot(x='处理状态', y='数值', data=df, ax=ax)
            #
            #                 # 设置标题和标签
            #                 ax.set_ylabel(data_before.name)
            #                 plt.figtext(0.5, -0.01,
            #                             f'图{st.session_state.IMAGECOUNT} {inputFields[o][0]}字段数据剔除前后对比图',
            #                             ha='center', fontsize=16)
            #                 # fig.suptitle(f'图{st.session_state.IMAGECOUNT} {data_before.name}数据剔除前后对比箱型图',
            #                 #              fontsize=16)
            #                 ax.set_xlabel('')
            #                 st.pyplot(fig)
            #                 st.session_state.IMAGECOUNT += 1
            #
            #             elif idPreMethods[o] == '剔除异常值及插补':
            #                 pass
            #                 # st.markdown('处理字段名称：降水')
            #                 # st.markdown('最小值：0')
            #                 # st.markdown('最大值：200')
            #                 # st.markdown('标准差：3')
            #                 # st.markdown('均值：20')
            #                 # st.markdown('众数：0')
            #                 # st.markdown('中位数：10')
            #
            #                 # st.info('剔除异常值及插补功能的可视化正在优化中', icon="ℹ️")
            #                 # data_before_temp = st.session_state["DPVisualInformation"][o]['before']
            #                 # data_after_temp = st.session_state["DPVisualInformation"][o]['after']
            #                 # # print(inputFields[o][0])
            #                 # data_before = pd.DataFrame({inputFields[o][0]: data_before_temp})
            #                 # data_after = pd.DataFrame({inputFields[o][0]: data_after_temp})
            #                 # # 查找缺失值的索引
            #                 # missing_indices = data_before[data_before[inputFields[o][0]].isna()].index
            #                 # # print(f'缺失索引:{missing_indices}')
            #                 # # 获取第一个缺失值的索引
            #                 # first_missing_index = missing_indices[0]
            #                 # # 获取第一个缺失值的行号
            #                 # # first_missing_index = 130
            #                 # # print(f"第一个缺失值的行号: {first_missing_index}")
            #                 # # 计算前5行和后5行的起始和结束索引
            #                 # start_index = max(first_missing_index - 80, 0)
            #                 # end_index = min(first_missing_index + 80 + 1, len(data_before))
            #                 # # 取第一个缺失值对应前15行和后15行预处理数据
            #                 # data_before_surrounding_data = data_before.iloc[start_index:end_index]
            #                 # data_after_surrounding_data = data_after.iloc[start_index:end_index]
            #                 # # 绘制对比折线图
            #                 # fig, ax = plt.subplots(figsize=(10, 6))
            #                 # # print(pages_utils.TempDataSet[1]['DayOfYear'])
            #                 # # 取第一个缺失值对应前15行和后15行'经度', '纬度', '年'数据
            #                 # missing_rows = \
            #                 #     pages_utils.TempDataSet[1].loc[
            #                 #         missing_indices, ['经度', '纬度', '年', 'DayOfYear']].to_dict(
            #                 #         'records')[0]
            #                 # province, station, year = missing_rows['经度'], missing_rows['纬度'], missing_rows[
            #                 #     '年']
            #                 # # print(missing_rows['DayOfYear'])
            #                 # # 整理前后15天dayOfYear为x轴
            #                 # # 提取数据列，获取从 start_index 到 end_index 范围内的行数
            #                 # # 生成从 start_index 到 end_index 的数字序列
            #                 # figure_x = pd.DataFrame({'row': list(range(start_index, end_index))})
            #                 # # 绘制插补前的折线图
            #                 # plt.plot(figure_x, data_before_surrounding_data[inputFields[o][0]],
            #                 #          label='原始数据',
            #                 #          color='black',
            #                 #          linestyle='-', marker='o')
            #                 # # 绘制插补后的折线图
            #                 # plt.plot(figure_x, data_after_surrounding_data[inputFields[o][0]],
            #                 #          label='插补后数据', color='blue',
            #                 #          linestyle='--',
            #                 #          marker='o', alpha=0.3)
            #                 # plt.xlabel('行号')
            #                 # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            #                 # plt.ylabel(inputFields[o][0])
            #                 # plt.figtext(0.5, -0.01,
            #                 #             f'图{st.session_state.IMAGECOUNT} {inputFields[o][0]}字段部分数据插补前后对比图',
            #                 #             ha='center', fontsize=16)
            #                 # plt.legend()
            #                 # st.pyplot(fig)
            #                 # st.session_state.IMAGECOUNT += 1
            #
            # else:
            #     st.info('跳过预处理', icon="ℹ️️")

            # want_to_contribute = interval_col34.button("跳转至可视化界面")
            # if want_to_contribute:
            #     switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\Visualization.py")
            btn3 = st.columns([5, 1])[1].button('下一步')
            if btn3:
                switch_page(os.path.join(PAGES_PATH, 'FeatureCalculation.py'))
