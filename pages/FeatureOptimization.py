import datetime

import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

import pages_utils
import seaborn as sns
import matplotlib.pyplot as plt

from modelandmethod.FeatureOptimizationMethod import FeatureOptimizationMethod

if 'page14' not in st.session_state:
    st.session_state.page14 = 0

checkBoxNum = 3
if "OptimizationMethodName" not in st.session_state:
    st.session_state["OptimizationMethodName"] = {
        'checkBox': None
    }
st.set_page_config(
    layout="wide"
)


def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return 'Person相关性分析'
    elif checkbox == 'checkbox1':
        return 't检验'
    elif checkbox == 'checkbox2':
        return 'Relief-F互相关分析'


def mergeArray(list1, list2, list3):
    return list(set().union(*[list1, list2, list3]))


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


def clear_all():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["OptimizationMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    return


def clear_other(key):
    for h in range(checkBoxNum):
        if h != key:
            st.session_state[f'checkbox{h}'] = False
    return


def firstPage(): st.session_state.page14 = 0


def onRun():
    if '优选特征' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('优选特征')
    st.session_state.page14 += 1

    # 调用数据和各类方法
    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[3]["编号"].tolist()
    fields = pages_utils.TempDataSetField[3]["输入特征"].tolist()
    methodParam = pages_utils.TempDataSetField[3]["方法参数"].tolist()
    methodList = pages_utils.TempDataSetField[3]["特征优选方法"].tolist()
    # ===============根据名称匹配调用并执行各个处理方法===============
    for tempMethod in methodList:
        afterHandleData = None
        # print(tempMethod)
        if tempMethod == 't检验':
            afterHandleData = FeatureOptimizationMethod(
                pages_utils.TempDataSet[2],
                fields[0]).tTest(methodParam)
        elif tempMethod == 'Person相关性分析':
            pass
        elif tempMethod == 'Relief-F互相关分析':
            afterHandleData = FeatureOptimizationMethod(
                pages_utils.TempDataSet[2],
                fields[0]).ReliefF(methodParam)

        row_size = len(afterHandleData)
        # print('-------优选特征-------')
        intersection_cols = pages_utils.getIntersectionCols(
            pages_utils.TempDataSet[3], afterHandleData
        )
        pages_utils.TempDataSet[3] = pd.merge(
            afterHandleData, pages_utils.TempDataSet[3],
            on=intersection_cols, how="left")

        print('======================优选特征======================')
        print(pages_utils.TempDataSet[3])
        # 更新记录
        update_values = {
            # "数据类型": "气象数据", "输入特征": fields[0],
            # "优选特征": fields[0],
            "大小": '1*' + str(row_size),
            # "特征计算方法": st.session_state["OptimizationMethodName"]['checkBox'],
            "时间": datetime.datetime.now().time()}
        # 查找要更新的数据记录
        for index, row in pages_utils.TempDataSetField[3].iterrows():
            if row["编号"] == idNumber[0]:
                for key, value in update_values.items():
                    pages_utils.TempDataSetField[3].loc[index, key] = value


# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    # st.data_editor(pages_utils.TempDataSet[0])
    # st.markdown(pages_utils.TempDataSet[1])
    # st.markdown(pages_utils.TempDataSet[2])
    # st.markdown(pages_utils.TempDataSet[3])
    # =======================左侧数据与特征显示=======================
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
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '被选特征':
                        column = ["数据类型", "被选特征", "大小", "特征计算方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '优选特征':
                        column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间', "下载数据集"]
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
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '被选特征':
                        column = ["数据类型", "被选特征", "大小", "特征计算方法", '时间', "下载数据集"]
                    elif st.session_state["leftTabs"][i] == '优选特征':
                        column = ["数据类型", "优选特征", "大小", "特征优选方法", '时间', "下载数据集"]
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)
    # =======================获取特征数据集表信息=======================
    # =======================选择数据集=======================
    # a = st.selectbox(
    #     '选择数据集',
    #     ('原始数据集', '预处理后数据集', '被选特征', '优选特征'))
    # 预处理后数据集表信息
    weatherNameT, plantNameT, agricultureNameT = pages_utils.getDataFiled()
    # 数组元素去重
    weatherName, plantName, agricultureName = list(set(weatherNameT)), list(set(plantNameT)), list(
        set(agricultureNameT))
    result1 = pages_utils.multiselect_all(
        st, '全选-气象数据', weatherName,
        'temp', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-植保数据', plantName,
        'temp', 'collapsed')
    result3 = pages_utils.multiselect_all(
        st, '全选-农学数据', agricultureName,
        'temp', 'collapsed')
with dataPCM:
    tab1, tab2 = st.tabs(["单因子敏感性分析", "多因子组合优化"])
    with tab1:
        genre = st.checkbox("Person相关性分析", key='checkbox0', on_change=clear_other, args=[0], disabled=True)
        genre1 = st.checkbox("t检验", key='checkbox1', on_change=clear_other, args=[1])

    with tab2:
        genre3 = st.checkbox("Relief-F互相关分析", key='checkbox2', on_change=clear_other, args=[2])
    st.markdown('---')
    # st.markdown("##### 方法参数设置")
    if genre:
        st.markdown('提取条件')
        genre2 = st.radio(
            label='',
            horizontal=True,
            label_visibility="collapsed",
            options=['p-value<0.001', 'p-value<0.005', 'p-value<0.01']
        )
    if genre1:
        st.markdown('提取条件')
        genre2 = st.radio(
            label='',
            horizontal=True,
            label_visibility="collapsed",
            options=['p-value<0.001', 'p-value<0.005', 'p-value<0.01']
        )
        st.session_state["OptimizationMethodName"]['param1'] = genre2
    # st.markdown('---')
    if genre3:
        # st.markdown('提取条件')
        option111 = st.selectbox(
            '目标变量',
            mergeArray(result1, result2, result3))
        option = st.selectbox(
            '提取条件',
            ('按百分比选取', '按权重值计算'))
        if option == '按百分比选取':
            st.session_state["OptimizationMethodName"]['param1'] = option
            number1 = st.number_input("TOP(%)", value=5, min_value=5, step=5)
            st.session_state["OptimizationMethodName"]['param2'] = str(number1)
        if option == '按权重值计算':
            st.session_state["OptimizationMethodName"]['param1'] = option
            number2 = st.number_input("权重阈值", value=10, min_value=10)
            st.session_state["OptimizationMethodName"]['param2'] = str(number2)

        st.session_state["OptimizationMethodName"]['param3'] = option111
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clear_all)
    # =======================执行任务清单=======================
    if btn:
        for key11, value11 in st.session_state["OptimizationMethodName"].items():
            pass
            # print(f"Key: {key11}, Value: {value11}")
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": '气象数据',
            "输入特征": mergeArray(result1, result2, result3),
            "优选特征": '降水',
            "特征优选方法": getCheckboxName(st.session_state["OptimizationMethodName"]['checkBox']),
            "方法参数":
                [value for key, value in st.session_state["OptimizationMethodName"].items() if key != 'checkBox'],
            "时间": datetime.datetime.now().time(),
            "下载数据集": False}
        print('======================特征优选-添加任务清单记录======================')
        print(new_data)
        pages_utils.TempDataSetField[3].loc[len(pages_utils.TempDataSetField[3])] = new_data
        st.rerun()
    st.markdown('---')

    # =======================显示任务清单=======================
    placeholder = st.empty()
    if st.session_state.page14 == 0:
        with placeholder.container():
            st.markdown('##### 任务清单')
            edited_df28 = st.data_editor(
                pages_utils.TempDataSetField[3], height=190, width=800,
                column_order=["编号", "数据类型", "输入特征", "优选特征", "特征优选方法", '时间'],
                disabled=["数据类型", "时间"], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])
            btn2 = interval_col33.button('运行', on_click=onRun)
    elif st.session_state.page14 == 1:
        with placeholder.container():
            st.markdown('##### 可视化')
            tab1, tab2 = st.tabs(["1", "2"])
            with tab1:
                # 模拟气温数据
                df1 = simulate_temperature_data1()
                # 划分特征和目标
                X = df1.drop('Target', axis=1)
                y = df1['Target']

                # 使用随机森林模型拟合数据
                rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
                rf_model.fit(X, y)

                # 获取特征重要性
                feature_importance = rf_model.feature_importances_

                # 创建特征重要性数据框
                feature_importance_df = pd.DataFrame(
                    {'Feature': ['temperature', 'precipitation', 'Continuous Rain Days'],
                     'Importance': feature_importance})

                # 排序特征重要性
                feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

                # 创建子图和轴
                fig, ax = plt.subplots()

                # 使用Seaborn的barplot生成特征重要性图
                sns.barplot(x='Importance', y='Feature', data=feature_importance_df, ax=ax)

                # 设置图形标题
                plt.title('Feature Importance Plot')
                st.pyplot(fig)
            with tab2:
                df = simulate_temperature_data()
                fig, ax = plt.subplots()
                sns.scatterplot(x='Temperature1', y='Temperature2', hue='Target', data=df)
                plt.title('Scatter Plot of Selected Features')
                st.pyplot(fig)
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('返回', on_click=firstPage)
