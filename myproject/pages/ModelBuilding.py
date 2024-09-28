import datetime
import os.path
import time

import streamlit as st
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from st_pages import hide_pages

from lib.share import RESOURCE_MODELRESULT_PATH, IMAGECOUNT
from lib.utils import filterUnique
from pages import pages_utils
from pages.modelandmethod.Model import Model

st.set_page_config(
    layout="wide"
)

# 隐藏页面
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
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'page15' not in st.session_state:
    st.session_state.page15 = 0
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")

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

emptyHeadMBP = st.empty()

checkBoxModelNum = 8
# 显示可视化中文图例
plt.rcParams['font.sans-serif'] = 'SimHei'
# 初始化模型参数
model_params = [
    {"模型名称": "SVM",
     "模型参数": {
         'C': '1.0', 'kernel': 'rbf', 'gamma': 'scale'},
     "备注": ['惩罚系数', '核函数类型', '核系数']},
    {"模型名称": "KNN",
     "模型参数": {"n_neighbors": "5", "leaf_size": "30", "n_jobs": "1"},
     "备注": ['邻居数量', '叶子大小', '并行作业数']},
    {"模型名称": "FLDA",
     "模型参数": {"store_covariance": "True"},
     "备注": ['是否存储协方差矩阵']},
    {"模型名称": "RF",
     "模型参数": {"n_estimators": "100", "criterion": "gini", "min_samples_split": "3"},
     "备注": ['树的数量', '切分标准', '最小分割样本数']},
    {"模型名称": "SEIR机理模型",
     "模型参数": {
         "min_coefficient_ka": "1", "max_coefficient_ka": "4",
         "min_coefficient_kb": "0", "max_coefficient_kb": "0.3", "min_coefficient_kc": "30",
         "max_coefficient_kc": "60", "min_coefficient_OPT_PRI": "10", "max_coefficient_OPT_PRI": "30",
         "min_coefficient_r": "10", "max_coefficient_r": "20",
         "min_coefficient_q": "50", "max_coefficient_q": "90", "ω": "3",
         "β0": "0.46", "optimumTEM": "28", "temStep": "3", "preStep": "5", "slideStep": "暂定",
         "loopNumbers": "1", "popSize": "20", "chromLength": "10", "pc": "0.6", "pm": "0.001"
     },
     "备注": [
         '最小缓冲系数ka', '最大缓冲系数ka', '最小缓冲系数kb', '最大缓冲系数kb',
         '温度T:函数方差(下限)', '温度T:函数方差(上限)', '降水P:最适降水量(下限)',
         '降水P:最适降水量(上限)', '降水P:调节参数(下限)', '降水P:调节参数(上限)',
         '平均感染期(下限)', '平均感染期(上限)', '平均潜伏期', '基本感染率',
         '最适温度范围中心', '温度窗口步长', '降水窗口步长', '滑动窗口步长',
         '迭代次数', '种群规模', '二进制编码长度', '交叉概率', '变异概率']},
    {"模型名称": "PLSR",
     "模型参数": {"n_components": "2", "scale": "True", "max_iter": "500"},
     "备注": ['成分数量', '是否缩放', '最大迭代次数']},
    {"模型名称": "LR",
     "模型参数": {"fit_intercept": "True"},
     "备注": ['是否拟合截距']},
    {"模型名称": "SVR", "模型参数": {
        "kernel": "linear", "C": "1.0", "epsilon": "0.1"
    },
     "备注": ['核函数', '惩罚系数', ' 损失函数中的松弛变量']}
]


def mergeArray(list1, list2, list3):
    return list(set().union(*[list1, list2, list3]))


# 获取模型选项值对应名称
def getCheckboxName():
    for indexH in range(checkBoxModelNum):
        if st.session_state[f'checkBoxModel{indexH}']:
            temp1 = f'checkBoxModel{indexH}'
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
    # 若已经在可视化展示状态,则默认返回任务清单
    st.session_state.page15 = 0
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
    isHandledFlags = pages_utils.TempDataSetField[4]["处理状态"]
    # print('============测试抽取数据集==============')
    inputDataSet = pages_utils.TempDataSet[4]
    # print(inputDataSet)

    with emptyHeadMBP:
        with st.spinner('训练模型中...'):
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
                # print(pages_utils.TempDataSetField[4])
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
                for index1, row1 in pages_utils.TempDataSetField[4].iterrows():
                    if row1["编号"] == idNumber[tempIndex]:
                        for key, value in update_values.items():
                            pages_utils.TempDataSetField[4].at[index1, key] = value

            # print('==============更新后指标================')
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
    if cboxList[4]:
        st.session_state["modelPrecisionName"].append('RMSE')
    # print(st.session_state["modelPrecisionName"])
    pages_utils.TempDataSetField[4]['评价指标'] = ','.join(st.session_state["modelPrecisionName"])
    st.session_state.page += 1


