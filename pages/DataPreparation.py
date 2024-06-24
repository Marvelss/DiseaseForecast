import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from PIL import Image

import pages_utils
from modelandmethod.PretreatmentMethod import PretreatmentMethod

# 处理方法内容记录(任务清单各项值)
if "preMethodName" not in st.session_state:
    st.session_state["preMethodName"] = {
        'checkBox': None
    }
if 'DPVisualInformation' not in st.session_state:
    st.session_state["DPVisualInformation"] = []
# 处理方法个数
checkBoxNum = 2
# 设置可视化图表中文
plt.rcParams['font.sans-serif'] = 'SimHei'

st.set_page_config(
    layout="wide"
)
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")


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
    elif checkbox == 'checkbox2':
        return '空间数据重采样'
    elif checkbox == 'checkbox3':
        return '点面数据转化'
    elif checkbox == 'checkbox4':
        return '点面数据关联'


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
    isHandledFlags = pages_utils.TempDataSetField[1]["处理状态"]
    methodList = pages_utils.TempDataSetField[1]["预处理方法"]
    # ===============根据名称匹配调用并执行各个处理方法===============
    # print('=========测试输入数据=========')
    # print(fields)
    # print(methodParam)

    # 若为空则跳过该步骤
    if idNumber.empty:
        pages_utils.TempDataSet[1] = pages_utils.TempDataSet[0]

    afterHandleData = None
    for indexT, (tempMethod, isHandled) in enumerate(zip(methodList, isHandledFlags)):
        # 检查方法是否已执行
        if isHandled:
            continue
        # 第一次使用原始数据集,而后基于预处理后数据集多次处理
        if pages_utils.TempDataSet[1].shape[0] == 0:
            dataFrameTemp = pages_utils.TempDataSet[0]
        else:
            dataFrameTemp = pages_utils.TempDataSet[1]
        # 使用处理后最新的字段内容
        reservedField = pages_utils.TempDataSet[0].columns.tolist()
        # print(f'=============测试保留字段-{reservedField}=============')
        newDataColumn = fields[indexT]

        DPVisualInformationTemp = {'before': dataFrameTemp[newDataColumn[0]]}
        if tempMethod == '缺失值插补':
            (afterHandleData, missingValueBefore, missingValueAfter,
             newDataColumn) = PretreatmentMethod(
                dataFrameTemp,
                fields[indexT], reservedField).linearInterpolation(methodParam[indexT])
            # 显示填补信息
            st.toast(f'填补缺失值:{str(missingValueBefore - missingValueAfter)}' +
                     '\n' +
                     f'剩余缺失值:{missingValueAfter}', icon='✅')
        elif tempMethod == '剔除异常值':
            (afterHandleData, outlierNum, lengthAfter,
             newDataColumn) = PretreatmentMethod(
                dataFrameTemp,
                fields[indexT], reservedField).outlierEliminator(methodParam[indexT])
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
        # print('======================预处理后数据集======================')

        # ===============更新左侧显示内容===============
        # print(f'更新左侧显示内容:{newDataColumn}')
        DPVisualInformationTemp['name'] = tempMethod
        DPVisualInformationTemp['after'] = pages_utils.TempDataSet[1][newDataColumn]
        # 可视化信息添加
        st.session_state["DPVisualInformation"].append(DPVisualInformationTemp)
        # print('=====================展示可视化内容======================')
        # print(st.session_state["DPVisualInformation"])
        update_values = {
            "预处理后字段": newDataColumn,
            "大小": '1*' + str(len(afterHandleData[fields[indexT]])),
            "时间": datetime.datetime.now().time(),
            "处理状态": True
        }
        # 查找要更新的数据记录
        for index, row in pages_utils.TempDataSetField[1].iterrows():
            if row["编号"] == idNumber[indexT]:
                for key1, value1 in update_values.items():
                    pages_utils.TempDataSetField[1].loc[index, key1] = value1
    print('===================预处理数据集===================')
    print(pages_utils.TempDataSet[1])

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
    weatherNameT, plantNameT, agricultureNameT = pages_utils.TempDataSet[0].columns.tolist(), ['无1'], ['无2']
    # 数组元素去重
    weatherName, plantName, agricultureName = list(set(weatherNameT)), list(set(plantNameT)), list(
        set(agricultureNameT))
    # 添加字段名称选项
    # weatherName, plantName, agricultureName = ['无1'], ['无2'], ['无3']
    # if tempDF[tempDF['数据类型'] == '气象数据']['字段'].any():
    #     weatherName.clear()
    #     weatherName = tempDF[tempDF['数据类型'] == '气象数据']['字段'].tolist()[0]
    # if tempDF[tempDF['数据类型'] == '植保数据']['字段'].any():
    #     plantName.clear()
    #     plantName = tempDF[tempDF['数据类型'] == '植保数据']['字段'].tolist()[0]
    # if tempDF[tempDF['数据类型'] == '农学数据']['字段'].any():
    #     agricultureName.clear()
    #     agricultureName = tempDF[tempDF['数据类型'] == '农学数据']['字段'].tolist()[0]
    # a = st.selectbox(
    #     '选择数据集',
    #     ('原始数据集', '预处理后数据集', '备选特征', '优选特征'))
    result1 = pages_utils.multiselect_all(
        st, '全选-字段', weatherName,
        'temp', 'collapsed')
    st.checkbox('全选-植保数据', disabled=True)
    st.checkbox('全选-农学数据', disabled=True)
    result2 = []
    result3 = []
    # result2 = pages_utils.multiselect_all(
    #     st, '全选-植保数据', plantName,
    #     'temp', 'collapsed')

    # result3 = pages_utils.multiselect_all(
    #     st, '全选-农学数据', agricultureName,
    #     'temp', 'collapsed')

