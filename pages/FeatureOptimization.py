import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

import pages_utils
import seaborn as sns
import matplotlib.pyplot as plt

if 'page14' not in st.session_state: st.session_state.page14 = 0
if 'df13' not in st.session_state:
    st.session_state.df13 = pages_utils.FeatureDataSet

checkBoxNum = 3


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
    df = pd.DataFrame(data)
    return df


def simulate_temperature_data():
    # 模拟生成温度数据
    np.random.seed(15)
    N = 15

    temperature1 = np.random.normal(loc=20, scale=2, size=(N,))
    temperature2 = np.random.normal(loc=25, scale=4, size=(N,))
    temperature3 = np.random.normal(loc=18, scale=1.5, size=(N,))
    temperature4 = np.random.normal(loc=22, scale=3, size=(N,))

    # 创建DataFrame
    df = pd.DataFrame({
        'Temperature1': temperature1,
        'Temperature2': temperature2,
        'Temperature3': temperature3,
        'Temperature4': temperature4,
        'Target': np.random.choice([0, 1], size=N)  # 二分类目标
    })
    return df


def clear_all():
    for i in range(checkBoxNum):
        st.session_state[f'checkbox{i}'] = False
    return


def clear_other(key):
    for i in range(checkBoxNum):
        if i != key:
            st.session_state[f'checkbox{i}'] = False
    return


def firstPage(): st.session_state.page14 = 0


def nextPage():
    if '优选特征' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('优选特征')
    st.session_state.page14 += 1
    data11 = {"选择特征": False, "数据集": "气象数据", "特征": "温度",
              "大小": '1*3', "处理方法": "t检验", "时间": '22:10:20',
              "下载数据集": True}
    data12 = {"选择特征": False, "数据集": "气象数据", "特征": "降水累积量",
              "大小": '1*5', "处理方法": "Person相关性分析", "时间": '22:10:21',
              "下载数据集": True}
    st.session_state.df13.loc[len(st.session_state.df13)] = data11
    st.session_state.df13.loc[len(st.session_state.df13)] = data12


# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    # 根据st.session_state.page12的值刷新表格
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        # st.markdown(st.session_state.page12)
        with placeholder1.container():
            tt1 = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt1[i]:
                    st.data_editor(
                        pages_utils.TempDataSet[i],
                        height=220, width=800,
                        column_config={
                            "选择字段": st.column_config.CheckboxColumn(
                                help="选择用于数据处理的字段",
                                default=False,
                            )
                        })

    if st.session_state.page12 == 1:
        with placeholder1.container():
            tt = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt[i]:
                    st.data_editor(
                        pages_utils.TempDataSet[i],
                        height=220, width=800,
                        column_config={
                            "选择字段": st.column_config.CheckboxColumn(
                                help="选择用于数据处理的字段",
                                default=False,
                            )
                        })
    a = st.selectbox(
        '选择数据集',
        ('原始数据集', '预处理后数据集', '备选特征'))
    result1 = pages_utils.multiselect_all(
        st, '全选-气象数据', ['温度', '降水'],
        'temp', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-植保数据', ['植保', '植保2'],
        'temp', 'collapsed')
    result3 = pages_utils.multiselect_all(
        st, '全选-农学数据', ['分支', '降水'],
        'temp', 'collapsed')
with dataPCM:
    tab1, tab2 = st.tabs(["单因子敏感性分析", "多因子组合优化"])
    with tab1:
        genre = st.checkbox("Person相关性分析", key='checkbox0', on_change=clear_other, args=[0])
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
    # st.markdown('---')
    if genre3:
        # st.markdown('提取条件')
        option = st.selectbox(
            '提取条件',
            ('按百分比选取', '按权重值计算'))
        if option == '按百分比选取':
            number1 = st.number_input("TOP(%)", value=5, min_value=5, step=5)
        if option == '按权重值计算':
            number2 = st.number_input("权重阈值", value=10, min_value=10)
        # st.markdown('---')

    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clear_all)
    if btn:
        # update dataframe state
        # st.markdown(type(st.session_state.df))
        new_data = {"数据集": "气象数据", "输入特征": "温度",
                    "输出特征": "温度",
                    "特征优选方法": "t检验", "时间": '22:20:20'}
        st.session_state.df1.loc[len(st.session_state.df1)] = new_data
        st.rerun()
    st.markdown('---')
    data = pd.DataFrame(columns=["数据集", "输入特征", "输出特征", "特征优选方法", '时间'])

    if 'df1' not in st.session_state:
        st.session_state.df1 = data
    placeholder = st.empty()
    if st.session_state.page14 == 0:
        with placeholder.container():
            st.markdown('##### 任务清单')
            edited_df28 = st.data_editor(
                st.session_state.df1, height=190, width=800,
                disabled=["数据集", "字段", "时间"],
                num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])
            btn2 = interval_col33.button('运行', on_click=nextPage)
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
