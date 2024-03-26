import datetime
import os

from PIL import Image
import streamlit as st
import numpy as np
import pandas as pd
from streamlit import switch_page

import pages_utils

import seaborn as sns
import matplotlib.pyplot as plt

from modelandmethod.PretreatmentMethod import PretreatmentMethod

# 处理方法内容记录(任务清单各项值)
if "preMethodName" not in st.session_state:
    st.session_state["preMethodName"] = {
        'checkBox': None
    }
# 处理方法个数
checkBoxNum = 2

st.set_page_config(
    layout="wide"
)


# 模拟24小时气温数据
def simulate_temperature_data():
    now = datetime.datetime.now()
    hours = pd.date_range(start=now, periods=24, freq='H')
    temperatures = np.random.randint(10, 30, size=24)
    data1 = {'Time': hours, 'Temperature': temperatures}
    df = pd.DataFrame(data1)
    return df


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


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '剔除异常值'
    elif checkbox == 'checkbox1':
        return '缺失值插补'


def mergeArray(list1, list2, list3):
    return list(set().union(*[list1, list2, list3]))


def mergeArray4(list1, list2, list3, list4):
    return list(set().union(*[list1, list2, list3, list4]))


# 取消选中所有选项
def clearOption():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["preMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    return


# 取消选中外其他所有选项
def clear_other(key1):
    # st.markdown(key)
    for h in range(checkBoxNum):
        if h != key1:
            st.session_state[f'checkbox{h}'] = False
    return


# 控制左侧表格不同数据集显示
def firstPage(): st.session_state.page12 = 0


# 运行任务清单中所有方法
def onRun():
    if '预处理后数据集' not in st.session_state["leftTabs"]:
        st.session_state["leftTabs"].append('预处理后数据集')
    st.session_state.page12 += 1

    # ===============获取任务清单内容===============
    idNumber = pages_utils.TempDataSetField[1]["编号"]
    fields = pages_utils.TempDataSetField[1]["输入字段"]
    methodParam = pages_utils.TempDataSetField[1]["方法参数"]
    methodList = pages_utils.TempDataSetField[1]["预处理方法"]
    # ===============根据名称匹配调用并执行各个处理方法===============
    print('=========测试输入数据=========')
    print(fields)
    # print(fields[0])
    # print(fields[1])
    print(methodParam)
    print(type(pages_utils.TempDataSetField[1]["编号"]))

    afterHandleData = None
    for indexT, tempMethod in enumerate(methodList):
        reservedField = pages_utils.TempDataSet[0].columns.tolist()
        print(f'=============测试保留字段-{reservedField}=============')
        print(type(reservedField))
        # print(tempMethod)
        if tempMethod == '缺失值插补':
            afterHandleData, missingValueBefore, missingValueAfter = PretreatmentMethod(
                pages_utils.TempDataSet[0],
                fields[indexT], reservedField).linearInterpolation()
            # 显示填补信息
            st.toast(f'填补缺失值:{str(missingValueBefore - missingValueAfter)}' +
                     '\n' +
                     f'剩余缺失值:{missingValueAfter}', icon='✅')
        elif tempMethod == '剔除异常值':
            print(f'执行任务==={fields[indexT]}-{methodParam[indexT]}')
            afterHandleData, outlierNum, lengthAfter = PretreatmentMethod(
                pages_utils.TempDataSet[0],
                fields[indexT], reservedField).outlierEliminator(methodParam[indexT])
            print('========执行完后数据')
            print(len(afterHandleData[fields[indexT]]))
            # 显示填补信息
            st.toast(f'剔除异常值个数:{outlierNum}' +
                     '\n' +
                     f'剩余条数:{lengthAfter}', icon='✅')

        # ===============合并处理后数据集===============
        intersection_cols = pages_utils.getIntersectionCols(
            pages_utils.TempDataSet[1], afterHandleData
        )

        pages_utils.TempDataSet[1] = pd.merge(
            afterHandleData, pages_utils.TempDataSet[1],
            on=intersection_cols, how="left")
        print('======================预处理后数据集======================')

        # ===============更新左侧显示内容===============
        update_values = {
            "预处理后字段": fields[0],
            "大小": '1*' + str(len(afterHandleData[fields[indexT]])),
            "时间": datetime.datetime.now().time(),
        }
        # 查找要更新的数据记录
        for index, row in pages_utils.TempDataSetField[1].iterrows():
            if row["编号"] == idNumber[0]:
                for key1, value1 in update_values.items():
                    pages_utils.TempDataSetField[1].loc[index, key1] = value1

    # ======================保留字段======================
    print('======================保留字段======================')
    tempReserved = afterHandleData.columns
    pages_utils.TempDataSet[1] = pages_utils.TempDataSet[1][tempReserved]


# ==============================界面==============================
# 界面名称+布局+布局内容
# dataPreparation + column + variables
dataPCV, dataPCM = st.columns([0.5, 0.7])
with dataPCV:
    st.markdown("##### 数据与特征")
    # ===============显示左侧数据与特征表格===============
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
                        column = ["数据类型", "预处理后字段", "大小", "预处理方法", '时间']
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
                        # print('---{}---'.format(column))
                    st.data_editor(
                        pages_utils.TempDataSetField[i],
                        height=220, width=800,
                        column_order=column)

    # ===============显示左下字段或特征及获取===============
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
    # a = st.selectbox(
    #     '选择数据集',
    #     ('原始数据集', '预处理后数据集', '被选特征', '优选特征'))
    result1 = pages_utils.multiselect_all(
        st, '全选-气象数据', weatherName,
        'temp', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-植保数据', plantName,
        'temp', 'collapsed')
    result3 = pages_utils.multiselect_all(
        st, '全选-农学数据', agricultureName,
        'temp', 'collapsed')

# ===============显示右上预处理方法选项===============
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

    # ===============显示和处理右中各个处理方法设置参数===============
    if agree10:
        # 显示缺失值信息
        info = '缺失字段个数及占比:\n'
        flag = False
        # 统计缺失值信息
        for column in pages_utils.TempDataSet[0].columns:
            # 获取每个字段的非缺失值数量
            non_missing_values = pages_utils.TempDataSet[0][column].count()
            total_rows = len(pages_utils.TempDataSet[0])
            # 计算缺失值数量
            missing_values = total_rows - non_missing_values
            # 计算缺失值占比
            missing_percentage = (missing_values / total_rows) * 100
            # 将每个字段的缺失值占比保存到信息中
            if missing_values:
                info += f"* {column}:{missing_values} {missing_percentage:.2f}%\n"
                flag = True
        if not flag:
            info = '无缺失字段\n'
            st.info(f"{info}\n", icon="ℹ️️")
        else:
            st.warning(f"{info}\n", icon="⚠️")
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
            latext = '* 公式:' + r'''
            $$ 
            y = y_0 + (y_1 - y_0) \frac{(x - x_0)}{(x_1 - x_0)} 
            $$ 
            '''
            st.info('插补方法介绍\n'
                    '* 描述:使用缺失值前后最近的两个非缺失值填充\n' +
                    latext, icon="ℹ️")
            img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', 'Figure_5.png'))
            st.image(img)
        # st.markdown('---')
    if agree:
        coll11, coll22 = st.columns([0.3, 0.6])
        with coll11:
            number2 = st.text_input("剔除大于", value=0.1)
            number3 = st.text_input("剔除小于", value=0.1)
            st.session_state["preMethodName"]['param1'] = number2
            st.session_state["preMethodName"]['param2'] = number3
        with coll22:
            st.info('剔除方法介绍\n'
                    '* 描述:剔除最大值和最小值区域外的异常值\n', icon="ℹ️")
            img = Image.open(os.path.join(os.getcwd(), 'resource', 'image', '3.png'))
            st.image(img)

    # =======================添加处理至任务清单=======================
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clearOption)
    if btn:
        # update dataframe state
        print('=======获取预处理方法=====')
        print(getCheckboxName(st.session_state["preMethodName"]['checkBox']))
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": '原始数据集',
            "输入字段": mergeArray(result1, result2, result3),
            "预处理后字段": mergeArray(result1, result2, result3),
            "预处理方法": getCheckboxName(st.session_state["preMethodName"]['checkBox']),
            "方法参数": [value for key, value in st.session_state["preMethodName"].items() if key != 'checkBox'],
            "时间": datetime.datetime.now().time(), "已处理": False}
        print('======================预处理-添加任务清单记录======================')
        print(new_data)
        pages_utils.TempDataSetField[1].loc[len(pages_utils.TempDataSetField[1])] = new_data
        st.rerun()
    st.markdown('---')

    # =======================显示右下内容=======================
    placeholder = st.empty()
    if st.session_state.page12 == 0:
        # pages_utils.TempDataSet[1] = pages_utils.TempDataSet[0].copy()
        # # 初始化添加旬、月字段
        # pages_utils.TempDataSet[1]['MonthOfYear'] = pages_utils.TempDataSet[1]['DayOfYear'].apply(
        #     lambda x: (x - 1) // 30 + 1)  # 简化的月份计算，实际应用中可能需要更精确的方法
        # pages_utils.TempDataSet[1]['DecadeOfYear'] = pages_utils.TempDataSet[1]['DayOfYear'].apply(
        #     lambda x: (x - 1) // 10 + 1)  # 计算旬

        # =======================显示右下任务清单表格=======================
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
            with interval_col33:
                # residualField = [arr for arr in pages_utils.TempDataSet[0].columns if
                #                  arr not in mergeArray4(
                #                      ['上级单位', '测报站点',
                #                       "年", "DayOfYear"], result1, result2, result3)]
                # print(f'剩余字段{residualField}')
                # 默认保留上一环节所有字段
                # reservedFiled = pages_utils.multiselect_all(
                #     st, '全选',
                #     residualField,
                #     'temp1', 'collapsed')
                btn2 = st.button('运行', on_click=onRun)
            # btn2 = interval_col33.button('运行', on_click=onRun)

        # =======================显示右下可视化图表=======================
    elif st.session_state.page12 == 1:
        with placeholder.container():
            st.markdown('##### 可视化')
            plt.rc("font", family='Microsoft YaHei')
            tab1, tab2, tab3 = st.tabs(["1", "2", "3"])
            with tab1:
                # 模拟降水数据
                precipitation_data = simulate_precipitation_data()
                # 绘制最高温度和最低温度的折线图
                plt.figure(figsize=(10, 5))
                sns.lineplot(data=precipitation_data, x="Time", y="Precipitation", label="降水量")
                plt.xlabel('日期')
                plt.ylabel('降水量(mm)')
                plt.title('预处理后降水量')
                plt.legend()
                st.pyplot(plt)
                # 模拟气温数据

            with tab2:
                pass
                # temperature_data = simulate_temperature_data()
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
            want_to_contribute = interval_col34.button("跳转至可视化界面")
            if want_to_contribute:
                switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\Visualization.py")
            btn3 = interval_col33.button('返回', on_click=firstPage)