# ===============显示右上预处理方法选项===============
with dataPCM:
    st.markdown("##### 预处理方法")
    # with tab1:
    col1, col2 = st.columns(2)

    with col1:
        agree = st.checkbox('剔除异常值', key='checkbox0', on_change=clear_other, args=[0])
        agree11 = st.checkbox("空间数据重采样(待发布)", key='checkbox2', on_change=clear_other, args=[2], disabled=True)
        agree12 = st.checkbox("点面数据转化(待发布)", key='checkbox3', on_change=clear_other, args=[3], disabled=True)
    with col2:
        agree10 = st.checkbox("缺失值插补", key='checkbox1', on_change=clear_other, args=[1])
        agree13 = st.checkbox("点面数据关联(待发布)", key='checkbox4', on_change=clear_other, args=[4], disabled=True)
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
                num = st.text_input('缺失值', value=np.nan)
                num1 = st.text_input('插补值')
                st.session_state["preMethodName"]['param2'] = num
                st.session_state["preMethodName"]['param3'] = num1
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
        # print('=======获取预处理方法=====')
        # print(getCheckboxName(st.session_state["preMethodName"]['checkBox']))
        new_data = {
            "编号": pages_utils.generateID(),
            "数据类型": '原始数据集',
            "输入字段": mergeArray(result1, result2, result3),
            "预处理后字段": None,
            "预处理方法": getCheckboxName(st.session_state["preMethodName"]['checkBox']),
            "方法参数": [value for key, value in st.session_state["preMethodName"].items() if key != 'checkBox'],
            "时间": datetime.datetime.now().time(), "处理状态": False}
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
            pages_utils.TempDataSetField[1] = st.data_editor(
                pages_utils.TempDataSetField[1], height=190, width=800,
                column_order=["编号", "数据类型", "输入字段", "预处理后字段", "预处理方法", '时间', '处理状态'],
                disabled=["数据类型", "输入字段", "预处理后字段", "时间", '处理状态'], num_rows="dynamic", )
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
            idPreMethods = pages_utils.TempDataSetField[1]["预处理方法"].tolist()
            inputFields = pages_utils.TempDataSetField[1]["输入字段"].tolist()
            # 若无方法处理,则直接跳过该环节
            if len(idPreMethods):
                # 创建新的从 1 开始的编号列表
                new_ids = list(range(0, len(idPreMethods)))

                # 创建标签页并重新命名记录
                new_ids = [f'记录编号_{h}' for h in new_ids]

                tt1 = st.tabs(new_ids)
                for o in range(len(idPreMethods)):
                    with tt1[o]:
                        # # 模拟气温和降水数据
                        # def simulate_weather_data():
                        #     np.random.seed(42)
                        #     date_range = pd.date_range(start='2024-01-01', end='2024-02-20')
                        #     temperature = np.random.normal(loc=15, scale=5, size=len(date_range))
                        #     precipitation = np.random.normal(loc=5, scale=2, size=len(date_range))
                        #     continuous_rain_days = np.random.randint(0, 10, size=len(date_range))
                        #
                        #     data = pd.DataFrame({
                        #         'Date': date_range,
                        #         '温度': temperature,
                        #         'Precipitation': precipitation,
                        #         '01-21_01-31_降雨日数': continuous_rain_days
                        #     })
                        #     return data
                        #
                        #
                        # # 生成累计降水量特征
                        # def generate_cumulative_precipitation_features(df):
                        #     df['01-21_01-31_累计降水量'] = df['Precipitation'].rolling(window=11, min_periods=1).sum()
                        #     df['01-01_01-20_累计降水量'] = df['Precipitation'].rolling(window=20, min_periods=1).sum()
                        #     df['02-01_02-20_累计降水量'] = df['Precipitation'].rolling(window=20, min_periods=1).sum()
                        #     return df
                        #
                        #
                        # # 模拟气温和降水数据
                        # df = simulate_weather_data()
                        # plt.rcParams['font.sans-serif'] = 'SimHei'
                        #
                        # # 生成累计降水量特征
                        # df = generate_cumulative_precipitation_features(df)
                        #
                        # # 随机生成目标变量
                        # df['Target'] = np.random.choice([0, 1], size=len(df))
                        #
                        # # 划分特征和目标
                        # X = df.drop(['Date', 'Precipitation', 'Target'], axis=1)
                        # y = df['Target']
                        #
                        # # 使用随机森林模型拟合数据
                        # rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
                        # rf_model.fit(X, y)
                        #
                        # # 获取特征重要性
                        # feature_importance = rf_model.feature_importances_
                        #
                        # # 创建特征重要性数据框
                        # feature_importance_df = pd.DataFrame(
                        #     {'Feature': X.columns,
                        #      'Importance': feature_importance})
                        #
                        # # 排序特征重要性
                        # feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
                        #
                        # # 创建子图和轴
                        # fig, ax = plt.subplots(figsize=(10, 6))
                        #
                        # # 使用Seaborn的barplot生成特征重要性图
                        # sns.barplot(x='Feature', y='Importance', data=feature_importance_df, ax=ax)
                        #
                        # # 设置图形标题和轴标签
                        # plt.title('基于Relief-F算法的各特征因子权值排序图', fontsize=16)
                        # plt.xlabel('')
                        # plt.ylabel('特征权值')
                        # plt.xticks(rotation=90)
                        # st.pyplot(plt)

                        # 移栽期
                        # # 创建DataFrame
                        # df = pd.read_excel(r'E:\a_python\program\diseaseForecastStreamlit\tests\test26\2024-05-22T11-04_export.xlsx')
                        #
                        # # 删除含有缺失值的行
                        # df = df.dropna()
                        #
                        # # 去除重复值
                        # df = df.drop_duplicates()
                        # plt.rcParams['font.sans-serif'] = 'SimHei'
                        #
                        # # 选择最多8个测报站点
                        # top_stations = df['测报站点'].value_counts().nlargest(8).index
                        # df_filtered_stations = df[df['测报站点'].isin(top_stations)]
                        #
                        # # 选择最多3个年份
                        # top_years = df['年'].value_counts().nlargest(3).index
                        # df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                        #
                        # # 绘制柱状图
                        # plt.figure(figsize=(12, 8))
                        # sns.lineplot(
                        #     data=df_filtered,
                        #     x="测报站点",
                        #     y="移栽期",
                        #     hue="年",
                        #     marker="o"
                        # )
                        # # 设置标签和标题
                        # plt.xlabel("测报站点")
                        # plt.ylabel("移栽期")
                        # plt.title("部分县市不同年份移栽期", fontsize=16)
                        #
                        # st.pyplot(plt)

                        # # 创建DataFrame
                        # df = pd.read_excel(
                        #     r'E:\a_python\program\diseaseForecastStreamlit\tests\test26\预测病害峰值-降水累积量.xlsx')
                        #
                        # # 删除含有缺失值的行
                        # df = df.dropna()
                        #
                        # # 去除重复值
                        # df = df.drop_duplicates()
                        # plt.rcParams['font.sans-serif'] = 'SimHei'
                        #
                        # # 选择最多8个测报站点
                        # top_stations = df['测报站点'].value_counts().nlargest(8).index
                        # df_filtered_stations = df[df['测报站点'].isin(top_stations)]
                        #
                        # # 选择最多5个年份
                        # top_years = df['年'].value_counts().nlargest(5).index
                        # df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                        #
                        # # 绘制柱状图
                        # plt.figure(figsize=(10, 6))
                        # sns.barplot(
                        #     data=df_filtered,
                        #     x="测报站点",
                        #     y="01-01_01-20_降水累积量",
                        #     hue="年",
                        #     dodge=True,
                        #     saturation=1
                        # )
                        # # 设置标签和标题
                        # plt.xlabel("测报站点")
                        # plt.ylabel("降水累积量")
                        # plt.title("部分县市不同年份01-01至01-20降水累积量")
                        # st.pyplot(plt)

                        if idPreMethods[o] == '缺失值插补':
                            data_before_temp = st.session_state["DPVisualInformation"][o]['before']
                            data_after_temp = st.session_state["DPVisualInformation"][o]['after']
                            # print(inputFields[o][0])
                            data_before = pd.DataFrame({inputFields[o][0]: data_before_temp})
                            data_after = pd.DataFrame({inputFields[o][0]: data_after_temp})
                            # 查找缺失值的索引
                            missing_indices = data_before[data_before[inputFields[o][0]].isna()].index

                            # 获取第一个缺失值的索引
                            first_missing_index = missing_indices[0]

                            # 计算前15行和后15行的起始和结束索引
                            start_index = max(first_missing_index - 15, 0)
                            end_index = min(first_missing_index + 15 + 1, len(data_before))

                            # 取第一个缺失值对应前15行和后15行预处理数据
                            data_before_surrounding_data = data_before.iloc[start_index:end_index]
                            data_after_surrounding_data = data_after.iloc[start_index:end_index]
                            # 绘制对比折线图
                            plt.figure(figsize=(10, 6))
                            # print(pages_utils.TempDataSet[1]['DayOfYear'])
                            # 取第一个缺失值对应前15行和后15行'上级单位', '测报站点', '年'数据
                            missing_rows = \
                                pages_utils.TempDataSet[1].loc[
                                    missing_indices, ['上级单位', '测报站点', '年', 'DayOfYear']].to_dict(
                                    'records')[0]
                            province, station, year = missing_rows['上级单位'], missing_rows['测报站点'], missing_rows[
                                '年']
                            print(missing_rows['DayOfYear'])
                            # 整理前后15天dayOfYear为x轴
                            figure_x = pd.DataFrame({'DayOfYear': pages_utils.TempDataSet[1]['DayOfYear']}).iloc[
                                       start_index:end_index]
                            # 绘制插补前的折线图
                            plt.plot(figure_x, data_before_surrounding_data[inputFields[o][0]],
                                     label='原始数据',
                                     color='black',
                                     linestyle='-', marker='o')

                            # 绘制插补后的折线图
                            plt.plot(figure_x, data_after_surrounding_data[inputFields[o][0]],
                                     label='插补后数据', color='blue',
                                     linestyle='--',
                                     marker='o', alpha=0.3)
                            plt.xlabel('Day of Year')
                            plt.ylabel(inputFields[o][0])
                            plt.title(f'{province}{station}{year}年部分{inputFields[o][0]}数据插补前后对比图',
                                      fontsize=16)
                            plt.legend()
                            st.pyplot(plt)
                        elif idPreMethods[o] == '剔除异常值':
                            # 剔除异常值-箱型图
                            data_before = st.session_state["DPVisualInformation"][o]['before']
                            data_after = st.session_state["DPVisualInformation"][o]['after']
                            # 创建两个子图
                            fig, axes = plt.subplots(1, 2, figsize=(12, 6))
                            # 绘制处理前的箱线图
                            sns.boxplot(y=data_before, ax=axes[0])
                            axes[0].set_ylabel(data_before.name)
                            axes[0].set_title('预处理后')
                            # axes[0].axhline(max_value, color='r', linestyle='--', linewidth=1, label=f'Max Value: {max_value}')
                            # axes[0].axhline(min_value, color='b', linestyle='--', linewidth=1, label=f'Min Value: {min_value}')
                            # axes[0].legend(loc='upper left')

                            # 绘制处理后的箱线图
                            sns.boxplot(y=data_after, ax=axes[1])
                            axes[1].set_ylabel(data_after.name)
                            axes[1].set_title('预处理后')
                            # axes[1].axhline(max_value, color='r', linestyle='--', linewidth=1, label=f'Max Value: {max_value}')
                            # axes[1].axhline(min_value, color='b', linestyle='--', linewidth=1, label=f'Min Value: {min_value}')
                            # axes[1].legend(loc='upper left')
                            # 设置主标题
                            fig.suptitle(f'{data_before.name}数据剔除前后对比箱型图',
                                         fontsize=16)
                            st.pyplot(fig)

            interval_col34, interval_col33 = st.columns([5, 1])
            # want_to_contribute = interval_col34.button("跳转至可视化界面")
            # if want_to_contribute:
            #     switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\Visualization.py")
            btn3 = interval_col33.button('返回', on_click=firstPage)
