import datetime

import streamlit as st
import numpy as np
import pandas as pd
from st_pages import hide_pages

from lib.utils import mergeExcludeArray, filterUnique
from pages import pages_utils
import seaborn as sns
import matplotlib.pyplot as plt

from pages.modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod

st.set_page_config(
    layout="wide"
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
if 'page14' not in st.session_state:
    st.session_state.page14 = 0
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")
# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据-面状",
        "数据预处理-面状",
        "特征计算-面状",
        "特征优选-面状",
        "模型构建-面状",
    ]
)
checkBoxNum = 3
# 预期保留特征
if "expectedRetentionFeature" not in st.session_state:
    st.session_state.expectedRetentionFeature = []
if "OptimizationMethodName" not in st.session_state:
    st.session_state["OptimizationMethodName"] = {
        'checkBox': None
    }
# 获取当前选中的方法名称
if "nowMethodName" not in st.session_state:
    st.session_state.nowMethodName = ''

emptyHeadFOP = st.empty()


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return 'Pearson相关性分析'
    elif checkbox == 'checkbox1':
        return 't检验'
    elif checkbox == 'checkbox2':
        return 'Relief-F互相关分析'


def simulate_temperature_data1():
    # 模拟生成数据
    np.random.seed(42)  # 设置随机种子以确保可重复性

    # 创建一个包含随机数据的数据框
    data = {
        'Feature1': np.random.normal(0, 1, 100),
        'Feature2': np.random.normal(0, 1, 100),
        'Feature3': np.random.normal(0, 1, 100),
        'Target': np.random.choice([0, 1], size=100)
    }
    dfT = pd.DataFrame(data)
    return dfT


def simulate_temperature_data():
    # 模拟生成温度数据
    np.random.seed(15)
    N = 15

    temperature1 = np.random.normal(loc=20, scale=2, size=(N,))
    temperature2 = np.random.normal(loc=25, scale=4, size=(N,))
    temperature3 = np.random.normal(loc=18, scale=1.5, size=(N,))
    temperature4 = np.random.normal(loc=22, scale=3, size=(N,))

    # 创建DataFrame
    dfT = pd.DataFrame({
        'Temperature1': temperature1,
        'Temperature2': temperature2,
        'Temperature3': temperature3,
        'Temperature4': temperature4,
        'Target': np.random.choice([0, 1], size=N)  # 二分类目标
    })
    return dfT


