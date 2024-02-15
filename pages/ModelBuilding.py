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

if 'page' not in st.session_state: st.session_state.page = 0
if 'page15' not in st.session_state: st.session_state.page15 = 0
if 'df15' not in st.session_state:
    st.session_state.df15 = pages_utils.ModelSet


def onTrain():
    if '模型' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('模型')
    st.session_state.page = 0
    st.session_state.page15 += 1
    # 训练模型
    df11 = pages_utils.TempDataSet[3]
    # 提取特征和目标变量
    X = df11[['上级单位', '测报站点', "年", "DayOfYear", '降水累积量', '降水']]
    Y = df11['峰值率']

    # 对分类变量进行one-hot编码
    X = pd.get_dummies(X, columns=['上级单位', '测报站点'])

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

    # 训练模型
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 预测
    y_pred = model.predict(X_test)

    # 计算均方误差
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    st.markdown('---')
    st.markdown(y_test)
    st.markdown(y_pred)
    st.markdown(mse)
    st.markdown(r2)
    # print("均方误差:", mse)
    data11 = {"模型": "SVM", "时间": datetime.datetime.now().time(),
              "下载模型结构、结果和参数值": False}
    st.session_state.df15.loc[len(st.session_state.df15)] = data11


def nextPage(): st.session_state.page += 1


def firstPage(): st.session_state.page = 0


modelACV, modelACM = st.columns([0.5, 0.7])
with modelACV:
    st.markdown("##### 特征与模型")
    st.data_editor(pages_utils.TempDataSet[0])
    st.markdown(pages_utils.TempDataSet[1])
    st.markdown(pages_utils.TempDataSet[2])
    st.markdown(pages_utils.TempDataSet[3])
    # 根据st.session_state.page12的值刷新表格
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        # st.markdown(st.session_state.page12)
        with placeholder1.container():
            tt1 = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt1[i]:
                    if st.session_state["leftTabs"][i] == '原始数据':
                        column = ['数据类型', '字段', '上传时间']
                    else:
                        column = pages_utils.TempDataSetField[i].columns
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
                    else:
                        column = pages_utils.TempDataSetField[i].columns
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)
    # 预处理后数据集表信息
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
                agree = st.checkbox('SVM')
                agree1 = st.checkbox('RF')
            with colOption2:
                agree2 = st.checkbox('KNN')

            with colOption3:
                agree3 = st.checkbox('FLDA')
                # agree4 = st.checkbox('贝叶斯统计')
                # agree5 = st.checkbox('模糊综合评价')
            st.markdown('---')
            if agree:
                df = pd.DataFrame(
                    [
                        {"参数名": "a", "参数值": 4},
                        {"参数名": "b", "参数值": 4},
                        {"参数名": "c", "参数值": 6},
                        {"参数名": "d", "参数值": 5},
                    ]
                )
                st.data_editor(df)
                st.markdown('---')
            interval_col1, interval_col2 = st.columns([4, 1])
            interval_col2.button("下一步", on_click=nextPage)

    # Page 1
    elif st.session_state.page == 1:
        with ph.container():
            st.markdown("###### 评价指标")
            agree6 = st.checkbox('OA')
            agree7 = st.checkbox('Kappa')
            interval_col1, interval_col2 = st.columns([4, 1])
            interval_col2.button("下一步", on_click=nextPage)

    # Page 2
    elif st.session_state.page == 2:
        with ph.container():
            st.markdown("###### 验证与训练数据集划分")
            option = st.selectbox(
                label="划分比例",
                options=("8:2", "7:3", "6:4")
            )
            interval_col1, interval_col2 = st.columns([5, 2])
            interval_col1.button("返回", on_click=firstPage)
            btn11 = interval_col2.button("开始模型训练", on_click=onTrain)
    placeholder1 = st.empty()
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
