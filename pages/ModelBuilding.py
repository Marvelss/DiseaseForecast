import datetime

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import confusion_matrix, accuracy_score, mean_squared_error, r2_score

import seaborn as sns

import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import SVC

import pages_utils

if 'page' not in st.session_state:
    st.session_state.page = 0
if 'page15' not in st.session_state:
    st.session_state.page15 = 0
# 处理方法内容记录(任务清单各项值)
if "modelName" not in st.session_state:
    st.session_state["modelName"] = {
        'checkBoxModel': None
    }

# 创建一个空的模型参数字典
model_params = [
    {"模型名称": "SVM", "参数1": "值1", "参数2": "值2", "参数3": "值3"},
    {"模型名称": "KNN", "K参数1": "K值1", "K参数2": "K值2", "K参数3": "值3"},
    {"模型名称": "FLDA", "F参数1": "F值1", "F参数2": "F值2", "F参数3": "值3"},
    {"模型名称": "RF", "R参数1": "R值1", "R参数2": "R值2", "R参数3": "值3"},
]

checkBoxModelNum = 4


# checkBoxPrecisionNum = 2

def getCheckboxName():
    for h in range(checkBoxModelNum):
        if st.session_state[f'checkBoxModel{h}']:
            temp = f'checkBoxModel{h}'
            print(f'--click{h}--')
            if temp == 'checkBoxModel0':
                return 'SVM'
            elif temp == 'checkBoxModel2':
                return 'KNN'
            elif temp == 'checkBoxModel1':
                return 'RF'
            elif temp == 'checkBoxModel3':
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
    print('-------------展示结果-------------')
    for key, value in pages_utils.TempDataSetField[4].items():
        print(key, value)

    # 训练模型
    # =======================获取优选特征数据集=======================
    # df11 = pages_utils.TempDataSet[3]
    # # 提取特征和目标变量
    # X = df11[['上级单位', '测报站点', "年", "DayOfYear", '降水累积量', '降水']]
    # Y = df11['峰值率']
    # # 对分类变量进行one-hot编码
    # X = pd.get_dummies(X, columns=['上级单位', '测报站点'])
    #
    # # =======================划分训练集和测试集=======================
    # X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    #
    # # =======================获取评价指标=======================
    #
    # # 训练模型
    # model = LinearRegression()
    # model.fit(X_train, y_train)
    #
    # # 预测
    # y_pred = model.predict(X_test)
    #
    # # 计算均方误差
    # mse = mean_squared_error(y_test, y_pred)
    # r2 = r2_score(y_test, y_pred)
    # st.markdown('---')
    # st.markdown(y_test)
    # st.markdown(y_pred)
    # st.markdown(mse)
    # st.markdown(r2)
    # # print("均方误差:", mse)
    #
    # data11 = {"模型": "SVM", "时间": datetime.datetime.now().time(),
    #           "下载模型结构、结果和参数值": False}
    # pages_utils.TempDataSetField[4].loc[len(
    #     pages_utils.TempDataSetField[4])] = data11


def onModel():
    # for h in range(checkBoxModelNum):
    #     if st.session_state[f'checkBoxModel{h}']:
    #         st.session_state["modelName"]['checkBoxModel'] = f'checkBoxModel{h}'
    #     st.session_state[f'checkBoxModel{h}'] = False
    st.session_state.page += 1
    return


def onAddModel():
    for h in range(checkBoxModelNum):
        if st.session_state[f'checkBoxModel{h}']:
            st.session_state["modelName"]['checkBoxModel'] = f'checkBoxModel{h}'
        st.session_state[f'checkBoxModel{h}'] = False
    return


def onPrecision():
    # for h in range(checkBoxPrecisionNum):
    #     if st.session_state[f'checkBoxPrecision{h}']:
    #         st.session_state["modelName"]['checkBoxPrecision'] = f'checkBoxPrecision{h}'
    #     st.session_state[f'checkBoxPrecision{h}'] = False
    st.session_state.page += 1


def firstPage(): st.session_state.page = 0


