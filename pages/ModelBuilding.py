import datetime
import streamlit as st
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pages_utils
from modelandmethod.Model import Model

st.set_page_config(
    layout="wide"
)
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'page15' not in st.session_state:
    st.session_state.page15 = 0
# 处理方法内容记录(任务清单各项值)
if "modelName" not in st.session_state:
    st.session_state["modelName"] = {
        'checkBoxModel': None
    }
if "modelParamName" not in st.session_state:
    st.session_state["modelParamName"] = {}
if "modelPrecisionName" not in st.session_state:
    st.session_state["modelPrecisionName"] = []
checkBoxModelNum = 6

# 初始化模型参数
model_params = [
    {"模型名称": "SVM", 'C': '1.0', 'kernel': 'rbf', 'gamma': 'scale'},
    {"模型名称": "KNN", "n_neighbors": "5", "leaf_size": "30",
     "n_jobs": "1"},
    {"模型名称": "FLDA", "n_components": "sqrt", "solver": "eigen",
     "store_covariance": "True"},
    {"模型名称": "RF", "n_estimators": "100", "criterion": "gini",
     "min_samples_split": "3"},
    {"模型名称": "SEIR机理模型"},
    {"模型名称": "PLSR", "n_components": "2", "scale": "True", "max_iter": "500"}
]


def mergeArray(list1, list2, list3):
    return list(set().union(*[list1, list2, list3]))


# 获取模型选项值对应名称
def getCheckboxName():
    for h in range(checkBoxModelNum):
        if st.session_state[f'checkBoxModel{h}']:
            temp1 = f'checkBoxModel{h}'
            if temp1 == 'checkBoxModel0':
                return 'SVM'
            elif temp1 == 'checkBoxModel2':
                return 'KNN'
            elif temp1 == 'checkBoxModel1':
                return 'RF'
            elif temp1 == 'checkBoxModel3':
                return 'FLDA'
            elif temp1 == 'checkBoxModel4':
                return 'SEIR机理模型'
            elif temp1 == 'checkBoxModel5':
                return 'PLSR'


def getModelName(temp1):
    if temp1 == 'checkBoxModel0':
        return 'SVM'
    elif temp1 == 'checkBoxModel1':
        return 'RF'
    elif temp1 == 'checkBoxModel2':
        return 'KNN'
    elif temp1 == 'checkBoxModel3':
        return 'FLDA'
    elif temp1 == 'checkBoxModel4':
        return 'SEIR机理模型'
    elif temp1 == 'checkBoxModel5':
        return 'PLSR'


# 取消其他选项按钮
def clearOtherOption(key1):
    # st.markdown(key)
    for h in range(checkBoxModelNum):
        if h != key1:
            st.session_state[f'checkBoxModel{h}'] = False
    return


