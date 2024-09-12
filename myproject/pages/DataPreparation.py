import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from PIL import Image
from st_pages import hide_pages

from lib.share import RESOURCE_IMAGES_PATH
from lib.utils import mergeExcludeArray, filterUnique
from pages import pages_utils
from pages.modelandmethod.PretreatmentMethod import PretreatmentMethod

st.set_page_config(
    layout="wide"
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")

# 隐藏页面
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
emptyHeadDPP = st.empty()


# 检测用户输入行为
def detectUserInput():
    # 1.添加处理
    # 1.1输入特征（空）
    # 1.2参数（空）
    # 1.3方法(空或对应方法无法处理)
    print()


# 获取选项值对应名称
def getCheckboxName(checkbox):
    if checkbox == 'checkbox0':
        return '剔除异常值'
    elif checkbox == 'checkbox1':
        return '缺失值插补'


# 取消选中所有选项
def clearOption():
    for h in range(checkBoxNum):
        if st.session_state[f'checkbox{h}']:
            st.session_state["preMethodName"]['checkBox'] = f'checkbox{h}'
        st.session_state[f'checkbox{h}'] = False
    # 若已经在可视化展示状,则默认返回任务清单
    st.session_state.page12 = 0
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
    with emptyHeadDPP:
        with st.spinner('处理数据中...'):
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

                try:
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

                except BaseException as e:
                    st.toast(f'{tempMethod}运行失败  \n错误:{e}', icon="⚠️")
                    # 不自动跳转至可视化
                    st.session_state.page12 = 0
                    # 删除最后一条记录
                    pages_utils.TempDataSetField[1] = pages_utils.TempDataSetField[1].drop(
                        pages_utils.TempDataSetField[1].index[-1])
                # 若执行正确则合并数据
                else:
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
    # weatherNameList, plantNameList, agricultureNameList = ['无1'], ['无2'], ['无3']
    # if not pages_utils.TempDataSetField[0].empty:
    weatherNameT1, plantNameT1, agricultureNameT1 = pages_utils.getDataFiled(0, pages_utils.TempDataSetField[0])
    # weatherNameList = weatherNameT1
    # plantNameList = plantNameT1
    # agricultureNameList = agricultureNameT1
    # if not pages_utils.TempDataSetField[1].empty:
    weatherNameT2, plantNameT2, agricultureNameT2 = pages_utils.getDataFiled(1, pages_utils.TempDataSetField[1])
    weatherNameList = weatherNameT1 + weatherNameT2
    plantNameList = plantNameT1 + plantNameT2
    agricultureNameList = agricultureNameT1 + agricultureNameT2
    # 按照数据类型显示左侧字段或特征
    result1 = pages_utils.multiselect_all(
        st, '全选-气象数据', filterUnique(weatherNameList, pages_utils.reservedField),
        'tempTemperature', 'collapsed')
    result2 = pages_utils.multiselect_all(
        st, '全选-植保数据', filterUnique(plantNameList, pages_utils.reservedField),
        'tempPlant', 'collapsed')
    result3 = pages_utils.multiselect_all(
        st, '全选-农学数据', filterUnique(agricultureNameList, pages_utils.reservedField),
        'tempAgriculture', 'collapsed')

# ===============显示右上预处理方法选项===============
with dataPCM:
    st.markdown("##### 预处理方法")
    # with tab1:
    col1, col2 = st.columns(2)

    with col1:
        agree = st.checkbox('剔除异常值', key='checkbox0', on_change=clear_other, args=[0])
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
            img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, 'Figure_5.png'))
            st.image(img)
        # st.markdown('---')
    if agree:
        # 异常值检测(温度和降水)
        # 显示缺失值信息
        info = '疑似异常字段:\n'
        # 第一次使用原始数据集,而后基于预处理后数据集多次处理
        if pages_utils.TempDataSet[1].shape[0] == 0:
            dataFrameTemp = pages_utils.TempDataSet[0]
        else:
            dataFrameTemp = pages_utils.TempDataSet[1]

        # infoT1 = PretreatmentMethod.detectLinearInterpolationWeather(dataFrameTemp)
        # infoT2 = PretreatmentMethod.detectLinearInterpolationRain(dataFrameTemp)
        columnList, lowNum, upNum, lowCount, upCount = PretreatmentMethod.detect_outliers_iqr(dataFrameTemp,
                                                                                              pages_utils.reservedField)
        if not len(columnList):
            info = '无异常字段\n'
            st.info(f"{info}\n", icon="ℹ️️")
        else:
            infoT1 = ''
            for columnT, lowNumT, upNumT, lowCountT, upCountT in zip(columnList, lowNum, upNum, lowCount, upCount):
                infoT1 += f"* {columnT} 下限:{round(lowNumT, 3)} 个数:{lowCountT} 上限:{round(upNumT, 3)} 个数:{upCountT}\n"
            st.warning(f"{info}  \n{infoT1}", icon="⚠️")

        coll11, coll22 = st.columns([0.3, 0.6])
        with coll11:
            number2 = st.text_input("剔除大于以下数值外的值", value=0.1)
            number3 = st.text_input("剔除小于以下数值外的值", value=0.1)
            st.session_state["preMethodName"]['param1'] = number2
            st.session_state["preMethodName"]['param2'] = number3

            if number3:
                # 检测剔除参数最小值>最大值
                if PretreatmentMethod.detectLinearInterpolationParam([number2, number3]):
                    st.toast('剔除数据的最小值>最大值', icon="⚠️")

        with coll22:
            st.info('剔除方法介绍\n'
                    '* 描述:剔除最大值和最小值区域外的异常值\n'
                    '* 疑似异常值检测:基于四分位数上下限\n', icon="ℹ️")
            img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '3.png'))
            st.image(img)

    # =======================添加处理至任务清单=======================

    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('添加处理', on_click=clearOption, type='primary')
    if btn:
        # 检测用户行为-输入特征为空(预处理方法空判定未添加)
        if not len(result1 + result2 + result3):
            st.toast('未选择特征  \n请重新添加处理', icon="⚠️")
        else:
            # 获取数据类型
            if result1:
                dataType = '气象数据'
            elif result2:
                dataType = '植保数据'
            elif result3:
                dataType = '农学数据'
            new_data = {
                "编号": pages_utils.generateID(),
                "数据类型": dataType,
                "输入字段": mergeExcludeArray(result1, result2, result3, pages_utils.reservedField),
                "预处理后字段": None,
                "预处理方法": getCheckboxName(st.session_state["preMethodName"]['checkBox']),
                "方法参数": [value for key, value in st.session_state["preMethodName"].items() if
                             key != 'checkBox'],
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
            interval_col34, interval_col33 = st.columns([6, 1])
            with interval_col33:
                # residualField = [arr for arr in pages_utils.TempDataSet[0].columns if
                #                  arr not in mergeArray4(
                #                      ['经度', '纬度',
                #                       "年", "DayOfYear"], result1, result2, result3)]
                # print(f'剩余字段{residualField}')
                # 默认保留上一环节所有字段
                # reservedFiled = pages_utils.multiselect_all(
                #     st, '全选',
                #     residualField,
                #     'temp1', 'collapsed')
                btn2 = st.button('运行', on_click=onRun, type='primary')

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
                            # 获取第一个缺失值的行号
                            # print(f"第一个缺失值的行号: {first_missing_index}")

                            # 计算前5行和后5行的起始和结束索引
                            start_index = max(first_missing_index - 5, 0)
                            end_index = min(first_missing_index + 5 + 1, len(data_before))
                            # 取第一个缺失值对应前15行和后15行预处理数据
                            data_before_surrounding_data = data_before.iloc[start_index:end_index]
                            data_after_surrounding_data = data_after.iloc[start_index:end_index]
                            # 绘制对比折线图
                            plt.figure(figsize=(10, 6))
                            # print(pages_utils.TempDataSet[1]['DayOfYear'])
                            # 取第一个缺失值对应前15行和后15行'经度', '纬度', '年'数据
                            missing_rows = \
                                pages_utils.TempDataSet[1].loc[
                                    missing_indices, ['经度', '纬度', '年', 'DayOfYear']].to_dict(
                                    'records')[0]
                            province, station, year = missing_rows['经度'], missing_rows['纬度'], missing_rows[
                                '年']
                            # print(missing_rows['DayOfYear'])
                            # 整理前后15天dayOfYear为x轴
                            # 提取数据列，获取从 start_index 到 end_index 范围内的行数
                            # 生成从 start_index 到 end_index 的数字序列
                            figure_x = pd.DataFrame({'row': list(range(start_index, end_index))})
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
                            plt.xlabel('行号')
                            plt.ylabel(inputFields[o][0])
                            plt.figtext(0.5, -0.01,
                                        f'图{st.session_state.IMAGECOUNT} {inputFields[o][0]}字段部分数据插补前后对比图',
                                        ha='center', fontsize=16)
                            plt.legend()
                            st.pyplot(plt)
                            st.session_state.IMAGECOUNT += 1
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
                            fig.suptitle(f'图{st.session_state.IMAGECOUNT} {data_before.name}数据剔除前后对比箱型图',
                                         fontsize=16)
                            st.pyplot(fig)
                            st.session_state.IMAGECOUNT += 1

            else:
                st.info('跳过预处理', icon="ℹ️️")

            interval_col34, interval_col33 = st.columns([5, 1])
            # want_to_contribute = interval_col34.button("跳转至可视化界面")
            # if want_to_contribute:
            #     switch_page(r"E:\a_python\program\diseaseForecastStreamlit\pages\Visualization.py")
            btn3 = interval_col33.button('返回', on_click=firstPage)