modelACV, modelACM = st.columns([0.5, 0.7])
with modelACV:
    st.markdown("##### 特征与模型")
    st.data_editor(pages_utils.TempDataSet[0])
    st.markdown(pages_utils.TempDataSet[1])
    st.markdown(pages_utils.TempDataSet[2])
    st.markdown(pages_utils.TempDataSet[3])
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
                        column = ["数据类型", "预处理后字段", "预处理方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '备选特征':
                        column = ["数据类型", "备选特征", "特征计算方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '优选特征':
                        column = ["数据类型", "优选特征", "特征优选方法", '时间', "下载数据集"]
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
                        column = ["数据类型", "预处理后字段", "预处理方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '备选特征':
                        column = ["数据类型", "备选特征", "特征计算方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '优选特征':
                        column = ["数据类型", "优选特征", "特征优选方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '模型':
                        column = ["编号", "模型", "评价指标", "数据集划分", "时间", "下载模型结构、结果和参数值"]
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)
    # =======================获取特征数据集表信息=======================
    tempDF = pages_utils.TempDataSetField[3]
    # 添加字段名称选项
    weatherName, plantName, agricultureName = ['无1'], ['无2'], ['无3']
    if tempDF[tempDF['数据类型'] == '气象数据']['优选特征'].any():
        weatherName.clear()
        weatherName = tempDF[tempDF['数据类型'] == '气象数据']['优选特征'].tolist()[0]
    if tempDF[tempDF['数据类型'] == '植保数据']['优选特征'].any():
        plantName.clear()
        plantName = tempDF[tempDF['数据类型'] == '植保数据']['优选特征'].tolist()[0]
    if tempDF[tempDF['数据类型'] == '农学数据']['优选特征'].any():
        # agricultureName.clear()
        agricultureName = tempDF[tempDF['数据类型'] == '农学数据']['优选特征'].tolist()[0]
    # =======================选择数据集=======================
    a = st.selectbox(
        '选择数据集',
        ('原始数据集', '预处理后数据集', '备选特征', '优选特征'))
    result1 = pages_utils.multiselect_all(
        st, '全选-气象数据',
        weatherName,
        'temp', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-植保数据', plantName,
        'temp', 'collapsed')
    result3 = pages_utils.multiselect_all(
        st, '全选-农学数据', agricultureName,
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
                agree1 = st.checkbox('RF', key='checkBoxModel1', on_change=clearOtherOption, args=[1])
            with colOption2:
                agree2 = st.checkbox('KNN', key='checkBoxModel2', on_change=clearOtherOption, args=[2])

            with colOption3:
                agree3 = st.checkbox('FLDA', key='checkBoxModel3', on_change=clearOtherOption, args=[3])
                # agree4 = st.checkbox('贝叶斯统计')
                # agree5 = st.checkbox('模糊综合评价')
            st.markdown('---')
            if agree or agree1 or agree2 or agree2 or agree3:
                model = getCheckboxName()
                print(f'--{model}--')
                # 获取SVM模型的参数
                svm_params_dict = {}
                for entry in model_params:
                    if entry.get("模型名称") == model:
                        svm_params_dict = {key: value for key, value in entry.items() if key != "模型名称"}

                # 转换参数格式
                formatted_params = [{"参数名": key, "参数值": value} for key, value in svm_params_dict.items()]
                df = pd.DataFrame(formatted_params)
                st.data_editor(df)
            interval_col1, interval_col2 = st.columns([5, 1])
            btn1 = interval_col2.button("下一步", on_click=onModel)
            btn = interval_col1.button("添加模型", on_click=onAddModel)
            if btn:
                new_data = {
                    "编号": pages_utils.generateID(),
                    "模型": getModelName(st.session_state["modelName"]['checkBoxModel']),
                    "模型参数": [value for key, value in st.session_state["preMethodName"].items() if
                                 key != 'checkBox'],
                    "时间": datetime.datetime.now().time(),
                    "下载模型结构、结果和参数值": False}
                print(new_data)
                pages_utils.TempDataSetField[4].loc[len(pages_utils.TempDataSetField[4])] = new_data
                st.rerun()
    # Page 1
    elif st.session_state.page == 1:
        with ph.container():
            st.markdown("###### 评价指标")
            agree6 = st.checkbox('OA', key='checkBoxPrecision0')
            agree7 = st.checkbox('Kappa', key='checkBoxPrecision1')
            interval_col1, interval_col2 = st.columns([5, 1])
            btn21 = interval_col1.button("下一步", on_click=onPrecision)
            if btn21:
                temp = []
                if agree6:
                    temp.append(agree6)
                if agree7:
                    temp.append(agree7)
                for index, row in pages_utils.TempDataSetField[4].iterrows():
                    pages_utils.TempDataSetField[4].loc[index, '精度指标'] = temp

    # Page 2
    elif st.session_state.page == 2:
        with ph.container():
            st.markdown("###### 验证与训练数据集划分")
            option = st.selectbox(
                label="划分比例",
                options=("8:2", "7:3", "6:4")
            )
            for index, row in pages_utils.TempDataSetField[4].iterrows():
                pages_utils.TempDataSetField[4].loc[index, '数据集划分'] = option
            interval_col1, interval_col2 = st.columns([5, 1])
            interval_col1.button("保存", on_click=firstPage)

            # btn11 = interval_col2.button("开始模型训练", on_click=onTrain)

    st.markdown('##### 任务清单')
    edited_df28 = st.data_editor(
        pages_utils.TempDataSetField[4], height=190, width=800,
        column_order=["编号", "模型", "模型参数", "时间"],
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
