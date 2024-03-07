import datetime
import streamlit as st
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pages_utils
from modelandmethod.Model import Model

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
# 初始化模型参数
model_params = [
    {"模型名称": "SVM", 'C': '1.0', 'kernel': 'rbf', 'gamma': 'scale'},
    {"模型名称": "KNN", "n_neighbors": "5", "leaf_size": "30",
     "n_jobs": "1"},
    {"模型名称": "FLDA", "n_components": "sqrt", "solver": "eigen",
     "store_covariance": "True"},
    {"模型名称": "RF", "n_estimators": "100", "criterion": "gini",
     "min_samples_split": "3"},
]

checkBoxModelNum = 4
st.set_page_config(
    layout="wide"
)


def mergeArray(list1, list2, list3):
    return list(set().union(*[list1, list2, list3]))


def getCheckboxName():
    for h in range(checkBoxModelNum):
        if st.session_state[f'checkBoxModel{h}']:
            temp1 = f'checkBoxModel{h}'
            # print(f'--click{h}--')
            if temp1 == 'checkBoxModel0':
                return 'SVM'
            elif temp1 == 'checkBoxModel2':
                return 'KNN'
            elif temp1 == 'checkBoxModel1':
                return 'RF'
            elif temp1 == 'checkBoxModel3':
                return 'FLDA'


def getModelName(temp1):
    if temp1 == 'checkBoxModel0':
        return 'SVM'
    elif temp1 == 'checkBoxModel2':
        return 'KNN'
    elif temp1 == 'checkBoxModel1':
        return 'RF'
    elif temp1 == 'checkBoxModel3':
        return 'FLDA'


def clearOtherOption(key1):
    # st.markdown(key)
    for h in range(checkBoxModelNum):
        if h != key1:
            st.session_state[f'checkBoxModel{h}'] = False
    return


