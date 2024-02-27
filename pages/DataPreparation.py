import datetime
import os

from PIL import Image
import streamlit as st
import numpy as np
import pandas as pd

import pages_utils

import seaborn as sns
import matplotlib.pyplot as plt

if 'page12' not in st.session_state:
    st.session_state.page12 = 0
if "leftTabs" not in st.session_state:
    st.session_state["leftTabs"] = ['原始数据']

# 处理方法内容记录(任务清单各项值)
if "preMethodName" not in st.session_state:
    st.session_state["preMethodName"] = {
        'checkBox': None
    }

checkBoxNum = 2

st.set_page_config(
    layout="wide"
)


# 线性插补
def linearInterpolation(dataFrame, fieldName):
    # dataFrame[fieldName].interpolate(inplace=True)
    dataFrame[fieldName] = dataFrame[fieldName].interpolate()
    # 单独计算插补所用的均值
    # mean_value = dataFrame[fieldName].mean()
    # print(f"均值为: {mean_value}")
    # dataFrame[fieldName].fillna(mean_value, inplace=True)

    # 检查是否还有缺失值
    # missing_values = dataFrame[fieldName].isnull().sum()
    # print(f"字段中的缺失值数量为: {missing_values}")
    # print(dataFrame[fieldName])
    # 返回三列值
    # print('-------三列值---')
    tempData = dataFrame[['上级单位', '测报站点', "年", "DayOfYear",
                          fieldName, '预测病株率']]
    return tempData


def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '剔除异常值'
    elif checkbox == 'checkbox1':
        return '缺失值插补'


def mergeArray(list1, list2, list3):
    return list(set().union(*[list1, list2, list3]))


# 模拟24小时气温数据
def simulate_temperature_data():
    now = datetime.datetime.now()
    hours = pd.date_range(start=now, periods=24, freq='H')
    temperatures = np.random.randint(10, 30, size=24)
    data1 = {'Time': hours, 'Temperature': temperatures}
    df = pd.DataFrame(data1)
    return df