def firstPage(): st.session_state.page = 0


def backPage(): st.session_state.page15 = 0


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
                    if st.session_state["leftTabs"][i] != '模型':
                        if st.session_state["leftTabs"][i] == '原始数据':
                            column = ['数据类型', '字段', '上传时间']
                            st.data_editor(
                                pages_utils.TempDataSet[0],
                                height=220, width=800, )
                        elif st.session_state["leftTabs"][i] == '预处理后数据集':
                            column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
                            st.data_editor(
                                pages_utils.TempDataSet[1],
                                height=220, width=800, )
                        elif st.session_state["leftTabs"][i] == '备选特征':
                            column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
                            st.data_editor(
                                pages_utils.TempDataSet[2],
                                height=220, width=800, )
                        elif st.session_state["leftTabs"][i] == '优选特征':
                            column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
                            st.data_editor(
                                pages_utils.TempDataSet[3],
                                height=220, width=800, )
                        # column_order=column)
                    else:
                        column = ["编号", "模型", "评价指标", "数据集划分比例", "时间", "下载模型结构、结果和参数值"]
                        st.data_editor(
                            pages_utils.TempDataSetField[i],
                            height=220, width=800,
                            column_order=column)

    if st.session_state.page12 == 1:
        with placeholder1.container():
            if pages_utils.TempDataSet[4].columns.tolist() == pages_utils.TempDataSet[3].columns.tolist():
                tt = st.tabs(['优选特征'])
                with tt[0]:
                    st.data_editor(
                        pages_utils.TempDataSet[3],
                        height=220, width=800, )
            else:
                tt = st.tabs(['优选特征', '模型'])
                with tt[0]:
                    st.data_editor(
                        pages_utils.TempDataSet[3],
                        height=220, width=800, )
                with tt[1]:
                    column = ["编号", "模型", "评价指标", "数据集划分比例", "时间", "下载模型结构、结果和参数值"]
                    st.data_editor(
                        pages_utils.TempDataSetField[4],
                        height=220, width=800,
                        column_order=column)

    # ===============显示左下字段或特征及获取===============
    # weatherNameList, plantNameList, agricultureNameList = ['无1'], ['无2'], ['无3']
    # if not pages_utils.TempDataSetField[3].empty:
    weatherNameT0, plantNameT0, agricultureNameT0 = pages_utils.getDataFiled(0, pages_utils.TempDataSetField[0])
    weatherNameT1, plantNameT1, agricultureNameT1 = pages_utils.getDataFiled(1, pages_utils.TempDataSetField[1])
    weatherNameT2, plantNameT2, agricultureNameT2 = pages_utils.getDataFiled(2, pages_utils.TempDataSetField[2])
    weatherNameT3, plantNameT3, agricultureNameT3 = pages_utils.getDataFiled(3, pages_utils.TempDataSetField[3])

    weatherNameList = weatherNameT1 + weatherNameT2 + weatherNameT0 + weatherNameT3
    plantNameList = plantNameT1 + plantNameT2 + plantNameT1 + plantNameT0 + plantNameT3
    agricultureNameList = agricultureNameT1 + agricultureNameT0 + agricultureNameT3
    modelACVCol1, modelACVCol2 = st.columns([0.7, 0.4])
    with modelACVCol1:
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
    with modelACVCol2:
        st.markdown("")
        st.markdown("###### 标签\n")
        resultLabel = st.selectbox(
            'predictLabel',
            filterUnique(weatherNameList + plantNameList + agricultureNameList, pages_utils.reservedField),
            label_visibility='collapsed')

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
                formatted_data = []

                # Loop through model_params to find the desired model and extract its details
                for entry in model_params:
                    if entry.get("模型名称") == model:
                        # Unpack the parameters and remarks together
                        for param_name, param_value in entry["模型参数"].items():
                            remark = entry["备注"].pop(0)  # Get the corresponding remark for each parameter
                            formatted_data.append({
                                # "模型名称": model,
                                "参数名": param_name,
                                "参数值": param_value,
                                "备注": remark
                            })
                df = pd.DataFrame(formatted_data)
                # st.table(df)
                edited_df = st.data_editor(df, height=190, width=800,
                                           disabled=["参数名", "备注"])
                # 删除 '备注' 列
                edited_df_no_remark = edited_df.drop(columns=["备注"])
                st.session_state["modelParamName"] = edited_df_no_remark.to_dict()

            # =======================准备任务清单内容=======================
            if st.session_state.nextBtnShow == 0:
                interval_col1, interval_col2 = st.columns([5, 1])
                btn1 = interval_col2.button("下一步", on_click=onModel)
            else:
                interval_col1, interval_col2 = st.columns([5, 1])
                btn = interval_col2.button("添加模型", on_click=onAddModel)
                # =======================添加模型=======================
                if btn:
                    # 检测目标连续/回归变量对应分类/回归模型
                    # 根据唯一值数据占比判断
                    dfT = pages_utils.TempDataSet[3]
                    dataRation = dfT[resultLabel].nunique() / len(dfT[resultLabel])
                    addModelFlag = True
                    # 占比<0.005
                    if dataRation < (5 * 0.001):
                        model_mapping1 = {
                            'agree': 'SVM',
                            'agree1': 'RF',
                            'agree2': 'KNN',
                            'agree3': 'FLDA'
                        }
                        # 查找第一个满足条件的 key
                        for _, message in model_mapping1.items():

                            if message == getModelName(st.session_state["modelName"]['checkBoxModel']):
                                addModelFlag = False
                                st.toast(f'{message}不支持回归模型构建', icon="⚠️")
                                time.sleep(1)
                    else:
                        model_mapping2 = {
                            'agree4': 'SEIR机理模型',
                            'agree5': 'PLSR',
                            'agree6': 'LR',
                            'agree7': 'SVR'
                        }
                        # 查找第一个满足条件的 key
                        for condition, message in model_mapping2.items():
                            if condition == getModelName(st.session_state["modelName"]['checkBoxModel']):
                                addModelFlag = False
                                st.toast(f'{message}不支持分类模型构建', icon="⚠️")
                                time.sleep(1)
                    # 若无错误选择模型
                    if addModelFlag:
                        # 隐藏添加模型按钮
                        st.session_state.nextBtnShow = 0
                        new_data = {
                            "编号": pages_utils.generateID(),
                            "模型": getModelName(st.session_state["modelName"]['checkBoxModel']),
                            "模型参数": st.session_state["modelParamName"],
                            "特征": result1 + result2 + result3,
                            "标签": resultLabel,
                            "时间": datetime.datetime.now().time(),
                            "处理状态": False}
                        print('======================模型构建-添加模型======================')
                        print(new_data)
                        pages_utils.TempDataSetField[4].loc[len(pages_utils.TempDataSetField[4])] = new_data
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

            # 检测判断精度指标回归/分类
            classify_models = ['SVM', 'FLDA', 'KNN', 'RF']
            regression_models = ['LR', 'SVR', 'PLSR', 'SEIR机理模型']

            model_name = getModelName(st.session_state["modelName"]['checkBoxModel'])

            if model_name in classify_models:
                if agree8 or agree9 or agree10:
                    st.toast(f'该指标不支持回归模型', icon="⚠️")
            if model_name in regression_models:
                if agree6 or agree7:
                    st.toast(f'该指标不支持分类模型', icon="⚠️")

            interval_col1, interval_col2 = st.columns([5, 1])
            # 传入指标
            btn21 = interval_col2.button(
                "下一步",
                on_click=onPrecision,
                args=[agree6, agree7, agree8, agree9, agree10])

    # Page 2
    elif st.session_state.page == 2:
        # =======================添加验证与训练数据集划分=======================
        with ph.container():
            # st.markdown("###### 有效特征集提取")
            # 检查是否有缺失值
            for p in range(len(pages_utils.TempDataSet) - 2, -1, -1):
                beforeDF = pages_utils.TempDataSet[p]
                if not beforeDF.empty:
                    break
            if 'DayOfYear' not in beforeDF.columns:
                beforeDF['DayOfYear'] = 0
            beforeDF = beforeDF[result1 + result2 + result3 + [resultLabel] + pages_utils.reservedField]

            # 若是SEIR机理模型则保留DayOfYear
            if 'SEIR机理模型' not in pages_utils.TempDataSetField[4]["模型"].tolist():
                # 分组并提取每个分组的第一个非空值
                result = beforeDF.groupby(['经度', '纬度', '年']).first().reset_index()
                # ******删除DayOfYear列******
                df_cleaned = result.drop('DayOfYear', axis=1)
                pages_utils.TempDataSet[4] = df_cleaned
            else:
                pages_utils.TempDataSet[4] = beforeDF
            st.markdown('###### 最终输入模型特征预览')
            st.dataframe(pages_utils.TempDataSet[4], width=700, height=200)
            # st.markdown('---')
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

            for index, row in pages_utils.TempDataSetField[4].iterrows():
                pages_utils.TempDataSetField[4].loc[index, '数据集划分比例'] = option

            # 将列名列表赋值给 '特征' 列
            pages_utils.TempDataSetField[4]['特征'] = [result1 + result2 + result3] * len(
                pages_utils.TempDataSetField[4])
            interval_col1, interval_col2 = st.columns([5, 1])
            interval_col2.button("保存", on_click=firstPage)

    # =======================显示右下内容=======================
    placeholder = st.empty()
    if st.session_state.page15 == 0:
        # =======================显示右下任务清单表格=======================
        with placeholder.container():
            st.markdown('##### 任务清单')
            pages_utils.TempDataSetField[4] = st.data_editor(
                pages_utils.TempDataSetField[4], height=190, width=800,
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
            models = pages_utils.TempDataSetField[4]["模型"].tolist()
            evaluationIndex = pages_utils.TempDataSetField[4]["评价指标"].tolist()
            targets = pages_utils.TempDataSetField[4]["标签"].tolist()
            # actualAndPredictList = pages_utils.TempDataSetField[4]["模型训练结果"].tolist()
            # print(print(actualAndPredictList))
            tt1 = st.tabs(models)
            for i in range(len(models)):
                with tt1[i]:
                    # print(actualAndPredictList)
                    # y_Actual = actualAndPredictList[i]['predictLabel']
                    # y_Predicted = actualAndPredictList[i]['actualLabel']
                    # print(f'=============可视化{y_Actual}{y_Predicted}=============')
                    # 创建模拟的混淆矩阵
                    rootPath = os.path.join(RESOURCE_MODELRESULT_PATH, 'predict')
                    testLabelDF = pd.read_excel(
                        os.path.join(rootPath,
                                     models[i] + '_testLabel.xlsx'))
                    predictLabelDF = pd.read_excel(
                        os.path.join(rootPath,
                                     models[i] + '_predictLabel.xlsx'))
                    # 假设第一列包含要绘制的数据
                    actual_values = testLabelDF.iloc[:, 0]
                    predicted_values = predictLabelDF.iloc[:, 0]
                    try:
                        # 回归模型
                        if models[i] == 'LR' or models[i] == 'SVR' or models[i] == 'PLSR' or models[
                            i] == 'SEIR机理模型':
                            # 绘制散点图
                            fig, ax = plt.subplots()

                            sns.scatterplot(x=actual_values, y=predicted_values)
                            plt.plot([actual_values.min(), actual_values.max()],
                                     [actual_values.min(), actual_values.max()],
                                     'r--')
                            ax.set_xlabel('实际峰值(%)')
                            ax.set_ylabel('预测峰值(%)')
                            # plt.figure(figsize=(10, 6))
                            plt.figtext(0.5, -0.03,
                                        f'图{IMAGECOUNT + 1} {models[i]}模型精度评价散点图',
                                        ha='center', fontsize=16)
                            # 精度结果直接显示在图中
                            metrics_text = "\n".join(
                                [f"{key}={round(value, 3)}" for key, value in evaluationIndex[i].items()])
                            plt.text(0.05, 0.95, metrics_text, transform=ax.transAxes, fontsize=10,
                                     verticalalignment='top', bbox=dict(facecolor='white', alpha=0.2))
                            st.pyplot(fig)

                        # 分类模型
                        elif models[i] == 'SVM' or models[i] == 'RF' or models[i] == 'FLDA' or models[i] == 'KNN':
                            actual_values = testLabelDF.iloc[:, 0]
                            predicted_values = predictLabelDF.iloc[:, 0]
                            # 绘制混淆矩阵图
                            fig, ax = plt.subplots()
                            conf_matrix = confusion_matrix(actual_values, predicted_values)
                            sns.heatmap(conf_matrix, annot=True, cmap='plasma', fmt='g', ax=ax)
                            ax.set_xlabel('实际病害发生程度')
                            ax.set_ylabel('预测病害发生程度')
                            plt.title(f'{models[i]}模型精度评价-混淆矩阵')
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
                    except BaseException:
                        st.toast('运行出错,点击返回上一步', icon="⚠️")
                    finally:
                        st.session_state.page = 0
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('返回', on_click=backPage)