# 取消所有选项按钮
def clear_all():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["OptimizationMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    st.session_state.page14 = 0
    return


# 取消其他选项按钮
def clear_other(key):
    st.session_state.nowMethodName = f'checkbox{key}'
    for h in range(checkBoxNum):
        if h != key:
            st.session_state[f'checkbox{h}'] = False
    return


# 控制左侧表格不同数据集显示
def firstPage(): st.session_state.page14 = 0


@st.experimental_dialog("预览", width='large')
# 预览运行结果
def onPreviewResults():
    afterHandleData, tempResultP, optimalFeatureList = None, None, None
    tempMethod = getCheckboxName(st.session_state.nowMethodName)
    methodParam = [value for key, value in st.session_state["OptimizationMethodName"].items() if
                   key != 'checkBox']

    # 第一次使用特征计算数据集,而后基于特征优选数据集多次处理
    if pages_utils.TempDataSet[3].shape[0] == 0:
        dataFrameTemp = pages_utils.TempDataSet[2]
    else:
        dataFrameTemp = pages_utils.TempDataSet[3]
    if tempMethod == 't检验':
        afterHandleData, tempResult, optimalFeatureListT = FeatureOptimizationMethod(
            dataFrameTemp.copy(), None).tTest(
            methodParam)
        # 可视化
        keys = list(tempResult.keys())
        values = list(tempResult.values())
        # 创建柱状图
        plt.figure(figsize=(10, 6))
        plt.bar(keys, values, color='blue')
        # 添加标题和标签
        plt.title('敏感性结果可视化')
        plt.xlabel('特征')
        plt.ylabel('p-value')
        # 基准线
        plt.axhline(y=float(methodParam[2]), color='red', linestyle='--', linewidth=1, label='基准线 (p=0.01)')
        # 显示图表
        plt.xticks(rotation=45, ha='right')  # 旋转x轴标签
        plt.tight_layout()  # 调整布局以防止标签重叠
        st.pyplot(plt)
        st.session_state.expectedRetentionFeature = st.multiselect(
            '预期保留特征:',
            options=optimalFeatureListT,
            default=optimalFeatureListT)
    elif tempMethod == 'Pearson相关性分析':
        afterHandleData, tempResultP, optimalFeatureList = FeatureOptimizationMethod(
            dataFrameTemp.copy(), None).Pearson(
            methodParam)

        # 可视化
        # 使用Seaborn绘制热图
        plt.figure(figsize=(10, 8))
        sns.heatmap(tempResultP, annot=True, cmap='coolwarm', center=0)
        plt.title('互相关分析矩阵')
        st.pyplot(plt)
        st.session_state.expectedRetentionFeature = st.multiselect(
            '预期保留特征:',
            options=optimalFeatureList,
            default=optimalFeatureList)
    elif tempMethod == 'Relief-F互相关分析':
        afterHandleData, tempResultR, optimalFeatureListR = FeatureOptimizationMethod(
            dataFrameTemp.copy(), None).ReliefF(
            methodParam)
        # 可视化
        keys = list(tempResultR.keys())
        values = list(tempResultR.values())
        # 创建柱状图
        plt.figure(figsize=(10, 6))
        plt.bar(keys, values, color='blue')
        # 添加标题和标签
        plt.title('基于Relief-F特征因子权值排序图')
        plt.xlabel('特征')
        plt.ylabel('特征权值')

        standard = 0.5
        if methodParam[2] == '按百分比选取':
            # 计算TOP元素的数量,向上取整
            num_top_percent = int(np.ceil(len(values) * float(methodParam[3]) * 0.01))
            # 提取TOP的元素值
            top_percent_values = values[:num_top_percent + 1]
            # 获取前40%元素的最大值
            threshold_value = top_percent_values[-1]
            # print(num_top_percent)
            # print(threshold_value)
            standard = threshold_value
        if methodParam[2] == '按权重值选取':
            standard = float(methodParam[3])
        # 基准线
        plt.axhline(y=standard, color='red', linestyle='--', linewidth=1, label='基准线')
        # 显示图表
        plt.xticks(rotation=45, ha='right')  # 旋转x轴标签
        plt.tight_layout()  # 调整布局以防止标签重叠
        st.pyplot(plt)
        st.session_state.expectedRetentionFeature = st.multiselect(
            '预期保留特征:',
            options=optimalFeatureListR,
            default=optimalFeatureListR)
    # 选择后变化
    if st.button("添加处理", on_click=clear_all):
        print(st.session_state.expectedRetentionFeature)
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": pages_utils.getDataType(st.session_state.expectedRetentionFeature),
            "输入特征": mergeExcludeArray(result1, result2, result3, pages_utils.reservedField),
            "特征优选方法": getCheckboxName(st.session_state["OptimizationMethodName"]['checkBox']),
            "方法参数":
                [value for key, value in st.session_state["OptimizationMethodName"].items() if
                 key != 'checkBox'],
            "优选特征": ','.join(st.session_state.expectedRetentionFeature),
            "时间": datetime.datetime.now().time(),
            "处理状态": False}
        print('======================特征优选-添加任务清单记录======================')
        print(new_data)
        pages_utils.TempDataSetField[3].loc[len(pages_utils.TempDataSetField[3])] = new_data
        st.rerun()