def clearOption():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["preMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    return


def clear_other(key1):
    # st.markdown(key)
    for h in range(checkBoxNum):
        if h != key1:
            st.session_state[f'checkbox{h}'] = False
    return


# 模拟24小时降水数据
def simulate_precipitation_data():
    now = datetime.datetime.now()
    hours = pd.date_range(start=now, periods=24, freq='H')
    precipitation = np.random.uniform(0, 10, size=24)
    data1 = {'Time': hours, 'Precipitation': precipitation}
    df = pd.DataFrame(data1)
    return df


def simulate_box_data():
    # 模拟生成温度数据
    N = 500
    temperature1 = np.random.normal(loc=20, scale=2, size=(N,))
    temperature2 = np.random.normal(loc=25, scale=4, size=(N,))
    temperature3 = np.random.normal(loc=18, scale=1.5, size=(N,))
    temperature4 = np.random.normal(loc=22, scale=3, size=(N,))

    # 创建DataFrame
    df1 = pd.DataFrame(temperature1, columns=['Temperature'])
    df1['day'] = 'Thur'
    df2 = pd.DataFrame(temperature2, columns=['Temperature'])
    df2['day'] = 'Fri'
    df3 = pd.DataFrame(temperature3, columns=['Temperature'])
    df3['day'] = 'Sat'
    df4 = pd.DataFrame(temperature4, columns=['Temperature'])
    df4['day'] = 'Sun'

    # 合并数据
    df = pd.concat([df1, df2, df3, df4], axis=0)
    return df


def firstPage(): st.session_state.page12 = 0


def onRun():
    if '预处理后数据集' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('预处理后数据集')
    st.session_state.page12 += 1

    # 调用数据和各类方法
    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[1]["编号"].tolist()
    fields = pages_utils.TempDataSetField[1]["输入字段"].tolist()
    # print('===============')
    # ===============根据名称匹配调用并执行各个处理方法===============
    afterHandleData = linearInterpolation(
        pages_utils.TempDataSet[0], fields[0][0])
    # 获取处理后的数据大小
    row_size = len(afterHandleData)

    intersection_cols = pages_utils.getIntersectionCols(
        pages_utils.TempDataSet[1], afterHandleData
    )
    pages_utils.TempDataSet[1] = pd.merge(
        afterHandleData, pages_utils.TempDataSet[1],
        on=intersection_cols, how="left")
    print('======================预处理后数据集======================')
    print(pages_utils.TempDataSet[1])

    # 更新记录
    update_values = {
        "数据类型": "气象数据",
        "输入字段": fields[0],
        "预处理后字段": fields[0],
        "大小": '1*' + str(row_size),
        "预处理方法": getCheckboxName(st.session_state["preMethodName"]['checkBox']),
        "时间": datetime.datetime.now().time(),
    }
    # 查找要更新的数据记录
    for index, row in pages_utils.TempDataSetField[1].iterrows():
        if row["编号"] == idNumber[0]:
            for key1, value1 in update_values.items():
                pages_utils.TempDataSetField[1].loc[index, key1] = value1
                # 根据字段名和索引来更新字段值


# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    # st.data_editor(pages_utils.TempDataSet[0])
    # st.markdown(pages_utils.TempDataSet[1])
    # st.markdown(pages_utils.TempDataSet[2])
    # st.markdown(pages_utils.TempDataSet[3])
    # 根据st.session_state.page12的值刷新表格
    placeholder1 = st.empty()
    if st.session_state.page12 == 0:
        with placeholder1.container():
            tt1 = st.tabs(st.session_state["leftTabs"])
            for i in range(len(st.session_state["leftTabs"])):
                with tt1[i]:
                    if st.session_state["leftTabs"][i] == '原始数据':
                        column = ['数据类型', '字段', '上传时间']
                    elif st.session_state["leftTabs"][i] == '预处理后数据集':
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间', "下载数据集"]
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
                        # print('---{}---'.format(column))
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)
    # 原始数据集表信息

    tempDF = pages_utils.TempDataSetField[0]
    # 添加字段名称选项
    weatherName, plantName, agricultureName = ['无1'], ['无2'], ['无3']
    if tempDF[tempDF['数据类型'] == '气象数据']['字段'].any():
        weatherName.clear()
        weatherName = tempDF[tempDF['数据类型'] == '气象数据']['字段'].tolist()[0]
    if tempDF[tempDF['数据类型'] == '植保数据']['字段'].any():
        plantName.clear()
        plantName = tempDF[tempDF['数据类型'] == '植保数据']['字段'].tolist()[0]
    if tempDF[tempDF['数据类型'] == '农学数据']['字段'].any():
        agricultureName.clear()
        agricultureName = tempDF[tempDF['数据类型'] == '农学数据']['字段'].tolist()[0]
    a = st.selectbox(
        '选择数据集',
        ('原始数据集', '预处理后数据集', '被选特征', '优选特征'))
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
    st.markdown("##### 预处理方法")
    # with tab1:
    col1, col2 = st.columns(2)

    with col1:
        agree = st.checkbox('剔除异常值', key='checkbox0', on_change=clear_other, args=[0])
        # agree5 = st.checkbox('剔除数据5')
    with col2:
        agree10 = st.checkbox("缺失值插补", key='checkbox1', on_change=clear_other, args=[1])
    st.markdown('---')
    # st.markdown("##### 方法参数设置")
    if agree10:
        # 显示缺失值信息
        info = '缺失字段及个数:\n'
        flag = False
        # 统计缺失值信息
        for column in pages_utils.TempDataSet[0].columns:
            # 获取每个字段的缺失值数量
            missing_values = pages_utils.TempDataSet[0][column].isnull().sum()
            # 将每个字段的缺失值数量保存到字典中
            if missing_values:
                info += f"* {column}:{missing_values}\n"
                flag = True
        if not flag:
            info = '无缺失字段\n'
        st.info(f"{info}\n", icon="ℹ️")

        coll11, coll22 = st.columns([0.3, 0.6])
        with coll11:
            option = st.selectbox(
                '插补方法',
                options=('线性插值', '自定义'))
            st.session_state["preMethodName"]['param1'] = option
            if option == '自定义':
                num = st.text_input('输入数值')
                st.session_state["preMethodName"]['param2'] = num
        with coll22:
            img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '0.png'))
            # st.image(img)
            latext = '* 公式:' + r'''
            $$ 
            y = y_0 + (y_1 - y_0) \frac{(x - x_0)}{(x_1 - x_0)} 
            $$ 
            '''
            st.info('插补方法介绍\n'
                    '* 描述:使用缺失值前后最近的两个非缺失值填充\n' +
                    latext, icon="ℹ️")
        # st.markdown('---')
    if agree:
        coll11, coll22 = st.columns([0.3, 0.6])
        with coll11:
            number2 = st.text_input("剔除大于", value=0.1)
            number3 = st.text_input("剔除小于", value=0.1)
        with coll22:
            st.info('剔除方法介绍\n'
                    '* 描述:剔除最大值和最小值区域外的异常值\n', icon="ℹ️")
            img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '3.png'))
            st.image(img)

    # 获取添加处理按钮各项值
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clearOption)
    # =======================执行任务清单=======================
    if btn:
        for key11, value11 in st.session_state["preMethodName"].items():
            pass
            # print(f"Key: {key11}, Value: {value11}")
        # print('--------------')
        # update dataframe state
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": a,
            "输入字段": mergeArray(result1, result2, result3),
            "预处理后字段": mergeArray(result1, result2, result3),
            "预处理方法": getCheckboxName(st.session_state["preMethodName"]['checkBox']),
            "方法参数": [value for key, value in st.session_state["preMethodName"].items() if key != 'checkBox'],
            "时间": datetime.datetime.now().time(), "下载数据集": False}
        print('======================预处理-添加任务清单记录======================')
        print(new_data)
        pages_utils.TempDataSetField[1].loc[len(pages_utils.TempDataSetField[1])] = new_data
        st.rerun()
    st.markdown('---')
    # with every interaction, the script runs from top to bottom
    # resulting in the empty dataframe

    placeholder = st.empty()
    if st.session_state.page12 == 0:
        with placeholder.container():
            st.markdown('##### 任务清单')
            # want_to_contribute = st.button("跳转可视化")
            # if want_to_contribute:
            #     switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\ModelEvaluation.py")
            edited_df28 = st.data_editor(
                pages_utils.TempDataSetField[1], height=190, width=800,
                column_order=["编号", "数据类型", "输入字段", "预处理后字段", "预处理方法", '时间'],
                disabled=["数据类型", "输入字段", "预处理后字段", "时间"], num_rows="dynamic", )
            interval_col34, interval_col33 = st.columns([5, 1])
            btn2 = interval_col33.button('运行', on_click=onRun)

    elif st.session_state.page12 == 1:
        with placeholder.container():
            st.markdown('##### 可视化')
            tab1, tab2, tab3 = st.tabs(["1", "2", "3"])
            with tab1:
                # 模拟气温数据
                temperature_data = simulate_temperature_data()
                st.line_chart(temperature_data.set_index('Time'))
            with tab2:
                # 模拟降水数据
                precipitation_data = simulate_precipitation_data()
                fig, ax = plt.subplots()
                sns.lineplot(data=precipitation_data)
                ax.set_xlabel('Time(hours)')
                ax.set_ylabel('Precipitation')
                st.pyplot(fig)
            with tab3:
                df111 = simulate_box_data()
                # 绘制箱型图
                fig, ax = plt.subplots()
                sns.boxplot(x='day', y='Temperature', data=df111,
                            linewidth=2,
                            width=0.8,
                            fliersize=3,
                            # palette='hls',
                            whis=1.5,
                            notch=True,
                            order=['Thur', 'Fri', 'Sat', 'Sun']
                            )
                ax.set_xlabel('Day')
                ax.set_ylabel('Temperature')
                plt.figure(figsize=(10, 6))
                # sns.(x='', y='', data=df, palette='Set3')
                plt.title('Boxplot of Temperature for Different Days')
                st.pyplot(fig)
            interval_col34, interval_col33 = st.columns([5, 1])
            btn3 = interval_col33.button('返回', on_click=firstPage)
