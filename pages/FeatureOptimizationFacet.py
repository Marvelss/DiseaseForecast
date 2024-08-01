import datetime

import streamlit as st
import numpy as np
import pandas as pd
from st_pages import hide_pages

import pages_utils
import seaborn as sns
import matplotlib.pyplot as plt

from modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod

st.set_page_config(
    layout="wide"
)
if 'page14' not in st.session_state:
    st.session_state.page14 = 0
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")

# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据",
        "数据预处理",
        "特征计算",
        "特征优选",
        "模型构建",
    ]
)
checkBoxNum = 3
if "OptimizationMethodName" not in st.session_state:
    st.session_state["OptimizationMethodName"] = {
        'checkBox': None
    }
# 获取当前选中的方法名称
if "nowMethodName" not in st.session_state:
    st.session_state.nowMethodName = ''


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return 'Pearson相关性分析'
    elif checkbox == 'checkbox1':
        return 't检验'
    elif checkbox == 'checkbox2':
        return 'Relief-F互相关分析'


def mergeArray4(list1, list2, list3, list4):
    return list(set().union(*[list1, list2, list3, list4]))


def mergeArray(list1, list2, list3):
    return list(set().union(*[list1, list2, list3]))


# 取消所有选项按钮
def clear_all():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["OptimizationMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
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


plt.rc("font", family='Microsoft YaHei')


@st.experimental_dialog("预览", width='large')
# 预览运行结果
def onPreviewResults():
    afterHandleData, tempResultP, optimalFeatureList = None, None, None
    tempMethod = getCheckboxName(st.session_state.nowMethodName)
    methodParam = [value for key, value in st.session_state["OptimizationMethodName"].items() if
                   key != 'checkBox']

    # 第一次使用特征计算数据集,而后基于特征优选数据集多次处理
    if pages_utils.TempDataSetFacet[3].shape[0] == 0:
        dataFrameTemp = pages_utils.TempDataSetFacet[2]
    else:
        dataFrameTemp = pages_utils.TempDataSetFacet[3]
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
        st.multiselect('预期保留特征:',
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
        plt.title('Pearson互相关性分析矩阵')
        st.pyplot(plt)
        st.multiselect('预期保留特征:',
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
        st.multiselect('预期保留特征:',
                       options=optimalFeatureListR,
                       default=optimalFeatureListR)
    # 选择后变化
    if st.button("添加处理", on_click=clear_all):
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": '气象数据',
            "输入特征": mergeArray(result1, result2, result3),
            "特征优选方法": getCheckboxName(st.session_state["OptimizationMethodName"]['checkBox']),
            "方法参数":
                [value for key, value in st.session_state["OptimizationMethodName"].items() if
                 key != 'checkBox'],
            "时间": datetime.datetime.now().time(),
            "处理状态": False}
        print('======================特征优选-添加任务清单记录======================')
        print(new_data)
        pages_utils.TempDataSetFieldFacet[3].loc[len(pages_utils.TempDataSetFieldFacet[3])] = new_data
        st.rerun()


def onRun():
    if '优选特征' not in st.session_state["leftTabsFacet"]:
        st.session_state["leftTabsFacet"].append('优选特征')
    st.session_state.page14 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetFieldFacet[3]["编号"].tolist()
    fields = pages_utils.TempDataSetFieldFacet[3]["输入特征"].tolist()
    methodParam = pages_utils.TempDataSetFieldFacet[3]["方法参数"].tolist()
    methodList = pages_utils.TempDataSetFieldFacet[3]["特征优选方法"].tolist()
    isHandledFlags = pages_utils.TempDataSetFieldFacet[3]["处理状态"].tolist()

    # 若为空则跳过该步骤
    if not idNumber:
        pages_utils.TempDataSetFacet[3] = pages_utils.TempDataSetFacet[2]

    newColumns = '错误'
    # ===============根据名称匹配调用并执行各个处理方法===============
    # 初始化特征优选方法
    for indexT, (tempMethod, isHandled) in enumerate(zip(methodList, isHandledFlags)):
        # 检查方法是否已执行
        if isHandled:
            continue
        # 第一次使用特征计算数据集,而后基于特征优选数据集多次处理
        if pages_utils.TempDataSetFacet[3].shape[0] == 0:
            dataFrameTemp = pages_utils.TempDataSetFacet[2]
        else:
            dataFrameTemp = pages_utils.TempDataSetFacet[3]
        reservedField = pages_utils.TempDataSetFacet[2].columns.tolist()
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
            pages_utils.TempDataSetFacet[3], afterHandleData
        )
        pages_utils.TempDataSetFacet[3] = pd.merge(
            afterHandleData, pages_utils.TempDataSetFacet[3],
            on=intersection_cols, how="left")

        # ===============更新左侧显示内容===============
        update_values = {
            # "数据类型": "气象数据", "输入特征": fields[0],
            "优选特征": ','.join(newColumns),
            "大小": '1*' + str(row_size),
            # "特征计算方法": st.session_state["OptimizationMethodName"]['checkBox'],
            "时间": datetime.datetime.now().time(),
            "处理状态": True}
        print(update_values)
        print(type(newColumns))
        print(len(idNumber))
        print(len(pages_utils.TempDataSetFieldFacet[3]))
        # 查找要更新的数据记录
        for index, row in pages_utils.TempDataSetFieldFacet[3].iterrows():
            if row["编号"] == idNumber[indexT]:
                for key, value in update_values.items():
                    pages_utils.TempDataSetFieldFacet[3].loc[index, key] = value

    print('======================优选特征集======================')
    print(pages_utils.TempDataSetFacet[3])


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
            # tempLeftTabs = pages_utils.TempDataSetFacet[2]
            print(f'f=========测试面状特征{st.session_state["leftTabsFacet"]}================')
            print(pages_utils.TempDataSetFacet[2])

            # 展示备选特征数据
            temp_df = pages_utils.TempDataSetFacet[2]
            # 排除指定列，获取其他列的名称
            exclude_columns = ['上级单位', '测报站点', '经度', '纬度', '年', 'DayOfYear']
            remaining_columns = [col for col in temp_df.columns if col not in exclude_columns]

            # 创建空的 DataFrame
            tempDataSetFacetReveal = pd.DataFrame(columns=["数据类型", "备选特征", "大小"])

            # 计算每个剩余列的数据量大小并填充到新的 DataFrame 中
            tempDataSetFacetReveal_list = []
            for col in remaining_columns:
                data_size = temp_df[col].memory_usage(index=False)
                tempDataSetFacetReveal_list.append({
                    "数据类型": "气象数据",
                    "备选特征": col,
                    "大小": data_size
                })

            # 使用 pd.concat 方法创建 DataFrame
            tempDataSetFacetReveal = pd.concat([tempDataSetFacetReveal, pd.DataFrame(tempDataSetFacetReveal_list)],
                                               ignore_index=True)
            print(f'{tempDataSetFacetReveal}-----tempDataSetFacetReveal')
            tt1 = st.tabs(st.session_state["leftTabsFacet"])
            for i in range(len(st.session_state["leftTabsFacet"])):
                with tt1[i]:
                    if st.session_state["leftTabsFacet"][i] == '备选特征':
                        st.data_editor(
                            tempDataSetFacetReveal,
                            height=220, width=800)
                    elif st.session_state["leftTabsFacet"][i] == '优选特征':
                        # column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                        st.data_editor(
                            pages_utils.TempDataSetFieldFacet[3],
                            height=220, width=800)

    if st.session_state.page12 == 1:
        with placeholder1.container():
            tempLeftTabs = st.session_state["leftTabsFacet"]
            # print(f'f=========测试{tempLeftTabs}================')
            tt = st.tabs(tempLeftTabs)
            for i in range(len(tempLeftTabs)):
                with tt[i]:
                    if st.session_state["leftTabsFacet"][i] == '备选特征':
                        st.data_editor(
                            tempDataSetFacetReveal,
                            height=220, width=800)
                    elif tempLeftTabs[i] == '优选特征':
                        # column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                        st.data_editor(
                            pages_utils.TempDataSetFieldFacet[3],
                            height=220, width=800)
    # ===============显示左下字段或特征及获取===============
    # a = st.selectbox(
    #     '选择数据集',
    #     ('原始数据集', '预处理后数据集', '备选特征', '优选特征'))
    # 预处理后数据集表信息
    # weatherNameT, plantNameT, agricultureNameT = pages_utils.getDataFiled()
    # weatherNameT, plantNameT, agricultureNameT = pages_utils.TempDataSet[2].columns.tolist(), ['无1'], ['无2']
    # 数组元素去重
    # weatherName, plantName, agricultureName = list(set(weatherNameT)), list(set(plantNameT)), list(
    #     set(agricultureNameT))
    result1 = pages_utils.multiselect_all(
        st, '全选-特征', pages_utils.TempDataSetFacet[2].columns.tolist(),
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
            mergeArray(result1, result2, result3))
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
            mergeArray(result1, result2, result3))
        option1122 = st.multiselect(
            '被比较变量',
            mergeArray(result1, result2, result3))
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
            mergeArray(result1, result2, result3))
        option11122 = st.multiselect(
            '被比较变量',
            mergeArray(result1, result2, result3))
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
            onPreviewResults()
    st.markdown('---')

    # =======================显示右下内容=======================
    placeholder = st.empty()
    if st.session_state.page14 == 0:
        # =======================显示右下任务清单表格=======================
        with placeholder.container():
            st.markdown('##### 任务清单')
            pages_utils.TempDataSetFieldFacet[3] = st.data_editor(
                pages_utils.TempDataSetFieldFacet[3], height=190, width=800,
                column_order=["编号", "数据类型", "输入特征", "优选特征", "特征优选方法", '时间', '处理状态'],
                disabled=["数据类型", "时间", '处理状态'], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])
            with interval_col33:
                #     with st.popover("准备运行"):
                #         st.markdown('保留字段选择')
                #         residualField = [arr for arr in pages_utils.TempDataSet[2].columns if
                #                          arr not in mergeArray4(
                #                              ['上级单位', '测报站点',
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
