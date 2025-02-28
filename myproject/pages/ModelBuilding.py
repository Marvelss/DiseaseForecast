import datetime
import os.path
import time

import streamlit_antd_components as sac

import streamlit as st
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from st_pages import hide_pages
import matplotlib.cm as cm
from streamlit import switch_page

from lib.share import RESOURCE_MODELRESULT_PATH, IMAGECOUNT, PAGES_PATH
from lib.utils import filterUnique
from pages import pages_utils
from pages.modelandmethod.Model import Model

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
    # st.toast('已根据默认设置勾选特征与建模方法', icon="ℹ️")

if 'pageMBIsInit' not in st.session_state:
    st.session_state.pageMBIsInit = 0

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
st.markdown("""
    <style>
        div [data-baseweb=select]  {
            max-height: 150px;
            overflow: auto;
        }
    </style>
    """, unsafe_allow_html=True)
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
st.header('模型构建',
          help='训练并验证模型', divider='grey', anchor=False)

sac.steps(
    items=[
        sac.StepsItem(title='原始建模数据', disabled=True),
        sac.StepsItem(title='气象数据预处理', disabled=True),
        sac.StepsItem(title='特征计算', disabled=True),
        sac.StepsItem(title='特征优选', disabled=True),
        sac.StepsItem(title='模型构建', disabled=True),
        sac.StepsItem(title='模型应用', disabled=True),
    ], index=4, color='#008000'
)

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


def getModelName1():
    modelListTemp = []
    if agree:
        modelListTemp.append('SVM')
    if agree1:
        modelListTemp.append('RF')
    if agree2:
        modelListTemp.append('KNN')
    if agree3:
        modelListTemp.append('FLDA')
    if agree5:
        modelListTemp.append('PLSR')
    if agree6:
        modelListTemp.append('LR')
    if agree7:
        modelListTemp.append('SVR')
    return modelListTemp


def getModelParam(modelT):
    formatted_dataT = []
    # Loop through model_params to find the desired model and extract its details
    for entryT in model_params:
        if entryT.get("模型名称") == modelT:
            # Unpack the parameters and remarks together
            for param_nameT, param_valueT in entryT["模型参数"].items():
                formatted_dataT.append({
                    # "模型名称": model,
                    "参数名": param_nameT,
                    "参数值": param_valueT,
                })
    return pd.DataFrame(formatted_dataT).to_dict()


# 取消其他选项按钮
def clearOtherOption(key1):
    # 显示添加模型按钮
    # st.session_state.nextBtnShow = 0 if st.session_state.nextBtnShow == 1 else 1

    # st.markdown(key)
    for h in range(checkBoxModelNum):
        if h != key1:
            st.session_state[f'checkBoxModel{h}'] = False
    # 若已经在可视化展示状态,则默认返回任务清单
    # st.session_state.page15 = 0
    return


