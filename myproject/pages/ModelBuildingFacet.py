import datetime
import os.path

import streamlit as st
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from st_pages import hide_pages

from lib.share import RESOURCE_MODELRESULT_PATH
from pages import pages_utils
from pages.modelandmethod.Model import Model

st.set_page_config(
    layout="wide"
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'page15' not in st.session_state:
    st.session_state.page15 = 0
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")

# 隐藏页面
if st.session_state.isPlanarInterface:
    hide_pages(
        [
            "测试界面",
            "原始数据",
            "数据预处理",
            "特征计算",
            "特征优选",
            "模型构建",
            "基于天气情景生成器的模型评价",
            "建模报告",
            "数据下载中心",
        ]
    )
else:
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
# 处理方法内容记录(任务清单各项值)
if "modelName" not in st.session_state:
    st.session_state["modelName"] = {
        'checkBoxModel': None
    }
if "modelParamName" not in st.session_state:
    st.session_state["modelParamName"] = {}
if "modelPrecisionName" not in st.session_state:
    st.session_state["modelPrecisionName"] = []
# 控制下一步按钮显隐
if "nextBtnShow" not in st.session_state:
    st.session_state.nextBtnShow = 0

checkBoxModelNum = 8
# 显示可视化中文图例
plt.rcParams['font.sans-serif'] = 'SimHei'
# 初始化模型参数
model_params = [
    {"模型名称": "SVM", 'C': '1.0', 'kernel': 'rbf', 'gamma': 'scale'},
    {"模型名称": "KNN", "n_neighbors": "5", "leaf_size": "30",
     "n_jobs": "1"},
    {"模型名称": "FLDA", "n_components": "sqrt", "solver": "eigen",
     "store_covariance": "True"},
    {"模型名称": "RF", "n_estimators": "100", "criterion": "gini",
     "min_samples_split": "3"},
    {"模型名称": "SEIR机理模型", "min_coefficient_ka": "1", "max_coefficient_ka": "4",
     "min_coefficient_kb": "0", "max_coefficient_kb": "0.3", "min_coefficient_kc": "30",
     "max_coefficient_kc": "60", "min_coefficient_OPT_PRI": "10", "max_coefficient_OPT_PRI": "30",
     "min_coefficient_r": "10", "max_coefficient_r": "20",
     "min_coefficient_q": "50", "max_coefficient_q": "90", "ω": "3",
     "β0": "0.46", "optimumTEM": "28", "temStep": "3", "preStep": "5", "slideStep": "暂定",
     "loopNumbers": "1", "popSize": "20", "chromLength": "10", "pc": "0.6", "pm": "0.001"},
    {"模型名称": "PLSR", "n_components": "2", "scale": "True", "max_iter": "500"},
    {"模型名称": "LR", "fit_intercept": "True", "normalize": "False", "alpha": "0.1"},
    {"模型名称": "SVR", "kernel": "linear", "C": "1.0", "epsilon": "0.1"}
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
            elif temp1 == 'checkBoxModel6':
                return 'LR'
            elif temp1 == 'checkBoxModel7':
                return 'SVR'


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
    elif temp1 == 'checkBoxModel6':
        return 'LR'
    elif temp1 == 'checkBoxModel7':
        return 'SVR'


# 取消其他选项按钮
def clearOtherOption(key1):
    # 显示添加模型按钮
    st.session_state.nextBtnShow = 0 if st.session_state.nextBtnShow == 1 else 1

    # st.markdown(key)
    for h in range(checkBoxModelNum):
        if h != key1:
            st.session_state[f'checkBoxModel{h}'] = False
    return


# 模型训练
def onTrain(temporaResolution):
    if '模型' not in st.session_state["leftTabsFacet"]:
        st.session_state["leftTabsFacet"].append('模型')
    st.session_state.page = 0
    st.session_state.page15 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetFieldFacet[4]["编号"].tolist()
    models = pages_utils.TempDataSetFieldFacet[4]["模型"].tolist()
    modelParam = pages_utils.TempDataSetFieldFacet[4]["模型参数"].tolist()
    evaluationIndicator = pages_utils.TempDataSetFieldFacet[4]["评价指标"].tolist()
    dataPartitioning = pages_utils.TempDataSetFieldFacet[4]["数据集划分比例"].tolist()
    features = pages_utils.TempDataSetFieldFacet[4]["特征"].tolist()
    targets = pages_utils.TempDataSetFieldFacet[4]["标签"].tolist()
    isHandledFlags = pages_utils.TempDataSetFieldFacet[4]["处理状态"]
    # print('============测试抽取数据集==============')
    inputDataSet = pages_utils.TempDataSetFacet[4]
    # print(inputDataSet)

    # ===============运行任务清单调用模型准备训练===============
    for tempIndex, (tempModel, isHandled) in enumerate(zip(models, isHandledFlags)):
        # 检查方法是否已执行
        if isHandled:
            continue
        evaluationResult = None
        modelStruct = None
        actualAndPredictResult = None
        if tempModel == 'SVM':
            evaluationResult, actualAndPredictResult, modelStruct = Model(
                inputDataSet,
                features[tempIndex], targets[tempIndex],
                dataPartitioning[tempIndex], eval(modelParam[tempIndex]),
                evaluationIndicator[tempIndex]).onSVM()
            # print('======测试返回模型评价结果======')
            # print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('SVM训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'KNN':
            evaluationResult, actualAndPredictResult, modelStruct = Model(
                inputDataSet,
                features[tempIndex], targets[tempIndex],
                dataPartitioning[tempIndex], eval(modelParam[tempIndex]),
                evaluationIndicator[tempIndex]).onKNN()

            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('KNN训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'FLDA':
            evaluationResult, actualAndPredictResult, modelStruct = Model(
                inputDataSet,
                features[tempIndex], targets[tempIndex],
                dataPartitioning[tempIndex], eval(modelParam[tempIndex]),
                evaluationIndicator[tempIndex]).onFLDA()

            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('FLDA训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'RF':
            evaluationResult, actualAndPredictResult, modelStruct = Model(
                inputDataSet,
                features[tempIndex], targets[tempIndex],
                dataPartitioning[tempIndex], eval(modelParam[tempIndex]),
                evaluationIndicator[tempIndex]).onRF()

            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('RF训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'PLSR':
            evaluationResult, actualAndPredictResult, modelStruct = Model(
                inputDataSet,
                features[tempIndex], targets[tempIndex],
                dataPartitioning[tempIndex], eval(modelParam[tempIndex]),
                evaluationIndicator[tempIndex]).onPLSR()
            print('======测试返回模型评价结果======')
            print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('PLSR训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'LR':
            # print('======测试输入参数======')
            # print(modelParam)
            evaluationResult, actualAndPredictResult, modelStruct = Model(
                inputDataSet,
                features[tempIndex], targets[tempIndex],
                dataPartitioning[tempIndex], eval(modelParam[tempIndex]),
                evaluationIndicator[tempIndex]).onLR()
            print('======测试返回模型评价结果======')
            print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('LR训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'SVR':
            # print('======测试输入参数======')
            # print(modelParam)
            evaluationResult, actualAndPredictResult, modelStruct = Model(
                inputDataSet,
                features[tempIndex], targets[tempIndex],
                dataPartitioning[tempIndex], eval(modelParam[tempIndex]),
                evaluationIndicator[tempIndex]).onSVR()
            print('======测试返回模型评价结果======')
            print(evaluationResult)
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('SVR训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        elif tempModel == 'SEIR机理模型':
            # print('======测试输入参数======')
            # print(modelParam)
            with st.status("正在运行SEIR机理模型"):
                evaluationResult, actualAndPredictResult, modelStruct = Model(
                    inputDataSet,
                    features[tempIndex], targets[tempIndex],
                    dataPartitioning[tempIndex], eval(modelParam[tempIndex]),
                    evaluationIndicator[tempIndex]).onSEIR()
            # print('======测试返回SEIR模型评价结果======')
            # print(f'精度:{evaluationResult}')
            # print(f'最优参数:{actualAndPredictResult}')
            # print(f'模型结构:{modelStruct}')
            # 显示模型训练结果信息
            info = ''
            for key, value in evaluationResult.items():
                info += f'{key}:{str(round(value, 3))}' + '       '
            # 显示精度结果
            st.toast('SEIR机理模型训练完成 \n' + '       ' + ' \n' + info,
                     icon='✅')
        # print('==============更新前================')
        # print(pages_utils.TempDataSetFieldFacet[4])
        # ===============更新左侧显示内容===============
        # print(actualAndPredictResult)
        update_values = {
            "时间": datetime.datetime.now().time(),
            "评价指标": evaluationResult,
            "处理状态": True,
            "模型训练结果": actualAndPredictResult,
            "模型结构": modelStruct}
        print('======更新指标======')
        print(update_values)
        # 查找要更新的数据记录
        for index1, row1 in pages_utils.TempDataSetFieldFacet[4].iterrows():
            if row1["编号"] == idNumber[tempIndex]:
                for key, value in update_values.items():
                    pages_utils.TempDataSetFieldFacet[4].at[index1, key] = value

    # print('==============更新后指标================')
    # print(pages_utils.TempDataSetFieldFacet[4])


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
    if cboxList[4]:
        st.session_state["modelPrecisionName"].append('RMSE')
    # print(st.session_state["modelPrecisionName"])
    pages_utils.TempDataSetFieldFacet[4]['评价指标'] = ','.join(st.session_state["modelPrecisionName"])
    st.session_state.page += 1


def firstPage(): st.session_state.page = 0


def backPage(): st.session_state.page15 = 0


# ==============================界面==============================
modelACV, modelACM = st.columns([0.5, 0.7])
with modelACV:
    st.markdown("##### 特征与模型")

    # =======================显示左侧特征与模型=======================
    tempLeftTabs = st.session_state["leftTabsFacet"][1:]
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        with placeholder1.container():
            tt1 = st.tabs(tempLeftTabs)
            for i in range(len(tempLeftTabs)):
                with tt1[i]:
                    if tempLeftTabs[i] == '优选特征':
                        # column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                        st.data_editor(
                            pages_utils.TempDataSetFieldFacet[3],
                            height=220, width=800)
                    elif tempLeftTabs[i] == '模型':
                        # column = ["编号", "模型", "评价指标", "数据集划分比例", "时间"]
                        st.data_editor(
                            pages_utils.TempDataSetFieldFacet[4],
                            height=220, width=800)

    if st.session_state.page12 == 1:
        with placeholder1.container():
            tt = st.tabs(tempLeftTabs)
            for i in range(len(tempLeftTabs)):
                with tt[i]:
                    if tempLeftTabs[i] == '优选特征':
                        # column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                        st.data_editor(
                            pages_utils.TempDataSetFieldFacet[3],
                            height=220, width=800)
                    elif tempLeftTabs[i] == '模型':
                        # column = ["编号", "模型", "评价指标", "数据集划分比例", "时间"]
                        st.data_editor(
                            pages_utils.TempDataSetFieldFacet[4],
                            height=220, width=800)
    # ===============显示左下字段或特征及获取===============
    # 获取所有column
    columnArrayT = pages_utils.TempDataSetFacet[3].columns

    # 去除元素不包含特定子字符串的元素，例如 "_优选"
    # columnArray = [col for col in columnArrayT if "_优选" in col]
    # 数组元素去重
    featureList = list(set(columnArrayT))  # 特征变量
    # 过滤特定元素
    filtered_columns = [col for col in featureList if col not in [
                                                                  "经度", "纬度",
                                                                  "年", "DayOfYear"]]

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
            # 按模型分类显示
            st.markdown("###### 分类模型")
            colOption1, colOption2, colOption3, colOption4 = st.columns(4)
            with colOption1:
                agree = st.checkbox('SVM', key='checkBoxModel0', on_change=clearOtherOption, args=[0])
                # agree6 = st.checkbox('LR', key='checkBoxModel6', on_change=clearOtherOption, args=[6])
            with colOption2:
                agree1 = st.checkbox('RF', key='checkBoxModel1', on_change=clearOtherOption, args=[1])

            with colOption3:
                agree3 = st.checkbox('FLDA', key='checkBoxModel3', on_change=clearOtherOption, args=[3])

            with colOption4:
                agree2 = st.checkbox('KNN', key='checkBoxModel2', on_change=clearOtherOption, args=[2])
                # agree4 = st.checkbox('贝叶斯统计')
                # agree5 = st.checkbox('模糊综合评价')
            st.markdown("###### 回归模型")
            colOption21, colOption22, colOption23, colOption24 = st.columns(4)
            with colOption21:
                agree6 = st.checkbox('LR', key='checkBoxModel6', on_change=clearOtherOption, args=[6])
            with colOption22:
                agree7 = st.checkbox('SVR', key='checkBoxModel7', on_change=clearOtherOption, args=[7])
            with colOption23:
                agree5 = st.checkbox('PLSR', key='checkBoxModel5', on_change=clearOtherOption, args=[5])
            with colOption4:
                pass
            st.markdown("###### 机理模型")
            colOption31, colOption32, = st.columns(2)
            with colOption31:
                agree4 = st.checkbox('SEIR机理模型', key='checkBoxModel4', on_change=clearOtherOption, args=[4])
            with colOption32:
                pass

            st.markdown('---')

            # ===============显示和处理右中各个模型参数(主要添加模型时加入checkbox名称)===============
            if agree or agree1 or agree2 or agree2 or agree3 or agree4 or agree5 or agree6 or agree7:
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
            if st.session_state.nextBtnShow == 0:
                interval_col1, interval_col2 = st.columns([5, 1])
                btn1 = interval_col2.button("下一步", on_click=onModel)
            else:
                interval_col1, interval_col2 = st.columns([5, 1])
                btn = interval_col2.button("添加模型", on_click=onAddModel)
                # =======================添加模型=======================
                if btn:
                    # 隐藏添加模型按钮
                    st.session_state.nextBtnShow = 0
                    new_data = {
                        "编号": pages_utils.generateID(),
                        "模型": getModelName(st.session_state["modelName"]['checkBoxModel']),
                        "模型参数": st.session_state["modelParamName"],
                        "特征": result1,
                        "标签": result2,
                        "时间": datetime.datetime.now().time(),
                        "处理状态": False}
                    print('======================模型构建-添加模型======================')
                    print(new_data)
                    pages_utils.TempDataSetFieldFacet[4].loc[len(pages_utils.TempDataSetFieldFacet[4])] = new_data
                    st.rerun()
    # Page 1
    elif st.session_state.page == 1:
        # =======================添加评价指标=======================
        with ph.container():
            st.markdown("##### 评价指标")

            st.markdown('###### 分类指标')
            tempCol21, tempCol22, tempCol23 = st.columns(3)
            with tempCol21:
                agree6 = st.checkbox('OA', key='checkBoxPrecision0')
            with tempCol22:
                agree7 = st.checkbox('Kappa', key='checkBoxPrecision1')
            with tempCol23:
                pass
            st.markdown('###### 回归指标')
            tempCol1, tempCol2, tempCol3 = st.columns(3)
            with tempCol1:
                agree10 = st.checkbox('RMSE', key='checkBoxPrecision4')
            with tempCol2:
                agree9 = st.checkbox('R方', key='checkBoxPrecision3')
            with tempCol3:
                agree8 = st.checkbox('MSE', key='checkBoxPrecision2')

            interval_col1, interval_col2 = st.columns([5, 1])
            # 传入指标
            # tempArgs =
            btn21 = interval_col2.button(
                "下一步",
                on_click=onPrecision,
                args=[agree6, agree7, agree8, agree9, agree10])

    # Page 2
    elif st.session_state.page == 2:
        # =======================添加验证与训练数据集划分=======================
        with ph.container():
            # 检查是否有缺失值
            for p in range(len(pages_utils.TempDataSetFacet))[::-1]:
                df11 = pages_utils.TempDataSetFacet[p]
                if not df11.empty:
                    break
            beforeDF = df11
            pages_utils.TempDataSetFacet[4] = beforeDF

            st.markdown("###### 训练与验证数据集划分")
            colOP1, colOP2 = st.columns(2)
            with colOP1:
                option1 = st.selectbox(
                    label="训练与验证数据集划分", label_visibility='collapsed',
                    options=("按比例划分", "按年份划分(未实现)")
                )
            with colOP2:
                if option1 == '按比例划分':
                    option = st.selectbox(
                        label="比例", label_visibility='collapsed',
                        options=("8:2", "7:3", "6:4")
                    )
                elif option1 == '按年份划分(未实现)':
                    option = st.selectbox(
                        label="年", label_visibility='collapsed',
                        options=('待实现', '')
                    )

            for index, row in pages_utils.TempDataSetFieldFacet[4].iterrows():
                pages_utils.TempDataSetFieldFacet[4].loc[index, '数据集划分比例'] = option
            interval_col1, interval_col2 = st.columns([5, 1])
            interval_col2.button("保存", on_click=firstPage)

    # =======================显示右下内容=======================
    placeholder = st.empty()
    if st.session_state.page15 == 0:
        # =======================显示右下任务清单表格=======================
        with placeholder.container():
            st.markdown('##### 任务清单')
            pages_utils.TempDataSetFieldFacet[4] = st.data_editor(
                pages_utils.TempDataSetFieldFacet[4], height=190, width=800,
                column_order=["编号", "模型", "时间", '处理状态'],
                disabled=["时间", '处理状态'], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([4, 1])
            with interval_col33:
                # st.info('当前时间分辨率为:1天')
                # temporaResolutionNum = st.text_input("统一时间分辨率(天)", value=1)
                btn = st.button('开始模型训练',
                                on_click=onTrain,
                                args=[1])
    # placeholder1 = st.empty()
    # =======================显示右下可视化图表=======================
    elif st.session_state.page15 == 1:
        with placeholder.container():
            st.markdown('---')
            st.write('###### 精度评价')
            models = pages_utils.TempDataSetFieldFacet[4]["模型"].tolist()
            evaluationIndex = pages_utils.TempDataSetFieldFacet[4]["评价指标"].tolist()
            targets = pages_utils.TempDataSetFieldFacet[4]["标签"].tolist()
            # actualAndPredictList = pages_utils.TempDataSetFieldFacet[4]["模型训练结果"].tolist()
            # print(print(actualAndPredictList))
            tt1 = st.tabs(models)
            for i in range(len(models)):
                with tt1[i]:
                    # print(actualAndPredictList)
                    # y_Actual = actualAndPredictList[i]['predictLabel']
                    # y_Predicted = actualAndPredictList[i]['actualLabel']
                    # print(f'=============可视化{y_Actual}{y_Predicted}=============')
                    # 创建模拟的混淆矩阵
                    rootPath = os.path.join(RESOURCE_MODELRESULT_PATH,
                                            'predict')
                    testLabelDF = pd.read_excel(
                        os.path.join(rootPath,
                                     models[i] + '_testLabel.xlsx'))
                    predictLabelDF = pd.read_excel(
                        os.path.join(rootPath,
                                     models[i] + '_predictLabel.xlsx'))
                    # 假设第一列包含要绘制的数据
                    actual_values = testLabelDF.iloc[:, 0]
                    predicted_values = predictLabelDF.iloc[:, 0]

                    # 回归模型
                    if models[i] == 'LR' or models[i] == 'SVR' or models[i] == 'PLSR' or models[i] == 'SEIR机理模型':
                        # 绘制散点图
                        fig, ax = plt.subplots()

                        sns.scatterplot(x=actual_values, y=predicted_values)
                        plt.plot([actual_values.min(), actual_values.max()], [actual_values.min(), actual_values.max()],
                                 'r--')
                        ax.set_xlabel('实际峰值(%)')
                        ax.set_ylabel('预测峰值(%)')
                        # plt.figure(figsize=(10, 6))
                        plt.title('回归模型精度评价-散点图')
                        st.pyplot(fig)

                    # 分类模型
                    elif models[i] == 'SVM' or models[i] == 'RF' or models[i] == 'FLDA' or models[i] == 'KNN':
                        # 绘制混淆矩阵图
                        fig, ax = plt.subplots()
                        conf_matrix = confusion_matrix(testLabelDF, predictLabelDF)
                        sns.heatmap(conf_matrix, annot=True, cmap='plasma', fmt='g', ax=ax)
                        ax.set_xlabel('实际病害发生程度')
                        ax.set_ylabel('预测病害发生程度')
                        plt.title('分类模型精度评价-混淆矩阵')
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
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('返回', on_click=backPage)