# 模型训练
def onTrain(temporaResolution):
    if '模型' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('模型')
    st.session_state.page = 0
    st.session_state.page15 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[4]["编号"].tolist()
    models = pages_utils.TempDataSetField[4]["模型"].tolist()
    modelParam = pages_utils.TempDataSetField[4]["模型参数"].tolist()
    evaluationIndicator = pages_utils.TempDataSetField[4]["评价指标"].tolist()
    dataPartitioning = pages_utils.TempDataSetField[4]["数据集划分比例"].tolist()
    features = pages_utils.TempDataSetField[4]["特征"].tolist()
    targets = pages_utils.TempDataSetField[4]["标签"].tolist()
    # ===============测试是否统一时间分辨率===============
    # 若数据集行数不一致则提示
    # if temporaResolution != 1:
    #     st.toast('测试')
    # ===============获取字段对应数据集===============
    selected_datasets = []
    inputDataSet = []
    combinedGroupArray = []
    # 合并特征和标签
    for group1, group2 in zip(features, targets):
        combinedArrayTemp = group1 + group2
        combinedGroupArray.append(combinedArrayTemp)
    # print('==========合并特征==========')
    # print(combinedGroupArray)
    # 获取对应数据集
    for smallGroup in combinedGroupArray:
        temp_selected = []
        for field in smallGroup:
            found = False  # 设置一个标志位
            for n in range(3, -1, -1):
                if field in pages_utils.TempDataSet[n].columns:
                    # 判断数据集是否为空
                    if len(pages_utils.TempDataSet[n]):
                        print(f'添加了{field}')
                        temp_selected.append(n)
                        found = True  # 找到了feature，将标志位设置为True
                        break  # 找到feature后跳出内循环
            if not found:
                # 如果没有找到任何数据集包含feature，可以在这里进行处理
                pass
        selected_datasets.append(temp_selected)

    # ===============抽取数据集===============
    print('============测试特征对应数据集==============')
    print(selected_datasets)
    print(combinedGroupArray)
    for fieldList, dataIndexList in zip(combinedGroupArray, selected_datasets):
        merged_df = pd.DataFrame()
        for field, dataIndex in zip(fieldList, dataIndexList):
            # print(f'保留字段{field}')
            # print(dataIndex)
            tempData = pages_utils.TempDataSet[dataIndex][field]
            temp_df = pd.DataFrame(tempData, columns=[field])  # 创建临时的DataFrame
            merged_df = pd.concat([merged_df, temp_df], axis=1)  # 逐步合并数据
        inputDataSet.append(merged_df)
    print('============测试抽取数据集==============')
    print(inputDataSet)

    # ===============运行任务清单调用模型准备训练===============
    for tempIndex, tempModel in enumerate(models):
        evaluationResult = None
        actualAndPredictResult = None
        if tempModel == 'SVM':
            evaluationResult, actualAndPredictResult = Model(
                inputDataSet[tempIndex],
                features[tempIndex], targets[tempIndex],
                dataPartitioning, modelParam,
                evaluationIndicator).onSVM()
            print('======测试返回模型评价结果======')
            print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('SVM训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'KNN':
            evaluationResult, actualAndPredictResult = Model(
                inputDataSet[tempIndex],
                features[tempIndex], targets[tempIndex],
                dataPartitioning, modelParam,
                evaluationIndicator).onKNN()
            print('======测试返回模型评价结果======')
            print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('KNN训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'FLDA':
            evaluationResult, actualAndPredictResult = Model(
                inputDataSet[tempIndex],
                features[tempIndex], targets[tempIndex],
                dataPartitioning, modelParam,
                evaluationIndicator).onFLDA()
            print('======测试返回模型评价结果======')
            print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('FLDA训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'RF':
            evaluationResult, actualAndPredictResult = Model(
                inputDataSet[tempIndex],
                features[tempIndex], targets[tempIndex],
                dataPartitioning, modelParam,
                evaluationIndicator).onRF()
            print('======测试返回模型评价结果======')
            print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('RF训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'PLSR':
            print('======测试输入参数======')
            print(modelParam)
            evaluationResult, actualAndPredictResult = Model(
                inputDataSet[tempIndex],
                features[tempIndex], targets[tempIndex],
                dataPartitioning, modelParam,
                evaluationIndicator).onPLSR()
            print('======测试返回模型评价结果======')
            print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('PLSR训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        print('==============更新前================')
        print(pages_utils.TempDataSetField[4])
        # ===============更新左侧显示内容===============
        print(actualAndPredictResult)
        update_values = {
            "时间": datetime.datetime.now().time(),
            "评价指标": evaluationResult,
            "处理状态": True}
        # "实际和预测值": actualAndPredictResult}
        # 查找要更新的数据记录
        for index1, row1 in pages_utils.TempDataSetField[4].iterrows():
            if row1["编号"] == idNumber[tempIndex]:
                for key, value in update_values.items():
                    pages_utils.TempDataSetField[4].at[index1, key] = value

    print('==============更新后指标================')
    # print(pages_utils.TempDataSetField[4])


def onModel():
    st.session_state.page += 1
    return


def onAddModel():
    # print(st.session_state["modelParamName"])
    for h in range(checkBoxModelNum):
        if st.session_state[f'checkBoxModel{h}']:
            st.session_state["modelName"]['checkBoxModel'] = f'checkBoxModel{h}'
        st.session_state[f'checkBoxModel{h}'] = False
    return


# 获取评价指标
def onPrecision(*cboxList):
    # print('传入接收参数')
    if cboxList[0]:
        st.session_state["modelPrecisionName"].append('OA')
    if cboxList[1]:
        st.session_state["modelPrecisionName"].append('Kappa')
    if cboxList[2]:
        st.session_state["modelPrecisionName"].append('MSE')
    if cboxList[3]:
        st.session_state["modelPrecisionName"].append('R方')
    # print(st.session_state["modelPrecisionName"])
    pages_utils.TempDataSetField[4]['评价指标'] = ','.join(st.session_state["modelPrecisionName"])
    st.session_state.page += 1


def firstPage(): st.session_state.page = 0


# ==============================界面==============================
modelACV, modelACM = st.columns([0.5, 0.7])
with modelACV:
    st.markdown("##### 特征与模型")

    # =======================显示左侧特征与模型=======================
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        with placeholder1.container():
            tt1 = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt1[i]:
                    if st.session_state["leftTabs"][i] == '原始数据':
                        column = ['数据类型', '字段', '上传时间']
                    elif st.session_state["leftTabs"][i] == '预处理后数据集':
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
                    elif st.session_state["leftTabs"][i] == '备选特征':
                        column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
                    elif st.session_state["leftTabs"][i] == '优选特征':
                        column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                    elif st.session_state["leftTabs"][i] == '模型':
                        column = ["编号", "模型", "评价指标", "数据集划分比例", "时间", "下载模型结构、结果和参数值"]
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
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
                    elif st.session_state["leftTabs"][i] == '备选特征':
                        column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
                    elif st.session_state["leftTabs"][i] == '优选特征':
                        column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                    elif st.session_state["leftTabs"][i] == '模型':
                        column = ["编号", "模型", "评价指标", "数据集划分比例", "时间", "下载模型结构、结果和参数值"]
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)
    # ===============显示左下字段或特征及获取===============
    # 获取所有column
    columnArray = []
    for p in range(len(pages_utils.TempDataSet) - 1):
        columnArray.extend(pages_utils.TempDataSet[p].columns)
    # 数组元素去重
    featureList = list(set(columnArray))  # 特征变量
    # 过滤特定元素
    filtered_columns = [col for col in featureList if col not in ["上级单位", "测报站点", "年", "DayOfYear"]]
    # 将过滤后的元素放入集合中
    targetList = set(filtered_columns)  # 目标变量
    result1 = pages_utils.multiselect_all(
        st, '全选-特征变量',
        featureList,
        'temp', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-目标变量', targetList,
        'temp', 'collapsed')

# ===============显示右上模型选项===============
with modelACM:
    ph = st.empty()
    # Page 0
    if st.session_state.page == 0:
        with ph.container():
            st.markdown("##### 建模方法")
            colOption1, colOption2, colOption3 = st.columns(3)
            with colOption1:
                agree = st.checkbox('SVM', key='checkBoxModel0', on_change=clearOtherOption, args=[0])
                agree1 = st.checkbox('RF', key='checkBoxModel1', on_change=clearOtherOption, args=[1])
            with colOption2:
                agree2 = st.checkbox('KNN', key='checkBoxModel2', on_change=clearOtherOption, args=[2])
                agree4 = st.checkbox('SEIR机理模型', key='checkBoxModel4', on_change=clearOtherOption, args=[4],
                                     disabled=True)
            with colOption3:
                agree3 = st.checkbox('FLDA', key='checkBoxModel3', on_change=clearOtherOption, args=[3])
                agree5 = st.checkbox('PLSR', key='checkBoxModel5', on_change=clearOtherOption, args=[5])
                # agree4 = st.checkbox('贝叶斯统计')
                # agree5 = st.checkbox('模糊综合评价')

            st.markdown('---')

            # ===============显示和处理右中各个模型参数(主要添加模型时加入checkbox名称)===============
            if agree or agree1 or agree2 or agree2 or agree3 or agree5:
                model = getCheckboxName()
                # print(f'--{model}--')
                # 获取SVM模型的参数
                svm_params_dict = {}
                for entry in model_params:
                    if entry.get("模型名称") == model:
                        svm_params_dict = {key: value for key, value in entry.items() if key != "模型名称"}

                # 转换参数格式
                formatted_params = [{"参数名": key, "参数值": value} for key, value in svm_params_dict.items()]
                df = pd.DataFrame(formatted_params)
                edited_df = st.data_editor(df, height=190, width=800,
                                           disabled=["参数名"])
                st.session_state["modelParamName"] = edited_df.to_dict()

            # =======================准备任务清单内容=======================
            interval_col1, interval_col2 = st.columns([5, 1])
            btn1 = interval_col2.button("下一步", on_click=onModel)
            btn = interval_col1.button("添加模型", on_click=onAddModel)
            # =======================添加模型=======================
            if btn:
                new_data = {
                    "编号": pages_utils.generateID(),
                    "模型": getModelName(st.session_state["modelName"]['checkBoxModel']),
                    "模型参数": st.session_state["modelParamName"],
                    "特征": result1,
                    "标签": result2,
                    "时间": datetime.datetime.now().time(),
                    "下载模型结构、结果和参数值": False,
                    "处理状态": False}
                print('======================模型构建-添加模型======================')
                print(new_data)
                pages_utils.TempDataSetField[4].loc[len(pages_utils.TempDataSetField[4])] = new_data
                st.rerun()
    # Page 1
    elif st.session_state.page == 1:
        # =======================添加评价指标=======================
        with ph.container():
            st.markdown("###### 评价指标")
            tempCol1, tempCol2 = st.columns(2)
            with tempCol1:
                agree6 = st.checkbox('OA', key='checkBoxPrecision0')
                agree7 = st.checkbox('Kappa', key='checkBoxPrecision1')
            with tempCol2:
                agree8 = st.checkbox('MSE', key='checkBoxPrecision2')
                agree9 = st.checkbox('R方', key='checkBoxPrecision3')
            interval_col1, interval_col2 = st.columns([5, 1])
            # 传入指标
            # tempArgs =
            btn21 = interval_col1.button(
                "下一步",
                on_click=onPrecision,
                args=[agree6, agree7, agree8, agree9])

    # Page 2
    elif st.session_state.page == 2:
        # =======================添加验证与训练数据集划分=======================
        with ph.container():
            st.markdown("###### 验证与训练数据集划分")
            option = st.selectbox(
                label="划分比例",
                options=("8:2", "7:3", "6:4"), label_visibility='collapsed'
            )
            for index, row in pages_utils.TempDataSetField[4].iterrows():
                pages_utils.TempDataSetField[4].loc[index, '数据集划分比例'] = option
            interval_col1, interval_col2 = st.columns([5, 1])
            interval_col1.button("保存", on_click=firstPage)

    # =======================显示右下内容=======================
    st.markdown('##### 任务清单')
    edited_df28 = st.data_editor(
        pages_utils.TempDataSetField[4], height=190, width=800,
        column_order=["编号", "模型", "时间", '处理状态'],
        disabled=["时间", '处理状态'], num_rows="dynamic", )
    interval_col34, interval_col33 = st.columns([4, 1])
    with interval_col33:
        with st.popover("准备模型训练"):
            st.info('当前时间分辨率为:1天')
            temporaResolutionNum = st.text_input("统一时间分辨率(天)", value=1)
            btn = st.button('开始模型训练',
                            on_click=onTrain,
                            args=[temporaResolutionNum])
    placeholder1 = st.empty()
    # =======================显示右下可视化图表=======================
    if st.session_state.page15 == 1:
        with placeholder1.container():
            st.markdown('---')
            st.write('###### 精度评价')
            models = pages_utils.TempDataSetField[4]["模型"].tolist()
            evaluationIndex = pages_utils.TempDataSetField[4]["评价指标"].tolist()
            actualAndPredictList = pages_utils.TempDataSetField[4]["实际和预测值"].tolist()
            tt1 = st.tabs(models)
            for i in range(len(models)):
                with tt1[i]:
                    print(actualAndPredictList)
                    # y_Actual = actualAndPredictList[i]['predictLabel']
                    # y_Predicted = actualAndPredictList[i]['actualLabel']
                    # print(f'=============可视化{y_Actual}{y_Predicted}=============')
                    # 创建模拟的混淆矩阵
                    df1 = pd.read_excel(r'E:\a_python\program\diseaseForecastStreamlit\temp\actualLabel.xlsx')
                    df2 = pd.read_excel(r'E:\a_python\program\diseaseForecastStreamlit\temp\predictLabel.xlsx')
                    conf_matrix = confusion_matrix(df1['发生程度'], df2['predictLabel'])
                    # 使用 seaborn 绘制混淆矩阵图
                    fig, ax = plt.subplots()
                    sns.heatmap(conf_matrix, annot=True, cmap='Blues', fmt='g', ax=ax)
                    ax.set_xlabel('Predicted Label')
                    ax.set_ylabel('True Label')
                    st.pyplot(fig)
                    # Populate the array with key-value pairs
                    metrics = []
                    for key, value in evaluationIndex[i].items():
                        metrics.append((key, round(value, 3)))
                    # Display the metrics in two columns
                    half = len(metrics) // 2
                    col1, col2 = st.columns(2)
                    for h in range(half):
                        col2.metric(metrics[h][0], metrics[h][1])
                    for h in range(half, len(metrics)):
                        col1.metric(metrics[h][0], metrics[h][1])
