import datetime

import streamlit as st
import numpy as np
import pandas as pd
from st_pages import hide_pages
import streamlit_antd_components as sac

from lib.utils import mergeExcludeArray, filterUnique
from pages import pages_utils
import seaborn as sns
import matplotlib.pyplot as plt

from pages.modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod

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

st.markdown("""
    <style>
        div [data-baseweb=select]  {
            max-height: 150px;
            overflow: auto;
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)
if 'page14' not in st.session_state:
    st.session_state.page14 = 0
    st.toast('本环节已默认勾选上一环节计算的所有特征及相应的优选方法', icon="ℹ️")

    # 数据集统一分辨率
    if st.session_state.timeResolution == '':
        print(st.session_state.timeResolution)
    result = pages_utils.TempDataSet[2].groupby(['经度', '纬度', '年']).first().reset_index()
    # ******删除DayOfYear列******
    # df_cleaned = result.drop('DayOfYear', axis=1)
    pages_utils.TempDataSet[2] = result

if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")

checkBoxNum = 3
# 预期保留特征
if "expectedRetentionFeature" not in st.session_state:
    st.session_state.expectedRetentionFeature = []
if "OptimizationMethodName" not in st.session_state:
    st.session_state["OptimizationMethodName"] = {
        'checkBox': None
    }
# 优选特征集
if "preferenceFeature" not in st.session_state:
    st.session_state.preferenceFeature = []

if "inputFeatureList" not in st.session_state:
    st.session_state.inputFeatureList = []
# 获取当前选中的方法名称
if "nowMethodName" not in st.session_state:
    st.session_state.nowMethodName = ''
if 'FOVisualInformation' not in st.session_state:
    st.session_state["FOVisualInformation"] = []

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
sac.steps(
    items=[
        sac.StepsItem(title='数据集', disabled=True),
        sac.StepsItem(title='气象数据预处理', disabled=True),
        sac.StepsItem(title='特征计算', disabled=True),
        sac.StepsItem(title='特征优选', disabled=True),
        sac.StepsItem(title='模型构建', disabled=True),
        sac.StepsItem(title='模型应用', disabled=True),
    ], index=3
)

emptyHeadFOP = st.empty()


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return 'Pearson相关性分析'
    elif checkbox == 'checkbox1':
        return 't检验'
    elif checkbox == 'checkbox2':
        return 'Relief-F互相关分析'


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


@st.dialog("预览", width='large')
# 预览运行结果
def onPreviewResults():
    afterHandleData, tempResultP, optimalFeatureList = None, None, None
    tempMethod = getCheckboxName(st.session_state.nowMethodName)
    tempMethod = 'Pearson相关性分析'
    methodParam = [value for key, value in st.session_state["OptimizationMethodName"].items() if
                   key != 'checkBox']

    print('-------------优选特征(参数)-----------')
    # 默认先使用Pearson相关性分析剔除冗余特征
    print(methodParam)
    # 后用Relief-F筛选最优特征

    # 第一次使用特征计算数据集,而后基于特征优选数据集多次处理
    if pages_utils.TempDataSet[3].shape[0] == 0:
        dataFrameTempT = pages_utils.TempDataSet[2]
    else:
        dataFrameTempT = pages_utils.TempDataSet[3]
    if tempMethod == 't检验':
        tempResult, optimalFeatureListT = FeatureOptimizationMethod(
            dataFrameTempT.copy()).tTest(
            methodParam)

        # 可视化
        keys = list(tempResult.keys())
        values = [list(np.atleast_1d(v)) for v in tempResult.values()]  # 保证每个元素都是列表
        # 格式化 values
        formatted_values = []
        for row in values:
            formatted_row = []
            for value in row:
                if value < 0.001:
                    formatted_row.append("***")
                elif value < 0.01:
                    formatted_row.append("**")
                elif value < 0.05:
                    formatted_row.append("*")
                else:
                    formatted_row.append("")
            formatted_values.append(formatted_row)
        # print('-----测试t检验可视化-----')
        # print(keys)
        # print(values)
        # 将 keys 作为列名，values 转置为 DataFrame
        dfTT = pd.DataFrame(formatted_values, index=keys).T
        st.columns(3)[1].markdown('###### 各特征t检验敏感性分析结果')

        st.table(dfTT)
        st.caption('注：*表示p值<0.05，**表示p值<0.01，***表示p值<0.001')
        st.session_state.expectedRetentionFeature = st.multiselect(
            '预期保留特征:',
            options=optimalFeatureListT,
            default=optimalFeatureListT)
    elif tempMethod == 'Pearson相关性分析':
        tempResultP, optimalFeatureList = FeatureOptimizationMethod(
            dataFrameTempT.copy()).Pearson(
            methodParam)

        # 可视化
        # 使用Seaborn绘制热图
        plt.figure(figsize=(10, 8))
        sns.heatmap(tempResultP, annot=True, cmap='coolwarm', center=0)
        plt.figtext(0.5, -0.13,
                    f'图{st.session_state.IMAGECOUNT} Pearson互相关分析矩阵图',
                    ha='center', fontsize=16)
        # st.columns([0.3, 0.6, 0.4])[1].pyplot(plt)
        st.pyplot(plt)

        st.session_state.expectedRetentionFeature = st.multiselect(
            '预期保留特征:',
            options=optimalFeatureList,
            default=optimalFeatureList)

    elif tempMethod == 'Relief-F互相关分析':
        tempResultR, optimalFeatureListR = FeatureOptimizationMethod(
            dataFrameTempT.copy()).ReliefF(
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
        # st.columns([0.3, 0.6, 0.4])[1].pyplot(plt)
        st.pyplot(plt)

        st.session_state.expectedRetentionFeature = st.multiselect(
            '预期保留特征:',
            options=optimalFeatureListR,
            default=optimalFeatureListR)
    if tempMethod == 't检验':
        FOVisualInformationTemp = {
            'before': None,
            'after': tempResult,
            'name': tempMethod,
            'column': list(tempResult.keys()),
            'value': values,
            'standard': float(methodParam[2])}
    elif tempMethod == 'Pearson相关性分析':
        FOVisualInformationTemp = {
            'before': None,
            'name': tempMethod,
            'column': tempResultP,
            'after': tempResultP}
    elif tempMethod == 'Relief-F互相关分析':
        standard = 0.5
        valuesT = list(tempResultR.values())
        if methodParam[2] == '按百分比选取':
            # 计算TOP元素的数量,向上取整
            num_top_percent = int(np.ceil(len(valuesT) * float(methodParam[3]) * 0.01))
            # 提取TOP的元素值
            top_percent_values = valuesT[:num_top_percent + 1]
            # 获取前40%元素的最大值
            threshold_value = top_percent_values[-1]
            # print(num_top_percent)
            # print(threshold_value)
            standard = threshold_value
        if methodParam[2] == '按权重值选取':
            standard = float(methodParam[3])
        FOVisualInformationTemp = {
            'before': None,
            'after': tempResultR,
            'column': list(tempResultR.keys()),
            'value': list(tempResultR.values()),
            'standard': standard}
    # 可视化信息添加
    st.session_state["FOVisualInformation"].append(FOVisualInformationTemp)

    # 选择后变化
    if st.button("保留优选特征至下一环节", on_click=clear_all):
        st.session_state.preferenceFeature += st.session_state.expectedRetentionFeature

        # print(st.session_state.expectedRetentionFeature)
        new_data = {
            "编号": pages_utils.generateID(),
            # "数据类型": pages_utils.getDataType(st.session_state.expectedRetentionFeature),
            "输入特征": st.session_state.inputFeatureList,
            "特征优选方法": getCheckboxName(st.session_state["OptimizationMethodName"]['checkBox']),
            "方法参数":
                [value for key, value in st.session_state["OptimizationMethodName"].items() if
                 key != 'checkBox'],
            "优选特征": ','.join(st.session_state.expectedRetentionFeature),
            "时间": datetime.datetime.now().time(),
            "处理状态": True}
        print('======================特征优选-添加任务清单记录======================')
        print(new_data)
        pages_utils.TempDataSetField[3].loc[len(pages_utils.TempDataSetField[3])] = new_data
        st.rerun()


# 自动执行，先Pearson后Relief-F
def onRunAutomatic():
    # 使用特征计算数据集
    dataFrameTempT = pages_utils.TempDataSet[2]

    # print('-------------优选特征(参数)-----------')
    # 默认先使用Pearson相关性分析剔除冗余特征
    # 先Pearson相关性分析,后Relief-F
    if genre and genre3:
        methodParamP = [option1122, ' '.join(option1132), str(number33)]
        tempResultP, optimalFeatureList = FeatureOptimizationMethod(
            dataFrameTempT.copy()).Pearson(
            methodParamP)
        st.session_state.preferenceFeature = optimalFeatureList
        new_data = {
            "编号": pages_utils.generateID(),
            # "数据类型": pages_utils.getDataType(st.session_state.expectedRetentionFeature),
            "输入特征": option1132,
            "特征优选方法": 'Pearson相关性分析',
            "方法参数": methodParamP,
            "优选特征": ','.join(st.session_state.preferenceFeature),
            "时间": datetime.datetime.now().time(),
            "处理状态": True}
        pages_utils.TempDataSetField[3].loc[len(pages_utils.TempDataSetField[3])] = new_data
        print('======================特征优选-添加任务清单记录-P======================')
        print(new_data)
        print('==================优选特征=============')
        print(optimalFeatureList)
        # ==============Relief - F互相关分析===================
        methodParamR = [option111, ' '.join(st.session_state.preferenceFeature), option, str(number1)]
        tempResultR, optimalFeatureListR = FeatureOptimizationMethod(
            dataFrameTempT.copy()).ReliefF(
            methodParamR)
        st.session_state.preferenceFeature = optimalFeatureListR

        new_data = {
            "编号": pages_utils.generateID(),
            # "数据类型": pages_utils.getDataType(st.session_state.expectedRetentionFeature),
            "输入特征": optimalFeatureList,
            "特征优选方法": 'Relief-F互相关分析',
            "方法参数": methodParamP,
            "优选特征": ','.join(st.session_state.preferenceFeature),
            "时间": datetime.datetime.now().time(),
            "处理状态": True}
        pages_utils.TempDataSetField[3].loc[len(pages_utils.TempDataSetField[3])] = new_data
        # print('======================特征优选-添加任务清单记录-R======================')
        # print(new_data)
    else:
        methodParam = None
        if genre:
            methodParamP = [option1122, ' '.join(option1132), str(number33)]
            methodParam = methodParamP
            tempResultP, optimalFeatureList = FeatureOptimizationMethod(
                dataFrameTempT.copy()).Pearson(
                methodParam)
            st.session_state.preferenceFeature = optimalFeatureList
        elif genre3:
            methodParamR = [option111, ' '.join(option1132), option, str(number1)]
            methodParam = methodParamR
            tempResultR, optimalFeatureListR = FeatureOptimizationMethod(
                dataFrameTempT.copy()).ReliefF(
                methodParam)
            st.session_state.preferenceFeature = optimalFeatureListR

        # print(st.session_state.expectedRetentionFeature)
        new_data = {
            "编号": pages_utils.generateID(),
            # "数据类型": pages_utils.getDataType(st.session_state.expectedRetentionFeature),
            "输入特征": st.session_state.inputFeatureList,
            "特征优选方法": 'Pearson相关性分析' if genre else 'Relief-F互相关分析',
            "方法参数": methodParam,
            "优选特征": ','.join(st.session_state.preferenceFeature),
            "时间": datetime.datetime.now().time(),
            "处理状态": True}
        pages_utils.TempDataSetField[3].loc[len(pages_utils.TempDataSetField[3])] = new_data
    st.toast(f"优选特征已保留至下一环节", icon="ℹ️️")


def onRun():
    # if '优选特征' not in st.session_state["leftTabs"]:
    #     st.session_state["leftTabs"].append('优选特征')
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
                # st.session_state["leftTabs"].pop(0)

            newColumns = '错误'
            # ===============根据名称匹配调用并执行各个处理方法===============
            # 初始化特征优选方法
            for indexT, (tempMethod, isHandled) in enumerate(zip(methodList, isHandledFlags)):
                # 检查方法是否已执行
                if isHandled:
                    continue
                # 第一次使用特征计算数据集,而后基于特征优选数据集多次处理
                dataFrameTempT1 = pages_utils.TempDataSet[2]
                # print(tempMethod)
                if tempMethod == 't检验':
                    _, newColumns = FeatureOptimizationMethod(
                        dataFrameTempT1).tTest(
                        methodParam[indexT])
                elif tempMethod == 'Pearson相关性分析':
                    # print('-------Pearson相关性分析-测试-------')
                    # print(methodParam[indexT])
                    _, newColumns = FeatureOptimizationMethod(
                        dataFrameTempT1).Pearson(
                        methodParam[indexT])
                elif tempMethod == 'Relief-F互相关分析':
                    # print('-------Pearson相关性分析-测试-------')
                    # print(fields[0])
                    # print(methodParam[indexT])
                    _, newColumns = FeatureOptimizationMethod(
                        dataFrameTempT1).ReliefF(methodParam[indexT])
                # print('=============返回数据=============')
                # print(afterHandleData)
                # ===============合并处理后数据集===============
                # row_size = len(afterHandleData)
                # print('-------优选特征-------')
                # intersection_cols = pages_utils.getIntersectionCols(
                #     pages_utils.TempDataSet[3], afterHandleData
                # )
                # pages_utils.TempDataSet[3] = pd.merge(
                #     afterHandleData, pages_utils.TempDataSet[3],
                #     on=intersection_cols, how="left")

                # print(newColumns)
                # ===============更新左侧显示内容===============
                update_values = {
                    # "数据类型": "气象数据", "输入特征": fields[0],
                    # "大小": '1*' + str(row_size),
                    # "特征计算方法": st.session_state["OptimizationMethodName"]['checkBox'],
                    "时间": datetime.datetime.now().time(),
                    "处理状态": True}
                # 查找要更新的数据记录
                for index, row in pages_utils.TempDataSetField[3].iterrows():
                    if row["编号"] == idNumber[indexT]:
                        for key, value in update_values.items():
                            pages_utils.TempDataSetField[3].loc[index, key] = value

            # print('======================优选特征集======================')
            # print(pages_utils.TempDataSet[3])


# ==============================界面==============================
# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    # ===============显示左侧数据与特征表格===============
    placeholder1 = st.empty()
    # if st.session_state.page12 == 0:
    with placeholder1.container():
        # tempLeftTabs = st.session_state["leftTabs"]
        # if not tempLeftTabs:
        #     tempLeftTabs = ['待进行特征计算']
        #     column = ['空']
        # print(f'f=========测试{tempLeftTabs}================')
        tt1 = st.tabs(['备选特征'])
        # for i in range(len(tempLeftTabs)):
        with tt1[0]:
            # if tempLeftTabs[i] == '备选特征':
            #     column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
            # elif tempLeftTabs[i] == '优选特征':
            #     column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
            st.data_editor(
                pages_utils.TempDataSet[2],
                height=220, width=800, )
            # column_order=column)

    # if st.session_state.page12 == 1:
    #     with placeholder1.container():
    #         if pages_utils.TempDataSet[3].columns.tolist() == pages_utils.TempDataSet[2].columns.tolist():
    #             tt = st.tabs(['优选特征'])
    #             with tt[0]:
    #                 st.data_editor(
    #                     pages_utils.TempDataSet[2],
    #                     height=220, width=800, )
    #         else:
    #             tt = st.tabs(['备选特征', '优选特征'])
    #             with tt[0]:
    #                 st.data_editor(
    #                     pages_utils.TempDataSet[2],
    #                     height=220, width=800, )
    #             with tt[1]:
    #                 st.data_editor(
    #                     pages_utils.TempDataSet[3],
    #                     height=220, width=800, )
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
    # weatherNameT3, plantNameT3, agricultureNameT3 = pages_utils.getDataFiled(3, pages_utils.TempDataSetField[3])
    weatherNameT2Decade, weatherNameT2Month, weatherNameT2Other = [], [], []
    for weatherNameT22 in weatherNameT2:
        if '均值' in weatherNameT22:
            # 旬均值获取
            if '旬' in weatherNameT22:
                weatherNameT2Decade += weatherNameT22.split(',')
            # 月均值获取
            else:
                weatherNameT2Month += weatherNameT22.split(',')
        # 其他气象特征获取
        else:
            weatherNameT2Other += weatherNameT22.split(',')
    #     if isinstance(weatherNameT22, str):
    #         weatherNameT2H
    #
    #
    # weatherNameList = weatherNameT2H
    plantNameList = plantNameT2 + plantNameT0
    agricultureNameList = agricultureNameT2 + agricultureNameT1 + agricultureNameT0
    # print(weatherNameT1 + weatherNameT2 + weatherNameT0)
    # print('---测试优选特征--')
    # print(weatherNameT3)
    # print(agricultureNameT3)
    # if weatherNameT3:
    #     for a, b in zip(weatherNameT1 + weatherNameT2 + weatherNameT0, weatherNameT3):
    #         if '-'.join(b.split('-')[:-1]) in a:
    #             weatherNameList.append(b)
    #         else:
    #             weatherNameList.append(a)
    # 按照数据类型显示左侧字段或特征

    colSelect1, colSelect2 = st.columns(2)
    with colSelect1:
        result5 = pages_utils.multiselect_all_checked(
            st, '全选-旬均值特征', filterUnique(weatherNameT2Decade, pages_utils.reservedField),
            'dekad', 'collapsed')
    with colSelect2:
        result6 = pages_utils.multiselect_all_checked(
            st, '全选-月均值特征', filterUnique(weatherNameT2Month, pages_utils.reservedField),
            'month', 'collapsed')
    result1 = pages_utils.multiselect_all_checked(
        st, '全选-其他气象特征', filterUnique(weatherNameT2Other, pages_utils.reservedField),
        'tempTemperature', 'collapsed')

    # result2 = pages_utils.multiselect_all(
    #     st, '全选-植保特征', filterUnique(plantNameList, pages_utils.reservedField),
    #     'tempPlant', 'collapsed')
    result2 = filterUnique(plantNameList, pages_utils.reservedField)
    # result3 = pages_utils.multiselect_all(
    #     st, '全选-地理遥感特征', filterUnique(agricultureNameList, pages_utils.reservedField),
    #     'tempAgriculture', 'collapsed')
    result3 = filterUnique(agricultureNameList, pages_utils.reservedField)
    # result4 = pages_utils.multiselect_all(
    #     st, '全选-优选特征', set(st.session_state.preferenceFeature),
    #     'tempOptimal', 'collapsed')
# ===============显示右上处理方法选项===============
with dataPCM:
    tab1, tab2 = st.tabs(["单因子敏感性分析", "多因子组合优化"])

    # with tab1:
    #     genre = st.checkbox("Pearson相关性分析", key='checkbox0', on_change=clear_other, args=[0])
    #     genre1 = st.checkbox("t检验", key='checkbox1', on_change=clear_other, args=[1], disabled=True,
    #                          help='该功能开发中')
    # with tab2:
    #     genre3 = st.checkbox("Relief-F互相关分析", key='checkbox2', on_change=clear_other, args=[2])
    with tab1:
        genre = st.checkbox("Pearson相关性分析", key='checkbox0', args=[0], value=True)
        genre1 = st.checkbox("t检验", key='checkbox1', args=[1], disabled=True,
                             help='该功能开发中')
    with tab2:
        genre3 = st.checkbox("Relief-F互相关分析", key='checkbox2', args=[2], value=True)
    st.markdown('---')
    paramPlaceHolder = st.empty()

    # ===============显示和处理右中各个处理方法设置参数===============
    if genre:
        with paramPlaceHolder.container():
            with st.expander("高级设置"):
                option1122 = st.selectbox('目标变量-植保数据', result2)
                # option1132 = pages_utils.multiselect_all(
                #     st, '全选-被比较变量', mergeExcludeArray(
                #         result1, result2, result3, [option1122]),
                #     'tempFiled', 'collapsed')
                option1132 = result1 + result5 + result6
                # option1132 = mergeExcludeArray(result1, result2, result3, pages_utils.reservedField)
                number33 = st.number_input("优选相关系数阈值(R)",
                                           value=0.8,
                                           min_value=0.1,
                                           max_value=0.9,
                                           step=0.1)
                st.session_state["OptimizationMethodName"]['param1'] = option1122
                st.session_state["OptimizationMethodName"]['param2'] = ' '.join(option1132)
                st.session_state["OptimizationMethodName"]['param3'] = str(number33)
                st.session_state.inputFeatureList = option1132
    if genre1:
        option112 = st.selectbox(
            '目标变量',
            filterUnique(result2, pages_utils.reservedField))
        option1122 = pages_utils.multiselect_all(
            st, '全选-被比较变量', mergeExcludeArray(
                result1, result3, [], pages_utils.reservedField),
            'tempFiled', 'collapsed')
        number112 = st.number_input("提取敏感性阈值(p-value)",
                                    value=0.01,
                                    min_value=0.01,
                                    max_value=0.05,
                                    step=0.01)
        st.session_state["OptimizationMethodName"]['param1'] = option112
        st.session_state["OptimizationMethodName"]['param2'] = ' '.join(option1122)
        st.session_state["OptimizationMethodName"]['param3'] = str(number112)
        st.session_state.inputFeatureList = option1122

    # st.markdown('---')
    if genre3:
        with paramPlaceHolder.container():
            with st.expander("高级设置"):
                st.warning('注意：Relief - F算法只针对植保数据为离散变量(如病情等级)情形', icon="⚠️")
                option111 = st.selectbox('目标变量', result2)

                option11122 = result1 + result5 + result6
                st.session_state["OptimizationMethodName"]['param1'] = option111
                st.session_state["OptimizationMethodName"]['param2'] = ' '.join(option11122)
                st.session_state.inputFeatureList = option11122

                option = st.selectbox(
                    '优选条件',
                    '按百分比选取')  # , '按权重值选取'
                if option == '按百分比选取':
                    st.session_state["OptimizationMethodName"]['param3'] = option
                    number1 = st.number_input("TOP(%)", value=30, min_value=5, step=5)
                    st.session_state["OptimizationMethodName"]['param4'] = str(number1)
                if option == '按权重值选取':
                    st.session_state["OptimizationMethodName"]['param3'] = option
                    number2 = st.number_input("权重阈值", value=10, min_value=10)
                    st.session_state["OptimizationMethodName"]['param4'] = str(number2)

    # =======================添加处理至任务清单=======================
    interval_col34, interval_col33 = st.columns([5, 1])
    btn2 = interval_col33.button('运行', on_click=onRunAutomatic)

    # interval_col1, interval_col2 = st.columns([4, 1])
    # with interval_col2:
    #     if st.button("结果预览"):
    #         isContinueModel = False
    #         # 检测Relief-F不接受回归
    #         if pages_utils.TempDataSet[3].shape[0] == 0:
    #             dataFrameTempT2 = pages_utils.TempDataSet[2]
    #         else:
    #             dataFrameTempT2 = pages_utils.TempDataSet[3]
    #         if getCheckboxName(st.session_state["OptimizationMethodName"]['checkBox']) == 'Relief-F互相关分析':
    #             isContinueModel = FeatureOptimizationMethod.detectReliefFContinueColumn(
    #                 dataFrameTempT2, option111)
    #         if isContinueModel:
    #             st.toast('Relief-F不支持回归模型,请重新选择', icon="⚠️")
    #         else:
    #             onPreviewResults()

    st.markdown('---')

    # =======================显示右下内容=======================
    placeholder = st.empty()
    if st.session_state.page14 == 0:
        # =======================显示右下任务清单表格=======================
        with placeholder.container():
            st.markdown('##### 优选记录')
            pages_utils.TempDataSetField[3] = st.data_editor(
                pages_utils.TempDataSetField[3], height=190, width=1200,
                column_order=["编号", "输入特征", "优选特征", "特征优选方法", '时间', '处理状态'],
                disabled=["数据类型", "时间", '处理状态'], num_rows="dynamic", )
            # interval_col34, interval_col33 = st.columns([5, 1])
            # with interval_col33:
            #     btn = st.button('运行', on_click=onRun)
    elif st.session_state.page14 == 1:
        # =======================显示右下可视化图表=======================
        with placeholder.container():
            st.markdown('##### 可视化')
            # plt.rc("font", family='Microsoft YaHei')
            # idFMethods = pages_utils.TempDataSetField[3]["特征优选方法"].tolist()
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
            #             if len(st.session_state["FOVisualInformation"]):
            #                 print(st.session_state["FOVisualInformation"][o])
            #                 # 创建DataFrame
            #                 data_after = st.session_state["FOVisualInformation"][o]['after']
            #                 # 特征名称
            #                 dataColumn = st.session_state["FOVisualInformation"][o]['column']
            #                 if idFMethods[o] == 't检验':
            #                     # 选择最多8个测报站点
            #                     # top_stations = data_after['纬度'].value_counts().nlargest(8).index
            #                     # df_filtered_stations = data_after[data_after['纬度'].isin(top_stations)]
            #                     #
            #                     # # 选择最多3个年份
            #                     # top_years = data_after['年'].value_counts().nlargest(3).index
            #                     # df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
            #
            #                     tempResult = st.session_state["FOVisualInformation"][o]['after']
            #                     # 可视化
            #                     keysT1 = list(tempResult.keys())
            #                     valuesT = [list(np.atleast_1d(v)) for v in tempResult.values()]  # 保证每个元素都是列表
            #                     # 格式化 values
            #                     formatted_values = []
            #                     for row in valuesT:
            #                         formatted_row = []
            #                         for value in row:
            #                             if value < 0.001:
            #                                 formatted_row.append("***")
            #                             elif value < 0.01:
            #                                 formatted_row.append("**")
            #                             elif value < 0.05:
            #                                 formatted_row.append("*")
            #                             else:
            #                                 formatted_row.append("")
            #                         formatted_values.append(formatted_row)
            #                     # print('-----测试t检验可视化-----')
            #                     # 将 keys 作为列名，values 转置为 DataFrame
            #                     dfTTT = pd.DataFrame(formatted_values, index=keysT1).T
            #                     st.columns(3)[1].markdown('###### 各特征t检验敏感性分析结果')
            #                     st.table(dfTTT)
            #                     st.caption('注：*表示p值<0.05，**表示p值<0.01，***表示p值<0.001')
            #                 elif idFMethods[o] == 'Pearson相关性分析':
            #                     # 可视化
            #                     # 使用Seaborn绘制热图
            #                     plt.figure(figsize=(10, 8))
            #                     sns.heatmap(data_after, annot=True, cmap='coolwarm', center=0)
            #
            #                     plt.figtext(0.5, -0.13,
            #                                 f'图{st.session_state.IMAGECOUNT} Pearson互相关分析矩阵图',
            #                                 ha='center', fontsize=16)
            #                     st.session_state.IMAGECOUNT += 1
            #                     st.pyplot(plt)
            #
            #                 elif idFMethods[o] == 'Relief-F互相关分析':
            #                     # 可视化
            #                     # 创建柱状图
            #                     plt.figure(figsize=(10, 6))
            #                     plt.bar(st.session_state["FOVisualInformation"][o]['column'],
            #                             st.session_state["FOVisualInformation"][o]['value'], color='blue')
            #                     # 添加标题和标签
            #                     plt.title('基于Relief-F特征因子权值排序图')
            #                     plt.xlabel('特征')
            #                     plt.ylabel('特征权值')
            #
            #                     # 基准线
            #                     plt.axhline(y=st.session_state["FOVisualInformation"][o]['standard'], color='red',
            #                                 linestyle='--', linewidth=1, label='基准线')
            #                     # 显示图表
            #                     plt.xticks(rotation=45, ha='right')  # 旋转x轴标签
            #                     plt.tight_layout()  # 调整布局以防止标签重叠
            #                     st.pyplot(plt)
            # else:
            #     st.info('跳过特征优选', icon="ℹ️️")
            interval_col34, interval_col33 = st.columns([5, 1])
            # want_to_contribute = interval_col34.button("跳转至可视化界面")
            # if want_to_contribute:
            #     switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\Visualization.py")
            btn3 = interval_col33.button('返回', on_click=firstPage)