# 模型训练
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
    dataPartitioning = pages_utils.TempDataSetField[4]["数据集划分比例"].tolist()
    features = pages_utils.TempDataSetField[4]["特征"].tolist()
    targets = pages_utils.TempDataSetField[4]["标签"].tolist()
    isHandledFlags = pages_utils.TempDataSetField[4]["处理状态"]
    # print('============测试抽取数据集==============')
    # 训练的数据集直接使用备选特征环节数据
    pages_utils.TempDataSet[4] = pages_utils.TempDataSet[2]
    inputDataSet = pages_utils.TempDataSet[4]
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
                # 转换类型
                if isinstance(modelParam[tempIndex], str):
                    modelParam[tempIndex] = eval(modelParam[tempIndex])

                if tempModel == 'SVM':
                    evaluationResult, actualAndPredictResult, modelStruct = Model(
                        inputDataSet,
                        features[tempIndex], targets[tempIndex],
                        dataPartitioning[tempIndex], modelParam[tempIndex],
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
                        dataPartitioning[tempIndex], modelParam[tempIndex],
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
                        dataPartitioning[tempIndex], modelParam[tempIndex],
                        evaluationIndicator[tempIndex]).onFLDA()

                    # 显示模型训练结果信息
                    info = ''
                    for key, value in evaluationResult.items():
                        info += f'{key}:{str(round(value, 3))}' + '       '
                    # 显示精度结果
                    st.toast('FLDA训练完成 \n' + '       ' + ' \n' + info,
                             icon='✅')
                elif tempModel == 'RF':
                    print('-' * 20)
                    print(modelParam[tempIndex])
                    evaluationResult, actualAndPredictResult, modelStruct = Model(
                        inputDataSet,
                        features[tempIndex], targets[tempIndex],
                        dataPartitioning[tempIndex], modelParam[tempIndex],
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
                        dataPartitioning[tempIndex], modelParam[tempIndex],
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
                        dataPartitioning[tempIndex], modelParam[tempIndex],
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
                        dataPartitioning[tempIndex], modelParam[tempIndex],
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
                            dataPartitioning[tempIndex], modelParam[tempIndex],
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
                # 精度结果保留三位小数
                for keyT1, valueT1 in evaluationResult.items():
                    # 格式化每个值为三位小数
                    evaluationResult[keyT1] = round(valueT1, 3)
                # 显示精度结果
                update_values = {
                    "时间": datetime.datetime.now().time(),
                    "评价指标": evaluationResult,
                    "模型训练结果": actualAndPredictResult,
                    "模型结构": modelStruct,
                    "处理状态": True}
                # print('======更新指标======')
                # print(update_values)
                # 查找要更新的数据记录
                for index1, row1 in pages_utils.TempDataSetField[4].iterrows():
                    if row1["编号"] == idNumber[tempIndex]:
                        for key, value in update_values.items():
                            pages_utils.TempDataSetField[4].at[index1, key] = value

            # print('==============更新后指标================')
            # print(pages_utils.TempDataSetField[4])


def onAddModel():
    # print(st.session_state["modelParamName"])
    for h in range(checkBoxModelNum):
        if st.session_state[f'checkBoxModel{h}']:
            st.session_state["modelName"]['checkBoxModel'] = f'checkBoxModel{h}'
        st.session_state[f'checkBoxModel{h}'] = False
    return


# 获取模型
def onModel(*cboxList):
    if cboxList[0]:
        st.session_state["modelPrecisionName"].append('OA')
    if cboxList[1]:
        st.session_state["modelPrecisionName"].append('Kappa')
    if cboxList[2]:
        st.session_state["modelPrecisionName"].append('MSE')


# 获取评价指标
def onPrecision(modelName):
    precisionListT = []
    # print('传入接收参数')
    if modelName == 'SVM' or modelName == 'FLDA' or modelName == 'KNN' or modelName == 'RF':
        precisionListT.append('OA')
        precisionListT.append('Kappa')
    elif modelName == 'LR' or modelName == 'SVR' or modelName == 'PLSR':
        precisionListT.append('MSE')
        precisionListT.append('R方')
        precisionListT.append('RMSE')
    precisionStrT = ','.join(precisionListT)
    return precisionStrT


def firstPage(): st.session_state.page = 0


def backPage(): st.session_state.page15 = 0


# ==============================界面==============================
modelACV, modelACM = st.columns([0.5, 0.5])
with modelACV:
    # st.markdown("##### 特征与模型")

    # =======================显示左侧特征与模型=======================
    # placeholder1 = st.empty()
    # if st.session_state.page12 == 0:
    #     with placeholder1.container():
    #         tt1 = st.tabs(['优选特征'])
    #         with tt1[0]:
    #             st.data_editor(
    #                 pages_utils.TempDataSet[2],
    #                 height=220, width=800, )
    #         # tt1 = st.tabs(st.session_state["leftTabs"])
    #         # for i in range(len(st.session_state["leftTabs"])):
    #         #     with tt1[i]:
    #         #         if st.session_state["leftTabs"][i] != '模型':
    #         #             if st.session_state["leftTabs"][i] == '原始建模数据':
    #         #                 column = ['数据类型', '字段', '上传时间']
    #         #                 st.data_editor(
    #         #                     pages_utils.TempDataSet[0],
    #         #                     height=220, width=800, )
    #         #             elif st.session_state["leftTabs"][i] == '预处理后数据集':
    #         #                 column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
    #         #                 st.data_editor(
    #         #                     pages_utils.TempDataSet[1],
    #         #                     height=220, width=800, )
    #         #             elif st.session_state["leftTabs"][i] == '备选特征':
    #         #                 column = ["数据类型", "备选特征", "大小", "特征计算方法", '时间']
    #         #                 st.data_editor(
    #         #                     pages_utils.TempDataSet[2],
    #         #                     height=220, width=800, )
    #         #             elif st.session_state["leftTabs"][i] == '优选特征':
    #         #                 column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间']
    #         #                 st.data_editor(
    #         #                     pages_utils.TempDataSet[3],
    #         #                     height=220, width=800, )
    #         #             # column_order=column)
    #         #         else:
    #         #             column = ["编号", "模型", "评价指标", "数据集划分比例", "时间", "下载模型结构、结果和参数值"]
    #         #             st.data_editor(
    #         #                 pages_utils.TempDataSetField[i],
    #         #                 height=220, width=800,
    #         #                 column_order=column)
    #
    # if st.session_state.page12 == 1:
    #     with placeholder1.container():
    #         if pages_utils.TempDataSet[4].columns.tolist() == pages_utils.TempDataSet[3].columns.tolist():
    #             tt = st.tabs(['优选特征'])
    #             with tt[0]:
    #                 st.data_editor(
    #                     pages_utils.TempDataSet[2],
    #                     height=220, width=800, )
    #         else:
    #             tt = st.tabs(['优选特征', '模型'])
    #             with tt[0]:
    #                 st.data_editor(
    #                     pages_utils.TempDataSet[2],
    #                     height=220, width=800, )
    #             with tt[1]:
    #                 column = ["编号", "模型", "评价指标", "数据集划分比例", "时间", "下载模型结构、结果和参数值"]
    #                 st.data_editor(
    #                     pages_utils.TempDataSetField[4],
    #                     height=220, width=800,
    #                     column_order=column)

    # ===============显示左下字段或特征及获取===============
    # weatherNameList, plantNameList, agricultureNameList = ['无1'], ['无2'], ['无3']
    # if not pages_utils.TempDataSetField[3].empty:
    # weatherNameT0, plantNameT0, agricultureNameT0 = pages_utils.getDataFiled(0, pages_utils.TempDataSetField[0])
    # weatherNameT1, plantNameT1, agricultureNameT1 = pages_utils.getDataFiled(1, pages_utils.TempDataSetField[1])
    # weatherNameT2, plantNameT2, agricultureNameT2 = pages_utils.getDataFiled(2, pages_utils.TempDataSetField[2])
    # weatherNameT3, plantNameT3, agricultureNameT3 = pages_utils.getDataFiled(3, pages_utils.TempDataSetField[3])
    #
    # weatherNameList = weatherNameT1 + weatherNameT2 + weatherNameT0 + weatherNameT3
    # plantNameList = plantNameT1 + plantNameT2 + plantNameT1 + plantNameT0 + plantNameT3
    # agricultureNameList = agricultureNameT1 + agricultureNameT0 + agricultureNameT3
    # getTempPF = pages_utils.TempDataSet[3].columns.tolist()
    # preferenceFeature, otherFeature = [], []
    # for tempTPF in getTempPF:
    #     if '-优选' in tempTPF:
    #         preferenceFeature.append(tempTPF)
    #     else:
    #         otherFeature.append(tempTPF)
    # # 剔除在其他特征中重复的优选特征
    # otherFeature = [ofT for ofT in otherFeature if not any(ofT in prT for prT in preferenceFeature)]

    _, plantNameT0, agricultureNameT0 = pages_utils.getDataFiled(0, pages_utils.TempDataSetField[0])
    # st.markdown("##### 特征与预测目标变量")
    with st.container(border=True):
        modelACVCol1, modelACVCol2 = st.columns([0.6, 0.3])
        with modelACVCol1:
            st.markdown("##### 特征选择")
            # 按照数据类型显示左侧字段或特征
            result1 = pages_utils.multiselect_all_checked(
                st, '全选-优选特征', filterUnique(st.session_state.preferenceFeature, []),
                'tempTemperature', 'collapsed')
            # 去除年、月、年内日期等字段
            result2 = pages_utils.multiselect_all(
                st, '全选-其他特征', filterUnique(pages_utils.TempDataSet[2].columns.tolist(),
                                                  st.session_state.preferenceFeature +
                                                  pages_utils.reservedField +
                                                  ['日期', '年内日期', '月', '旬'] +
                                                  plantNameT0 +
                                                  # 预处理环节的数据，排除地理遥感数据
                                                  filterUnique(pages_utils.TempDataSet[1].columns.tolist(),
                                                               agricultureNameT0)),
                'tempPlant', 'collapsed')
        with modelACVCol2:
            # st.markdown("")
            st.markdown("##### 预测目标变量选择")
            resultLabel = st.selectbox(
                'predictLabel',
                filterUnique(plantNameT0, pages_utils.reservedField),
                label_visibility='collapsed')

    # st.markdown('---')
    # =======================添加验证与训练数据集划分=======================
    with st.container(border=True):
        st.markdown("##### 训练与验证数据集划分")
        st.info(f'建模数据样本量:{pages_utils.TempDataSet[2].shape[0]}条', icon="ℹ️️")

        colOP1, colOP2 = st.columns(2)
        with colOP1:
            option1 = st.selectbox(
                label="训练与验证数据集划分", label_visibility='collapsed',
                options="按比例划分"
            )
        with colOP2:
            if option1 == '按比例划分':
                option = st.selectbox(
                    label="比例", label_visibility='collapsed',
                    options=("7:3", "8:2", "6:4")
                )
            # elif option1 == '按年份划分(未实现)':
            #     option = st.selectbox(
            #         label="年", label_visibility='collapsed',
            #         options=('待实现', '')
            #     )
    # ===============显示右上模型选项===============
    with st.container(border=True):
        st.markdown("##### 建模方法")
        st.warning('注意：分类模型针对离散变量；回归模型针对连续变量', icon="⚠️")
        # 按模型分类显示
        st.markdown("###### 分类模型（离散变量）")
        colOption1, colOption2, colOption3, colOption4 = st.columns(4)
        with colOption1:
            agree = st.checkbox('SVM', key='checkBoxModel0', args=[0], on_change=clearOtherOption)
            # agree6 = st.checkbox('LR', key='checkBoxModel6', on_change=clearOtherOption, args=[6])
        with colOption2:
            agree1 = st.checkbox('RF', key='checkBoxModel1', args=[1], on_change=clearOtherOption)

        with colOption3:
            agree3 = st.checkbox('FLDA', key='checkBoxModel3', args=[3], on_change=clearOtherOption)

        with colOption4:
            agree2 = st.checkbox('KNN', key='checkBoxModel2', args=[2], on_change=clearOtherOption)
            # agree4 = st.checkbox('贝叶斯统计')
            # agree5 = st.checkbox('模糊综合评价')
        st.markdown("###### 回归模型（连续变量）")
        colOption21, colOption22, colOption23, colOption24 = st.columns(4)
        with colOption21:
            agree6 = st.checkbox('LR', key='checkBoxModel6', on_change=clearOtherOption, args=[6])
        with colOption22:
            agree7 = st.checkbox('SVR', key='checkBoxModel7', on_change=clearOtherOption, args=[7])
        with colOption23:
            agree5 = st.checkbox('PLSR', key='checkBoxModel5', on_change=clearOtherOption, args=[5])
        with colOption4:
            pass
        # st.markdown("###### 机理模型")
        # colOption31, colOption32, = st.columns(2)
        # with colOption31:
        #     agree4 = st.checkbox('SEIR机理模型', key='checkBoxModel4', on_change=clearOtherOption, args=[4])
        # with colOption32:
        #     pass

        # st.markdown('---')

        # ===============显示和处理右中各个模型参数(主要添加模型时加入checkbox名称)===============
        if agree or agree1 or agree2 or agree2 or agree3 or agree5 or agree6 or agree7:
            model = getModelName1().pop()
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
            with st.expander('高级设置'):
                edited_df = st.data_editor(df, height=190, width=900,
                                           disabled=["参数名", "备注"])
                # 删除 '备注' 列
                edited_df_no_remark = edited_df.drop(columns=["备注"])
            st.session_state["modelParamName"] = edited_df_no_remark.to_dict()

        # st.info('当前时间分辨率为:1天')
        # temporaResolutionNum = st.text_input("统一时间分辨率(天)", value=1)
        btn = st.columns([4, 1])[1].button('添加模型', on_click=onAddModel)
        if btn:
            # =======================准备任务清单内容=======================
            new_dataTT = {
                "编号": pages_utils.generateID(),
                "模型": getModelName(st.session_state["modelName"]['checkBoxModel']),
                "模型参数": st.session_state["modelParamName"],
                "特征": result1 + result2,
                "标签": resultLabel,
                "评价指标": onPrecision(getModelName(st.session_state["modelName"]['checkBoxModel'])),
                "数据集划分比例": option,
                "时间": datetime.datetime.now().time(),
                "处理状态": False}
            print('======================模型构建-添加模型======================')
            print(new_dataTT)
            pages_utils.TempDataSetField[4].loc[len(pages_utils.TempDataSetField[4])] = new_dataTT
        # 自动添加
        # if not st.session_state.pageMBIsInit:
        if 1 == 0:
            st.session_state.pageMBIsInit += 1
            # 通过判断预测目标变量在0-5内判断分类模型(未添加代码)
            for modelNameTemp1 in ['SVM', 'RF', 'FLDA', 'KNN']:
                # =======================准备任务清单内容=======================
                new_dataT = {
                    "编号": pages_utils.generateID(),
                    "模型": modelNameTemp1,
                    "模型参数": getModelParam(modelNameTemp1),  # getModelParam(modelNameTemp1)
                    "特征": filterUnique(st.session_state.preferenceFeature, []),  # result1 + result2
                    "标签": filterUnique(plantNameT0, pages_utils.reservedField)[0],
                    "评价指标": onPrecision(modelNameTemp1),
                    "时间": datetime.datetime.now().time(),
                    "数据集划分比例": option,
                    "处理状态": False}
                # print('======================模型构建-自动添加模型======================')
                # print(new_dataT)
                pages_utils.TempDataSetField[4].loc[len(pages_utils.TempDataSetField[4])] = new_dataT

with modelACM:
    # ph = st.empty()
    # Page 0
    # if st.session_state.page == 0:
    #     with ph.container():

    # =======================显示右下内容=======================
    # placeholder = st.empty()
    # if st.session_state.page15 == 0:
    # =======================显示右下任务清单表格=======================
    # with placeholder.container():
    with st.container(border=True):
        st.markdown('##### 任务清单')
        # st.info('本环节已默认勾选上一环节优选的特征及可训练的模型，用户也可以自行选用其他特征建模', icon="ℹ️")

        pages_utils.TempDataSetField[4] = st.data_editor(
            pages_utils.TempDataSetField[4], height=273, width=1200,
            column_order=["模型", "标签", "特征", "评价指标", "数据集划分比例", "时间", '处理状态'],
            disabled=["时间", '处理状态'], num_rows="dynamic", )

        btn2 = st.columns([5, 1])[1].button('运行', on_click=onTrain)
    placeholder = st.empty()

    # =======================显示右下可视化图表=======================
    # elif st.session_state.page15 == 1:
    with placeholder.container(border=True, height=435):
        # st.markdown('---')
        st.write('##### 建模结果')
        if st.session_state.page15 >= 1:
            evaluationIndex = pages_utils.TempDataSetField[4]["评价指标"].tolist()
            for i in range(len(evaluationIndex)):
                item = evaluationIndex[i]
                if isinstance(item, dict):
                    evaluationIndex[i] = '、'.join([f'{key}={round(value, 3)}' for key, value in item.items()])
                else:
                    evaluationIndex[i] = '、'.join([f'{key}={round(value, 3)}' for key, value in eval(item).items()])
            models = pages_utils.TempDataSetField[4]["模型"].tolist()
            # 创建一个新的 DataFrame，组合精度评价和模型
            # st.toast(evaluationIndex)
            tempResult = pd.DataFrame({
                '模型': models,
                '精度': evaluationIndex
            })
            st.table(tempResult)
            # targets = pages_utils.TempDataSetField[4]["标签"].tolist()
            # isHandledFlagsT = pages_utils.TempDataSetField[4]["处理状态"]

            # actualAndPredictList = pages_utils.TempDataSetField[4]["模型训练结果"].tolist()
            # print(print(actualAndPredictList))

            # 计算处理状态为True的模型数量
            # handled_models = [model for model, is_handled in zip(models, isHandledFlagsT) if is_handled]
            # # 创建tabs
            # tt1 = st.tabs(handled_models)
            # for i in range(len(handled_models)):
            #     with tt1[i]:
            #         try:
            #             rootPath = os.path.join(RESOURCE_MODELRESULT_PATH, 'predict')
            #             testLabelDF = pd.read_excel(
            #                 os.path.join(rootPath,
            #                              models[i] + '_testLabel.xlsx'))
            #             predictLabelDF = pd.read_excel(
            #                 os.path.join(rootPath,
            #                              models[i] + '_predictLabel.xlsx'))
            #             # 假设第一列包含要绘制的数据
            #             actual_values = testLabelDF.iloc[:, 0]
            #             predicted_values = predictLabelDF.iloc[:, 0]
            #             #
            #             # st.markdown("##### 验证集预测结果")
            #             # st.data_editor(testLabelDF)
            #
            #             # 区分回归分类模型
            #             if models[i] == 'LR' or models[i] == 'SVR' or models[i] == 'PLSR' or models[
            #                 i] == 'SEIR机理模型':
            #                 colMB1, colMB2 = st.columns(2)
            #                 with colMB1:
            #                     # 选择最多8个纬度
            #                     top_stations = predictLabelDF['纬度'].value_counts().nlargest(8).index
            #                     df_filtered_stations = predictLabelDF[predictLabelDF['纬度'].isin(top_stations)]
            #                     # 选择最多5个年份
            #                     top_years = predictLabelDF['年'].value_counts().nlargest(3).index
            #                     df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
            #                     # df_filtered['地区'] = df_filtered['纬度'].astype(str) + " " + df_filtered[
            #                     #     '经度'].astype(
            #                     #     str)
            #                     # Explicitly use .loc[] to avoid SettingWithCopyWarning
            #                     df_filtered.loc[:, '地区'] = df_filtered['纬度'].astype(str) + " " + df_filtered[
            #                         '经度'].astype(str)
            #
            #                     # 绘制柱状图
            #                     plt.figure(figsize=(10, 6))
            #                     sns.barplot(
            #                         data=df_filtered,
            #                         x="地区",
            #                         y='predictLabel',
            #                         hue="年",
            #                         dodge=True,
            #                         saturation=1
            #                     )
            #                     # 设置标签和标题
            #                     plt.gca().set_xlabel("")  # 隐藏x轴标题
            #                     plt.xticks(rotation=30)  # x轴标签旋转65度
            #                     plt.ylabel(testLabelDF.columns[0])
            #                     plt.figtext(0.5, -0.1,
            #                                 f'图{st.session_state.IMAGECOUNT} 部分地区各年份预测结果图',
            #                                 ha='center', fontsize=16)
            #                     st.pyplot(plt)
            #                 with colMB2:
            #                     # 绘制散点图
            #                     fig, ax = plt.subplots()
            #                     sns.scatterplot(x=actual_values, y=predicted_values)
            #                     plt.plot([actual_values.min(), actual_values.max()],
            #                              [actual_values.min(), actual_values.max()],
            #                              'r--')
            #                     ax.set_xlabel(f'实际{testLabelDF.columns[0]}')
            #                     ax.set_ylabel(f'预测{testLabelDF.columns[0]}')
            #                     # plt.figure(figsize=(10, 6))
            #                     plt.figtext(0.5, -0.03,
            #                                 f'图{IMAGECOUNT} {models[i]}模型精度评价结果图',
            #                                 ha='center', fontsize=16)
            #                     # 精度结果直接显示在图中
            #                     metrics_text = "\n".join(
            #                         [f"{key}={round(value, 3)}" for key, value in evaluationIndex[i].items()])
            #                     plt.text(0.05, 0.95, metrics_text, transform=ax.transAxes, fontsize=10,
            #                              verticalalignment='top', bbox=dict(facecolor='white', alpha=0.2))
            #                     st.pyplot(fig)
            #             else:
            #                 # colMB1, colMB2, colMB3 = st.columns([0.2, 0.5, 0.2])
            #                 # with colMB1:
            #                 #     pass
            #                 # 分类模型
            #                 # predictLabelDF = pd.read_excel(os.path.join(path1, f'{models[i]}_predictLabel.xlsx'))
            #                 # # 绘制二维平面散点图，只标记predictLabel为0和1的点
            #                 # # 分别绘制 predictLabel 为 0 和 1 的点
            #                 # fig, ax = plt.subplots()
            #                 # # 获取 'RdYlGn_r' colormap 对象，从绿到红
            #                 # cmap = plt.get_cmap('RdYlGn')
            #                 #
            #                 # # 假设有 5 个唯一的标签值
            #                 # unique_labels = predictLabelDF['predictLabel'].unique()
            #                 # num_colors = len(unique_labels)
            #                 #
            #                 # # 从 colormap 获取等间隔的颜色
            #                 # selected_colors = cmap(np.linspace(0, 1, num_colors))
            #                 # for idx, label in enumerate(unique_labels):
            #                 #     # print(f'获取颜色:{selected_colors[idx]}')
            #                 #     # print(label)
            #                 #     subset = predictLabelDF[predictLabelDF['predictLabel'] == label]
            #                 #     plt.scatter(subset['经度'], subset['纬度'], label=f'{label}', color=selected_colors[idx], s=100, alpha=0.6)
            #                 # # predicted_values = predictLabelDF.iloc[:, 0]
            #                 # ax.set_xlabel('经度')
            #                 # ax.set_ylabel('纬度')
            #                 # plt.legend(title=f'预测{testLabelDF.columns[0]}')
            #                 # # plt.title(f'{models[i]}模型混淆矩阵图')
            #                 # plt.figtext(0.5, -0.03,
            #                 #             f'图{st.session_state.IMAGECOUNT} {models[i]}模型部分预测结果图',
            #                 #             ha='center', fontsize=15)
            #                 # st.pyplot(fig)
            #                 # with colMB2:
            #                 # 绘制混淆矩阵图
            #                 # fig, ax = plt.subplots()
            #                 # conf_matrix = confusion_matrix(actual_values, predicted_values)
            #                 # sns.heatmap(conf_matrix, annot=True, cmap='Blues', fmt='g', ax=ax, cbar=False)
            #                 # # sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
            #                 # ax.set_xlabel(f'实际{testLabelDF.columns[0]}')
            #                 # ax.set_ylabel(f'预测{testLabelDF.columns[0]}')
            #                 # # plt.title(f'{models[i]}模型精度评价-混淆矩阵')
            #                 # # st.pyplot(fig)
            #                 # plt.figtext(0.5, -0.03,
            #                 #             f'图{st.session_state.IMAGECOUNT} {models[i]}模型混淆矩阵图',
            #                 #             ha='center', fontsize=15)
            #                 # 精度结果直接显示在图中
            #                 # metrics_text = "\n".join(
            #                 #     [f"{key}={round(value, 3)}" for key, value in evaluationIndex[i].items()])
            #                 # plt.text(-0.1, 0.97, metrics_text, transform=ax.transAxes, fontsize=10,
            #                 #          verticalalignment='top', bbox=dict(facecolor='white', alpha=0.1))
            #                 # st.columns([0.2, 0.5, 0.2])[1].pyplot(fig)
            #
            #                 st.markdown("###### 模型精度")
            #                 metrics = []
            #                 if isinstance(evaluationIndex[i], str):
            #                     evaluationIndex[i] = eval(evaluationIndex[i])
            #                 for key, value in evaluationIndex[i].items():
            #                     metrics.append((key, round(value, 3)))
            #                     half = len(metrics) // 2
            #                 col111, col211 = st.columns(2)
            #                 for h in range(half):
            #                     col211.metric(metrics[h][0], metrics[h][1])
            #                 for h in range(half, len(metrics)):
            #                     col111.metric(metrics[h][0], metrics[h][1])
            #                 # with colMB3:
            #                 #     pass
            #         except BaseException as e:
            #             raise e
            #             # st.toast('运行出错,点击返回上一步', icon="⚠️")
            #         finally:
            #             st.session_state.page = 0
            for _ in range(3):
                st.markdown('')
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('下一步')
            if btn3:
                switch_page(os.path.join(PAGES_PATH, 'ModelApplication.py'))