def onTrain():
    if '模型' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('模型')
    st.session_state.page = 0
    st.session_state.page15 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[4]["编号"].tolist()
    models = pages_utils.TempDataSetField[4]["模型"].tolist()
    modelParam = pages_utils.TempDataSetField[4]["模型参数"].tolist()
    evaluationIndicator = pages_utils.TempDataSetField[4]["评价指标"].tolist()
    dataPartitioning = pages_utils.TempDataSetField[4]["数据集划分"].tolist()
    features = pages_utils.TempDataSetField[4]["特征"].tolist()
    targets = pages_utils.TempDataSetField[4]["标签"].tolist()
    # ===============测试是否统一时间分辨率===============
    # 若数据集行数不一致则提示

    # ===============获取字段对应数据集===============
    selected_datasets = []
    inputDataSet = []
    combinedGroupArray = []
    # 合并特征和标签
    for group1, group2 in zip(features, targets):
        combinedArrayTemp = group1 + group2
        combinedGroupArray.append(combinedArrayTemp)
    # for n in range(3, -1, -1):
    #     print(pages_utils.TempDataSet[n].columns)
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
    # ===============调用模型完成训练===============
    # print(pages_utils.TempDataSetField[4])
    for tempIndex, tempModel in enumerate(models):
        if tempModel == 'SVM':
            evaluationResult = Model(
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
    # 更新时间记录
    update_values = {
        "时间": datetime.datetime.now().time()}
    # 查找要更新的数据记录
    for index1, row1 in pages_utils.TempDataSetField[4].iterrows():
        if row1["编号"] == idNumber[0]:
            for key, value in update_values.items():
                pages_utils.TempDataSetField[4].loc[index1, key] = value


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


def onPrecision(cbox1, cbox2, cbox3):
    if cbox1:
        st.session_state["modelPrecisionName"].append('OA')
    if cbox2:
        st.session_state["modelPrecisionName"].append('Kappa')
    if cbox3:
        st.session_state["modelPrecisionName"].append('MSE')
    # print(pages_utils.TempDataSetField[4]['评价指标'])
    pages_utils.TempDataSetField[4]['评价指标'] = ','.join(st.session_state["modelPrecisionName"])
    st.session_state.page += 1


def firstPage(): st.session_state.page = 0


modelACV, modelACM = st.columns([0.5, 0.7])
with modelACV:
    st.markdown("##### 特征与模型")
    # st.data_editor(pages_utils.TempDataSet[0])
    # st.markdown(pages_utils.TempDataSet[1])
    # st.markdown(pages_utils.TempDataSet[2])
    # st.markdown(pages_utils.TempDataSet[3])
    # =======================左侧特征与模型显示=======================
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        # st.markdown(st.session_state.page12)
        with placeholder1.container():
            tt1 = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt1[i]:
                    if st.session_state["leftTabs"][i] == '原始数据':
                        column = ['数据类型', '字段', '上传时间']
                    elif st.session_state["leftTabs"][i] == '预处理后数据集':
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
                    elif st.session_state["leftTabs"][i] == '被选特征':
                        column = ["数据类型", "被选特征", "大小", "特征计算方法", '时间']
                    elif st.session_state["leftTabs"][i] == '优选特征':
                        column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                    elif st.session_state["leftTabs"][i] == '模型':
                        column = ["编号", "模型", "评价指标", "数据集划分", "时间", "下载模型结构、结果和参数值"]
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
                    elif st.session_state["leftTabs"][i] == '被选特征':
                        column = ["数据类型", "被选特征", "大小", "特征计算方法", '时间']
                    elif st.session_state["leftTabs"][i] == '优选特征':
                        column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                    elif st.session_state["leftTabs"][i] == '模型':
                        column = ["编号", "模型", "评价指标", "数据集划分", "时间", "下载模型结构、结果和参数值"]
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)
    # =======================选择数据集=======================
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
with modelACM:
    ph = st.empty()
    # Page 0
    if st.session_state.page == 0:
        with ph.container():
            st.markdown("###### 建模方法")
            colOption1, colOption2, colOption3 = st.columns(3)
            with colOption1:
                agree = st.checkbox('SVM', key='checkBoxModel0', on_change=clearOtherOption, args=[0])
                agree1 = st.checkbox('RF', key='checkBoxModel1', on_change=clearOtherOption, args=[1], disabled=True)
            with colOption2:
                agree2 = st.checkbox('KNN', key='checkBoxModel2', on_change=clearOtherOption, args=[2], disabled=True)

            with colOption3:
                agree3 = st.checkbox('FLDA', key='checkBoxModel3', on_change=clearOtherOption, args=[3], disabled=True)
                # agree4 = st.checkbox('贝叶斯统计')
                # agree5 = st.checkbox('模糊综合评价')
            st.markdown('---')
            if agree or agree1 or agree2 or agree2 or agree3:
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
            interval_col1, interval_col2 = st.columns([5, 1])
            btn1 = interval_col2.button("下一步", on_click=onModel)
            btn = interval_col1.button("添加模型", on_click=onAddModel)
            if btn:
                new_data = {
                    "编号": pages_utils.generateID(),
                    "模型": getModelName(st.session_state["modelName"]['checkBoxModel']),
                    "模型参数": st.session_state["modelParamName"],
                    "特征": result1,
                    "标签": result2,
                    "时间": datetime.datetime.now().time(),
                    "下载模型结构、结果和参数值": False}
                print('======================模型构建-添加任务清单记录======================')
                print(new_data)
                pages_utils.TempDataSetField[4].loc[len(pages_utils.TempDataSetField[4])] = new_data
                st.rerun()
    # Page 1
    elif st.session_state.page == 1:
        with ph.container():
            st.markdown("###### 评价指标")
            agree6 = st.checkbox('OA', key='checkBoxPrecision0')
            agree7 = st.checkbox('Kappa', key='checkBoxPrecision1')
            agree8 = st.checkbox('MSE', key='checkBoxPrecision2')
            interval_col1, interval_col2 = st.columns([5, 1])
            btn21 = interval_col1.button(
                "下一步",
                on_click=onPrecision,
                args=[agree6, agree7, agree8])

    # Page 2
    elif st.session_state.page == 2:
        with ph.container():
            st.markdown("###### 验证与训练数据集划分")
            option = st.selectbox(
                label="划分比例",
                options=("8:2", "7:3", "6:4"), label_visibility='collapsed'
            )
            for index, row in pages_utils.TempDataSetField[4].iterrows():
                pages_utils.TempDataSetField[4].loc[index, '数据集划分'] = option
            interval_col1, interval_col2 = st.columns([5, 1])
            interval_col1.button("保存", on_click=firstPage)

            # btn11 = interval_col2.button("开始模型训练", on_click=onTrain)

    st.markdown('##### 任务清单')
    edited_df28 = st.data_editor(
        pages_utils.TempDataSetField[4], height=190, width=800,
        column_order=["编号", "模型", "时间"],
        disabled=["时间"], num_rows="dynamic", )
    interval_col34, interval_col33 = st.columns([4, 1])
    btn2 = interval_col33.button('开始模型训练', on_click=onTrain)

    placeholder1 = st.empty()
    # =======================结果可视化=======================
    if st.session_state.page15 == 1:
        with placeholder1.container():
            st.markdown('---')
            st.write('###### 精度评价')
            tab1, tab2 = st.tabs(["SVM", "FLDA"])
            with tab1:
                # 创建模拟的混淆矩阵
                data = {'y_Actual': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                        'y_Predicted': [1, 1, 1, 1, 0, 0, 0, 0, 1, 1]}
                df = pd.DataFrame(data, columns=['y_Actual', 'y_Predicted'])

                conf_matrix = confusion_matrix(df['y_Actual'], df['y_Predicted'])

                # 使用 seaborn 绘制混淆矩阵图
                fig, ax = plt.subplots()
                sns.heatmap(conf_matrix, annot=True, cmap='Blues', fmt='g', ax=ax)
                ax.set_xlabel('Predicted Label')
                ax.set_ylabel('True Label')
                st.pyplot(fig)

                col2, col3 = st.columns(2)
                oa = col2.metric("OA", "0.36")
                pa = col3.metric("Kappa", "0.5")
            with tab2:
                # 创建模拟的混淆矩阵
                data = {'y_Actual': [1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
                        'y_Predicted': [1, 1, 1, 1, 0, 0, 0, 0, 1, 1]}
                df = pd.DataFrame(data, columns=['y_Actual', 'y_Predicted'])

                conf_matrix = confusion_matrix(df['y_Actual'], df['y_Predicted'])

                # 使用 seaborn 绘制混淆矩阵图
                fig, ax = plt.subplots()
                sns.heatmap(conf_matrix, annot=True, cmap='Blues', fmt='g', ax=ax)
                ax.set_xlabel('Predicted Label')
                ax.set_ylabel('True Label')
                st.pyplot(fig)

                col2, col3 = st.columns(2)
                oa1 = col2.metric("OA", "0.37")
                pa1 = col3.metric("Kappa", "0.8")