def onRun():
    if '优选特征' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('优选特征')
    st.session_state.page14 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[3]["编号"].tolist()
    fields = pages_utils.TempDataSetField[3]["输入特征"].tolist()
    methodParam = pages_utils.TempDataSetField[3]["方法参数"].tolist()
    methodList = pages_utils.TempDataSetField[3]["特征优选方法"].tolist()
    isHandledFlags = pages_utils.TempDataSetField[3]["处理状态"].tolist()

    with emptyHeadFOP:
        with st.spinner('处理数据中...'):
            # 若为空则跳过该步骤
            if not idNumber:
                pages_utils.TempDataSet[3] = pages_utils.TempDataSet[2]

            newColumns = '错误'
            # ===============根据名称匹配调用并执行各个处理方法===============
            # 初始化特征优选方法
            for indexT, (tempMethod, isHandled) in enumerate(zip(methodList, isHandledFlags)):
                # 检查方法是否已执行
                if isHandled:
                    continue
                # 第一次使用特征计算数据集,而后基于特征优选数据集多次处理
                if pages_utils.TempDataSet[3].shape[0] == 0:
                    dataFrameTemp = pages_utils.TempDataSet[2]
                else:
                    dataFrameTemp = pages_utils.TempDataSet[3]
                reservedField = pages_utils.TempDataSet[2].columns.tolist()
                afterHandleData = None
                # print(tempMethod)
                if tempMethod == 't检验':
                    afterHandleData, _, newColumns = FeatureOptimizationMethod(
                        dataFrameTemp, reservedField).tTest(
                        methodParam[indexT])
                elif tempMethod == 'Pearson相关性分析':
                    # print('-------Pearson相关性分析-测试-------')
                    # print(methodParam[indexT])
                    afterHandleData, _, newColumns = FeatureOptimizationMethod(
                        dataFrameTemp, reservedField).Pearson(
                        methodParam[indexT])
                elif tempMethod == 'Relief-F互相关分析':
                    # print('-------Pearson相关性分析-测试-------')
                    # print(fields[0])
                    # print(methodParam[indexT])
                    afterHandleData, _, newColumns = FeatureOptimizationMethod(
                        dataFrameTemp, reservedField).ReliefF(methodParam[indexT])
                # print('=============返回数据=============')
                # print(afterHandleData)
                # ===============合并处理后数据集===============
                row_size = len(afterHandleData)
                # print('-------优选特征-------')
                intersection_cols = pages_utils.getIntersectionCols(
                    pages_utils.TempDataSet[3], afterHandleData
                )
                pages_utils.TempDataSet[3] = pd.merge(
                    afterHandleData, pages_utils.TempDataSet[3],
                    on=intersection_cols, how="left")

                # print(newColumns)
                # ===============更新左侧显示内容===============
                update_values = {
                    # "数据类型": "气象数据", "输入特征": fields[0],
                    "大小": '1*' + str(row_size),
                    # "特征计算方法": st.session_state["OptimizationMethodName"]['checkBox'],
                    "时间": datetime.datetime.now().time(),
                    "处理状态": True}
                # 查找要更新的数据记录
                for index, row in pages_utils.TempDataSetField[3].iterrows():
                    if row["编号"] == idNumber[indexT]:
                        for key, value in update_values.items():
                            pages_utils.TempDataSetField[3].loc[index, key] = value

            print('======================优选特征集======================')
            print(pages_utils.TempDataSet[3])


# ==============================界面==============================
# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    # ===============显示左侧数据与特征表格===============
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        with placeholder1.container():
            tempLeftTabs = st.session_state["leftTabs"][2:]
            if not tempLeftTabs:
                tempLeftTabs = ['待进行特征计算']
                column = ['空']
            # print(f'f=========测试{tempLeftTabs}================')
            tt1 = st.tabs(tempLeftTabs)
            for i in range(len(tempLeftTabs)):
                with tt1[i]:
                    if tempLeftTabs[i] == '备选特征':
                        column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
                    elif tempLeftTabs[i] == '优选特征':
                        column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                    st.data_editor(
                        pages_utils.TempDataSetField[i + 2],
                        height=220, width=800,
                        column_order=column)

    if st.session_state.page12 == 1:
        with placeholder1.container():
            tempLeftTabs = st.session_state["leftTabs"][2:]
            # print(f'f=========测试{tempLeftTabs}================')
            tt = st.tabs(tempLeftTabs)
            for i in range(len(tempLeftTabs)):
                with tt[i]:
                    if tempLeftTabs[i] == '备选特征':
                        column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
                    elif tempLeftTabs[i] == '优选特征':
                        column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                    st.data_editor(
                        pages_utils.TempDataSetField[i + 2],
                        height=220, width=800,
                        column_order=column)
    # ===============显示左下字段或特征及获取===============
    # weatherNameList, plantNameList, agricultureNameList = ['无1'], ['无2'], ['无3']
    # if not pages_utils.TempDataSetField[2].empty:
    weatherNameT0, plantNameT0, agricultureNameT0 = pages_utils.getDataFiled(0, pages_utils.TempDataSetField[0])
    weatherNameT1, plantNameT1, agricultureNameT1 = pages_utils.getDataFiled(1, pages_utils.TempDataSetField[1])
    weatherNameT2, plantNameT2, agricultureNameT2 = pages_utils.getDataFiled(2, pages_utils.TempDataSetField[2])
    # weatherNameList = weatherNameT1 + weatherNameT2 + weatherNameT0
    # plantNameList = plantNameT1 + plantNameT2 + plantNameT1 + plantNameT0
    # agricultureNameList = agricultureNameT1 + agricultureNameT0
    # if not pages_utils.TempDataSetField[3].empty:
    weatherNameT3, plantNameT3, agricultureNameT3 = pages_utils.getDataFiled(3, pages_utils.TempDataSetField[3])
    weatherNameList = weatherNameT1 + weatherNameT2 + weatherNameT0 + weatherNameT3
    plantNameList = plantNameT1 + plantNameT2 + plantNameT1 + plantNameT0 + plantNameT3
    agricultureNameList = agricultureNameT1 + agricultureNameT0 + agricultureNameT3
    print(weatherNameT1 + weatherNameT2 + weatherNameT0)
    print(weatherNameT3)
    if weatherNameT3:
        for a, b in zip(weatherNameT1 + weatherNameT2 + weatherNameT0, weatherNameT3):
            if '-'.join(b.split('-')[:-1]) in a:
                weatherNameList.append(b)
            else:
                weatherNameList.append(a)

    # 按照数据类型显示左侧字段或特征
    result1 = pages_utils.multiselect_all(
        st, '全选-气象特征', filterUnique(weatherNameList, pages_utils.reservedField),
        'tempTemperature', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-植保特征', filterUnique(plantNameList, pages_utils.reservedField),
        'tempPlant', 'collapsed')
    result3 = pages_utils.multiselect_all(
        st, '全选-农学特征', filterUnique(agricultureNameList, pages_utils.reservedField),
        'tempAgriculture', 'collapsed')
# ===============显示右上处理方法选项===============
with dataPCM:
    tab1, tab2 = st.tabs(["单因子敏感性分析", "多因子组合优化"])
    with tab1:
        genre = st.checkbox("Pearson相关性分析", key='checkbox0', on_change=clear_other, args=[0])
        genre1 = st.checkbox("t检验", key='checkbox1', on_change=clear_other, args=[1])

    with tab2:
        genre3 = st.checkbox("Relief-F互相关分析", key='checkbox2', on_change=clear_other, args=[2])
    st.markdown('---')

    # ===============显示和处理右中各个处理方法设置参数===============
    if genre:
        option1132 = st.multiselect(
            '变量',
            mergeExcludeArray(result1, result2, result3, pages_utils.reservedField))
        number33 = st.number_input("剔除相关系数阈值(R)",
                                   value=0.8,
                                   min_value=0.1,
                                   max_value=0.9,
                                   step=0.1)
        st.session_state["OptimizationMethodName"]['param1'] = ' '.join(option1132)
        st.session_state["OptimizationMethodName"]['param2'] = str(number33)

    if genre1:
        option112 = st.selectbox(
            '目标变量',
            mergeExcludeArray(result1, result2, result3, pages_utils.reservedField))
        option1122 = st.multiselect(
            '被比较变量',
            mergeExcludeArray(result1, result2, result3, pages_utils.reservedField))
        number112 = st.number_input("提取敏感性阈值(p-value)",
                                    value=0.01,
                                    min_value=0.01,
                                    max_value=0.05,
                                    step=0.01)
        st.session_state["OptimizationMethodName"]['param1'] = option112
        st.session_state["OptimizationMethodName"]['param2'] = ' '.join(option1122)
        st.session_state["OptimizationMethodName"]['param3'] = str(number112)
    # st.markdown('---')
    if genre3:
        # st.markdown('提取条件')
        option111 = st.selectbox(
            '目标变量',
            mergeExcludeArray(result1, result2, result3, pages_utils.reservedField))
        option11122 = st.multiselect(
            '被比较变量',
            mergeExcludeArray(result1, result2, result3, pages_utils.reservedField))
        st.session_state["OptimizationMethodName"]['param1'] = option111
        st.session_state["OptimizationMethodName"]['param2'] = ' '.join(option11122)
        option = st.selectbox(
            '提取条件',
            ('按百分比选取', '按权重值选取'))
        if option == '按百分比选取':
            st.session_state["OptimizationMethodName"]['param3'] = option
            number1 = st.number_input("TOP(%)", value=5, min_value=5, step=5)
            st.session_state["OptimizationMethodName"]['param4'] = str(number1)
        if option == '按权重值选取':
            st.session_state["OptimizationMethodName"]['param3'] = option
            number2 = st.number_input("权重阈值", value=10, min_value=10)
            st.session_state["OptimizationMethodName"]['param4'] = str(number2)

    # =======================添加处理至任务清单=======================
    interval_col1, interval_col2 = st.columns([4, 1])
    with interval_col2:
        if st.button("结果预览"):
            isContinueModel = False
            # 检测Relief-F不接受回归
            if pages_utils.TempDataSet[3].shape[0] == 0:
                dataFrameTemp = pages_utils.TempDataSet[2]
            else:
                dataFrameTemp = pages_utils.TempDataSet[3]
            if getCheckboxName(st.session_state["OptimizationMethodName"]['checkBox']) == 'Relief-F互相关分析':
                isContinueModel = FeatureOptimizationMethod.detectReliefFContinueColumn(
                    dataFrameTemp, option111)
            if isContinueModel:
                st.toast('Relief-F不支持回归模型,请重新选择', icon="⚠️")
            else:
                onPreviewResults()
    st.markdown('---')

    # =======================显示右下内容=======================
    placeholder = st.empty()
    if st.session_state.page14 == 0:
        # =======================显示右下任务清单表格=======================
        with placeholder.container():
            st.markdown('##### 任务清单')
            pages_utils.TempDataSetField[3] = st.data_editor(
                pages_utils.TempDataSetField[3], height=190, width=800,
                column_order=["编号", "数据类型", "输入特征", "优选特征", "特征优选方法", '时间', '处理状态'],
                disabled=["数据类型", "时间", '处理状态'], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])
            with interval_col33:
                #     with st.popover("准备运行"):
                #         st.markdown('保留字段选择')
                #         residualField = [arr for arr in pages_utils.TempDataSet[2].columns if
                #                          arr not in mergeArray4(
                #                              ['经度', '纬度',
                #                               "年", "DayOfYear"], result1, result2, result3)]
                #         # print(f'剩余字段{residualField}')
                #         reservedFiled = pages_utils.multiselect_all(
                #             st, '全选',
                #             residualField,
                #             'temp2', 'collapsed')
                #         btn = st.button('运行', on_click=onRun, args=[reservedFiled])
                btn = st.button('运行', on_click=onRun)
    elif st.session_state.page14 == 1:
        # =======================显示右下可视化图表=======================
        with placeholder.container():
            st.markdown('##### 可视化')
            st.markdown('待优化中')
            # plt.rc("font", family='Microsoft YaHei')
            # # idFMethods = pages_utils.TempDataSetField[2]["特征优选方法"].tolist()
            #
            # # 若无方法处理,则直接跳过该环节
            # if len(idFMethods):
            #     # 创建新的从 1 开始的编号列表
            #     new_ids = list(range(0, len(idFMethods)))
            #     # 创建标签页并重新命名记录
            #     new_ids = [f'记录编号_{h}' for h in new_ids]
            #
            #     tt1 = st.tabs(new_ids)
            #     for o in range(len(idFMethods)):
            #         with tt1[o]:
            #             # 创建DataFrame
            #             data_after = st.session_state["FCVisualInformation"][o]['after']
            #             # 特征名称
            #             dataColumn = st.session_state["FCVisualInformation"][o]['column']
            #             if idFMethods[o] == 't检验':
            #                 # 选择最多8个测报站点
            #                 top_stations = data_after['测报站点'].value_counts().nlargest(8).index
            #                 df_filtered_stations = data_after[data_after['测报站点'].isin(top_stations)]
            #
            #                 # 选择最多3个年份
            #                 top_years = data_after['年'].value_counts().nlargest(3).index
            #                 df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
            #
            #                 # 绘制折线图
            #                 plt.figure(figsize=(10, 6))
            #                 sns.lineplot(
            #                     data=df_filtered,
            #                     x="测报站点",
            #                     y=dataColumn,
            #                     hue="年",
            #                     marker="o"
            #                 )
            #                 # 设置标签和标题
            #                 plt.xlabel("测报站点")
            #                 plt.ylabel(dataColumn)
            #                 plt.title(f"部分县市与各年份{dataColumn}", fontsize=16)
            #                 st.pyplot(plt)
            #             elif idFMethods[o] == 'Pearson相关性分析':
            #                 pass
            #             elif idFMethods[o] == 'Relief-F互相关分析':
            #                 pass
            interval_col34, interval_col33 = st.columns([5, 1])
            # want_to_contribute = interval_col34.button("跳转至可视化界面")
            # if want_to_contribute:
            #     switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\Visualization.py")
            btn3 = interval_col33.button('返回', on_click=firstPage)
