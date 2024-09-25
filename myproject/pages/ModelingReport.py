"""
@Author : SakuraFox
@Time: 2024-08-10 9:06
@File : ModelingReport.py
@Description : 建模报告
"""
import base64
import itertools
import os.path
import random
from datetime import datetime

import streamlit as st

from PIL import Image
from matplotlib.ticker import MaxNLocator
from sklearn.metrics import confusion_matrix
from st_pages import hide_pages

from lib.share import RESOURCE_IMAGES_PATH, RESOURCE_PROCESS_PATH, RESOURCE_MODELRESULT_PATH
from pages import ui, pages_utils
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 显示可视化中文图例
plt.rcParams['font.sans-serif'] = 'SimHei'
matplotlib.rcParams['axes.unicode_minus'] = False

st.set_page_config(
    layout="wide"
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr1 {display: none;}
    </style>
    """, unsafe_allow_html=True)
if st.session_state.isPlanarInterface:
    hide_pages(
        [
            "测试界面",
            "原始数据",
            "数据预处理",
            "特征计算",
            "特征优选",
            "基于天气情景生成器的模型评价",
            "建模报告",
            "数据下载中心",
        ]
    )
else:
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
            "数据下载中心-面状",
        ]
    )

category_colors_cycle = itertools.cycle(
    [
        # ui.color("red-70"),
        ui.color("orange-70"),
        ui.color("light-blue-70"),
        ui.color("blue-green-70"),
        ui.color("blue-70"),
        ui.color("violet-70"),
        ui.color("red-70"),
        ui.color("green-70"),
    ]
)


def category(name, description=None):
    ui.colored_subHeader(name, next(category_colors_cycle), description)
    st.write("")


def generateID():
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(16):
        random_str += base_str[random.randint(0, length)]
    return random_str


# st.header('建模报告')
colHead1, colHead2 = st.columns([0.7, 0.2])
with colHead1:
    st.title('多场景作物病虫害预测建模报告')
    st.markdown(f'#### &emsp;&emsp;场景名称:{st.session_state.modelingName}')

with colHead2:
    st.markdown(' ')
    st.markdown(f'#### 编号:2024{generateID()[:10]}')
    current_date = datetime.now().strftime('%Y年%m月%d日')
    st.markdown(f'#### 日期: {current_date}')

# st.markdown('# 建模报告')
st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 28px;
}
</style>
""",
    unsafe_allow_html=True,
)
if 'hideBtnDict' not in st.session_state:
    st.session_state.hideBtnDict = {
        'brief': False,
        'raw': False,
        'pre': False,
        'fc': False,
        'fo': False,
        'mb': False,
        'wg': False,
    }

hideBtnBrief = st.empty()
hideBtnRaw = st.empty()
hideBtnPre = st.empty()
hideBtnFC = st.empty()
hideBtnFO = st.empty()
hideBtnMB = st.empty()
hideBtnWG = st.empty()

with hideBtnBrief.container():
    category("ℹ️ 摘要")
    # pages_utils.TempDataSetField[3]["特征优选方法"] = ["方法A", "方法B", "方法C"]

    aInfoGap1 = '、'.join(list(set(pages_utils.TempDataSetField[0]['数据类型'].tolist()))) if len(
        pages_utils.TempDataSetField[0]['数据类型'].tolist()) else '(待进行处理)'
    aInfoGap2 = '、'.join(pages_utils.TempDataSetField[1]['预处理方法'].tolist()) if len(
        pages_utils.TempDataSetField[1]['预处理方法'].tolist()) else '(待进行处理)'
    aInfoGap3 = '、'.join(pages_utils.TempDataSetField[2]['特征计算方法'].tolist()) if len(
        pages_utils.TempDataSetField[2]['特征计算方法'].tolist()) else '(待进行处理)'
    aInfoGap4 = '、'.join(pages_utils.TempDataSetField[3]['特征优选方法'].tolist()) if len(
        pages_utils.TempDataSetField[3]['特征优选方法'].tolist()) else '(待进行处理)'
    aInfoGap5 = '、'.join(pages_utils.TempDataSetField[4]['特征'].tolist()[0]) if len(
        pages_utils.TempDataSetField[4]['特征'].tolist()) else '(待进行处理)'
    # pages_utils.TempDataSet[4] = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

    rows, columns = pages_utils.TempDataSet[4].shape
    aInfoGap6 = f'{rows}*{columns}'
    aInfoGap7 = '、'.join(pages_utils.TempDataSetField[4]['模型'].tolist()) if len(
        pages_utils.TempDataSetField[4]['特征'].tolist()) else '(待进行处理)'
    if len(pages_utils.TempDataSetField[4]['特征'].tolist()):
        mbInfo4_list = []
        for item in pages_utils.TempDataSetField[4]['评价指标']:
            formatted = '、'.join([f'{key}={round(value, 3)}' for key, value in eval(item).items()])
            mbInfo4_list.append(formatted)
        aInfoGap8 = '；'.join(mbInfo4_list)
    else:
        aInfoGap8 = '(待进行处理)'
    # st.session_state.modelSituationIndexResult = {'高温多雨': 0.45}
    # st.session_state.modelSituationIndexResult = {}
    aInfoGap9 = '、'.join(st.session_state.modelReportWeatherInfo['情景']) if len(
        st.session_state.modelReportWeatherInfo['模型']) else '(待进行处理)'
    aInfoGap13 = '、'.join(st.session_state.modelReportWeatherInfo['模型']) if len(
        st.session_state.modelReportWeatherInfo['模型']) else '(待进行处理)'
    # 格式化指标结果
    if len(st.session_state.modelReportWeatherInfo['模型']):
        values_list = list(st.session_state.modelSituationIndexResult.values())
        # 创建结果列表
        data = {}

        # 遍历并格式化为指定格式
        for value in values_list:
            # 提取文件路径中的模型名称
            file_path = value[0]
            # 提取模型名称和情景
            model_info = os.path.basename(file_path).split('_applicationPredict.xlsx')[0].split('_')

            if len(model_info) >= 2:
                model_name, scenario = model_info[0], model_info[1]

                # 将精度值存入字典
                data.setdefault(model_name, {})[scenario] = float(value[1])

        aInfoGap10 = data
    else:
        aInfoGap10 = '(待进行处理)'
    aInfoGap11 = '较一致' if 0.45 < 1 else '较不一致'  # 天气情景好
    aInfoGap12 = ['较高', '较好'] if 0.45 < 1 else ['较低', '较差']  # 模型评价和天气情景都好
    aInfoModelName = st.session_state.modelingName

    preInfo = f'通过<u>{aInfoGap2}</u>预处理步骤，' if len(
        pages_utils.TempDataSetField[1]['预处理方法'].tolist()) else ''
    abstractInfo = f"""
    ##### &emsp;&emsp;本次建模使用了<u>{aInfoGap1}</u>，{preInfo}结合<u>{aInfoGap3}</u>环节，并利用<u>{aInfoGap4}</u>筛选出优选特征集，包括<u>{aInfoGap5}</u>，数据维度为<u>{aInfoGap6}</u>，最后采用<u>{aInfoGap7}方法</u>，构建了<u>{aInfoModelName}</u>，模型精度分别为<u>{aInfoGap8}</u>。
    ##### &emsp;&emsp;同时，基于天气情景生成器模拟生成了<u>{aInfoGap9}</u>的气象情景，对<u>{aInfoGap13}</u>进行模型评估，得到静态偏差指标Dev_S，结果分别如下：
    """
    abstractInfo1 = f"""
    ##### &emsp;&emsp;综合上述结果，<u>{aInfoGap13}</u>模型表现出<u>{aInfoGap12[0]}</u>的可靠性和预测效果，参数设置合理，具有<u>{aInfoGap12[1]}</u>的鲁棒性。
    """
    st.markdown(abstractInfo, unsafe_allow_html=True)
    # 创建 DataFrame
    df = pd.DataFrame(aInfoGap10).T.fillna('')  # 转置并填充空值
    st.table(df)
    st.markdown(abstractInfo1, unsafe_allow_html=True)
    colInfo1, colInfo2, colInfo3, colInfo4 = st.columns(4)
    # if btnBrief:
    #     st.session_state.hideBtnDict['brief'] = True

with hideBtnRaw.container():
    category("📊️ 原始数据")
    array_1d = [item for sublist in pages_utils.TempDataSetField[0]['字段'] for item in sublist]

    rInfo1 = '、'.join(list(set(array_1d)))
    # pages_utils.TempDataSet[0] = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    rowsR, columnsR = pages_utils.TempDataSet[0].shape
    rInfo2 = f'{rowsR}*{columnsR}'
    rawInfo1 = f"""
##### &emsp;&emsp;本次上传的原始数据集包含<u>{aInfoGap1}</u>，具体字段为：<u>{rInfo1}</u>，数据维度为<u>{rInfo2}</u>。
                """
    st.markdown(rawInfo1, unsafe_allow_html=True)
    # if btnRaw:
    #     st.session_state.hideBtnDict['raw'] = True
with hideBtnPre.container():
    if len(pages_utils.TempDataSetField[1]['预处理方法'].tolist()):
        category("🌌 预处理")
        preInfo1 = '、'.join(pages_utils.TempDataSetField[1]['预处理方法'].tolist())
        preInfo2 = '、'.join(list(set(pages_utils.TempDataSetField[1]['输入字段'].tolist())))
        # pages_utils.TempDataSet[1] = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        rowsP, columnsP = pages_utils.TempDataSet[1].shape
        preInfo3 = f'{rowsP}'
        st.markdown(f'##### &emsp;&emsp;本次预处理使用了<u>{preInfo1}</u>方法，'
                    f'处理字段为：<u>{preInfo2}</u>，'
                    f'处理后剩余数据为<u>{preInfo3}</u>条，具体内容如下', unsafe_allow_html=True)
        for indexT, tempPreM in enumerate(pages_utils.TempDataSetField[1]['预处理方法'].tolist()):
            inputFields = pages_utils.TempDataSetField[1]["输入字段"].tolist()

            if tempPreM == '缺失值插补':
                data_before_temp = st.session_state["DPVisualInformation"][indexT]['before']
                data_after_temp = st.session_state["DPVisualInformation"][indexT]['after']
                # print(inputFields[o][0])
                data_before = pd.DataFrame({inputFields[indexT][0]: data_before_temp})
                data_after = pd.DataFrame({inputFields[indexT][0]: data_after_temp})
                # 查找缺失值的索引
                missing_indices = data_before[data_before[inputFields[indexT][0]].isna()].index
                # print(f'缺失索引:{missing_indices}')
                # 获取第一个缺失值的索引
                # first_missing_index = missing_indices[0]
                # 获取第一个缺失值的行号
                first_missing_index = 35
                # print(f"第一个缺失值的行号: {first_missing_index}")

                # 计算前5行和后5行的起始和结束索引
                start_index = max(first_missing_index - 15, 0)
                end_index = min(first_missing_index + 15 + 1, len(data_before))
                # 取第一个缺失值对应前15行和后15行预处理数据
                data_before_surrounding_data = data_before.iloc[start_index:end_index]
                data_after_surrounding_data = data_after.iloc[start_index:end_index]
                # 绘制对比折线图
                fig, ax = plt.subplots(figsize=(10, 6))
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
                plt.plot(figure_x, data_before_surrounding_data[inputFields[indexT][0]],
                         label='原始数据',
                         color='black',
                         linestyle='-', marker='o')
                # 绘制插补后的折线图
                plt.plot(figure_x, data_after_surrounding_data[inputFields[indexT][0]],
                         label='插补后数据', color='blue',
                         linestyle='--',
                         marker='o', alpha=0.3)
                plt.xlabel('行号')
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                plt.ylabel(inputFields[indexT][0])
                plt.figtext(0.5, -0.01,
                            f'图{st.session_state.IMAGECOUNT} {inputFields[indexT][0]}字段部分数据插补前后对比图',
                            ha='center', fontsize=16)
                plt.legend()
                st.pyplot(plt)
                st.session_state.IMAGECOUNT += 1
            elif tempPreM == '剔除异常值':
                # 剔除异常值-箱型图
                data_before = st.session_state["DPVisualInformation"][indexT]['before']
                data_after = st.session_state["DPVisualInformation"][indexT]['after']
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

        # colPart1, colPart2, colPart3 = st.columns(3)
        # colPart1.metric('预处理字段', '温度')
        # colPart2.metric('预处理方法', '缺失值插补')
        # colPart3.metric('预处理数据条数', '3')  # 根据输入和输出字段对应的数据对比
        # if btnPre:
        #     st.session_state.hideBtnDict['pre'] = True
with hideBtnFC.container():
    if len(pages_utils.TempDataSetField[2]['特征计算方法'].tolist()):
        category("🌍 特征计算")

        fcInfo2 = '、'.join(pages_utils.TempDataSetField[2]['特征计算方法'].tolist())
        fcInfo1 = '、'.join(
            list(set([item for sublist in pages_utils.TempDataSetField[2]['输入特征'].tolist() for item in sublist])))
        fcInfo3 = '、'.join(list(set(pages_utils.TempDataSetField[2]['备选特征'].tolist())))
        st.markdown(f'##### &emsp;&emsp;本次特征计算基于<u>{fcInfo1}</u>数据，'
                    f'通过<u>{fcInfo2}</u>方法，得到了特征包括：<u>{fcInfo3}</u>，'
                    f'具体内容如下：', unsafe_allow_html=True)
        for indexT, tempFCM in enumerate(pages_utils.TempDataSetField[2]['特征计算方法'].tolist()):
            # 创建DataFrame
            data_after = pages_utils.TempDataSet[2]
            # 特征名称
            dataColumn = pages_utils.TempDataSetField[2]['备选特征'].tolist()[indexT]
            data_after = data_after[pages_utils.reservedField + [dataColumn]]
            # 删除含有缺失值的行
            data_after = data_after.dropna()
            # 去除重复值
            data_after = data_after.drop_duplicates()

            if tempFCM == '基于活动积温的生育期计算':
                # 选择最多8个纬度
                top_stations = data_after['纬度'].value_counts().nlargest(8).index
                df_filtered_stations = data_after[data_after['纬度'].isin(top_stations)]

                # 选择最多3个年份
                top_years = data_after['年'].value_counts().nlargest(3).index
                df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]

                # 绘制折线图
                plt.figure(figsize=(10, 6))
                sns.lineplot(
                    data=df_filtered,
                    x="纬度",
                    y=dataColumn,
                    hue="年",
                    marker="o"
                )
                # 设置标签和标题
                plt.xlabel("地区")
                plt.ylabel(f'{dataColumn}(Day Of Year)')
                plt.figtext(0.5, -0.01,
                            f'图{st.session_state.IMAGECOUNT} 部分地区各年份{dataColumn}图',
                            ha='center', fontsize=16)
                st.pyplot(plt)
            elif tempFCM == '降水累积量计算':
                # 时期范围名称修剪
                integratedDataColumnT = dataColumn.split('_')
                integratedDataColumn = integratedDataColumnT[0] + '至' + integratedDataColumnT[1] + \
                                       integratedDataColumnT[2]
                # 选择最多8个纬度
                top_stations = data_after['纬度'].value_counts().nlargest(8).index
                df_filtered_stations = data_after[data_after['纬度'].isin(top_stations)]
                # 选择最多5个年份
                top_years = data_after['年'].value_counts().nlargest(5).index
                df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                print(df_filtered)
                # 绘制柱状图
                plt.figure(figsize=(10, 6))
                sns.barplot(
                    data=df_filtered,
                    x="纬度",
                    y=dataColumn,
                    hue="年",
                    dodge=True,
                    saturation=1
                )
                # 设置标签和标题
                plt.xlabel("地区")
                plt.ylabel("降水累积量(mm)")
                plt.figtext(0.5, -0.01,
                            f'图{st.session_state.IMAGECOUNT} 部分地区各年份{integratedDataColumn}图',
                            ha='center', fontsize=16)
                st.pyplot(plt)
                st.session_state.IMAGECOUNT += 1
            elif tempFCM == '降雨日数计算':
                # 时期范围名称修剪
                integratedDataColumnRT = dataColumn.split('_')
                integratedDataColumnR = integratedDataColumnRT[0] + '至' + integratedDataColumnRT[1] + \
                                        integratedDataColumnRT[2]
                # 选择最多8个纬度
                top_stations = data_after['纬度'].value_counts().nlargest(8).index
                df_filtered_stations = data_after[data_after['纬度'].isin(top_stations)]

                # 选择最多3个年份
                top_years = data_after['年'].value_counts().nlargest(3).index
                df_filtered = df_filtered_stations[df_filtered_stations['年'].isin(top_years)]
                # 绘制折线图
                plt.figure(figsize=(10, 6))
                sns.lineplot(
                    data=df_filtered,
                    x="纬度",
                    y=dataColumn,
                    hue="年",
                    marker="o"
                )
                # 设置标签和标题
                plt.xlabel("地区")
                plt.ylabel("降雨日数(天)")
                plt.figtext(0.5, -0.01,
                            f'图{st.session_state.IMAGECOUNT} 部分地区各年份{integratedDataColumnR}图',
                            ha='center', fontsize=16)
                st.pyplot(plt)

        # 命名: 界面名称缩写
        # colFC1, colFC2 = st.columns(2)
        # with colFC1:
        # img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '特征计算-降水累积量.png'))
        # st.image(img)
        # colFCPart1, colFCPart2 = st.columns(2)
        # colFCPart1.metric('输入字段', '降水')
        # colFCPart2.metric('特征计算方法', '降水累积量计算')
        # colFCPart3, colFCPart4 = st.columns(2)
        # colFCPart3.metric('输出特征', '07-19_08-23_降水累积量')
        # colFCPart4.metric('特征条数', '1271')
        # if btnFC:
        #     st.session_state.hideBtnDict['fc'] = True

with hideBtnFO.container():
    if len(pages_utils.TempDataSetField[3]['特征优选方法'].tolist()):
        category("🌎 特征优选")
        foInfo1 = '、'.join(list(set(pages_utils.TempDataSetField[3]['特征优选方法'].tolist())))
        # pages_utils.TempDataSetField[3]["优选特征"] = ["特征A", "特征B", "特征C"]
        # print('--测试特征因子---')
        featureListT = pages_utils.TempDataSetField[3]['优选特征'].tolist()[0].split(',')
        # print(featureListT)
        foInfo2 = '、'.join(pages_utils.TempDataSetField[3]['优选特征'].tolist())

        st.markdown(f'##### &emsp;&emsp;本次特征优选基于<u>{foInfo1}</u>进行筛选，'
                    f'最终选取了<u>{len(featureListT)}</u>个特征因子，'
                    f'形成最终优选特征集，包括<u>{foInfo2}</u>，具体内容如下：',
                    unsafe_allow_html=True)
        for indexT, tempFOM in enumerate(pages_utils.TempDataSetField[3]['特征优选方法'].tolist()):
            # # 特征名称
            # dataColumn = pages_utils.TempDataSetField[3]['输入特征'].tolist()[indexT]
            # print(dataColumn)
            # # 创建DataFrame
            # data_after = pages_utils.TempDataSet[3][dataColumn]
            data_after = st.session_state["FOVisualInformation"][indexT]['after']
            # 特征名称
            dataColumn = st.session_state["FOVisualInformation"][indexT]['column']
            # 特征名称
            if tempFOM == 'Pearson相关性分析':
                # 可视化
                # 使用Seaborn绘制热图
                plt.figure(figsize=(10, 8))
                sns.heatmap(data_after, annot=True, cmap='coolwarm', center=0)

                plt.figtext(0.45, -0.13,
                            f'图{st.session_state.IMAGECOUNT} Pearson互相关分析矩阵图',
                            ha='center', fontsize=16)
                st.session_state.IMAGECOUNT += 1
                st.pyplot(plt)

            elif tempFOM == 'Relief-F互相关分析':
                # 可视化
                # 创建柱状图
                plt.figure(figsize=(10, 6))
                plt.bar(st.session_state["FOVisualInformation"][indexT]['column'],
                        st.session_state["FOVisualInformation"][indexT]['value'], color='blue')
                # 添加标题和标签
                plt.title('基于Relief-F特征因子权值排序图')
                plt.xlabel('特征')
                plt.ylabel('特征权值')

                # 基准线
                plt.axhline(y=st.session_state["FOVisualInformation"][indexT]['standard'], color='red',
                            linestyle='--', linewidth=1, label='基准线')
                # 显示图表
                plt.xticks(rotation=45, ha='right')  # 旋转x轴标签
                plt.tight_layout()  # 调整布局以防止标签重叠
                st.pyplot(plt)
    # colFCPart1, colFCPart2 = st.columns([0.7, 0.3])
    # colFCPart1.metric('输入特征', '降水、温度')
    # colFCPart2.metric('特征优选方法', 'Pearson相关性分析')
    # colFCPart3, colFCPart4 = st.columns([0.7, 0.3])
    # colFCPart3.metric('优选特征集', '温度')
    # colFCPart4.metric('筛选条件', '相关系数(R)<0.8')
    # if btnFO:
    #     st.session_state.hideBtnDict['fo'] = True

with hideBtnMB.container():
    if len(pages_utils.TempDataSetField[4]['模型'].tolist()):
        category("🌏 模型构建")
        # pages_utils.TempDataSetField[4]['数据集划分比例'] = ['7：3']
        # pages_utils.TempDataSetField[4]['模型'] = ['PLSR']
        mbInfo1 = '、'.join(pages_utils.TempDataSetField[4]['模型'].tolist())
        mbInfo2 = st.session_state.modelingName
        mbInfo3 = pages_utils.TempDataSetField[4]['数据集划分比例'].tolist()[0]
        # print(pages_utils.TempDataSetField[4]['评价指标'].tolist())
        # 处理多条评价指标，并将每个字典的键值对格式化为 "key=value"
        mbInfo4 = '；'.join(mbInfo4_list)
        st.markdown(f'##### &emsp;&emsp;本次建模基于优选特征集，'
                    f'使用了<u>{mbInfo1}</u>方法构建了<u>{mbInfo2}</u>。'
                    f'训练集与验证集比例为<u>{mbInfo3}</u>，'
                    f'模型精度分别为<u>{mbInfo4}</u>。',
                    unsafe_allow_html=True)
        if '峰值' in pages_utils.TempDataSetField[4]['标签'].tolist():
            evaluationIndex = pages_utils.TempDataSetField[4]["评价指标"].tolist()
            for indexT1, temp in enumerate(pages_utils.TempDataSetField[4]['模型'].tolist()):
                path1 = os.path.join(RESOURCE_MODELRESULT_PATH, 'predict')
                testLabelDF = pd.read_excel(os.path.join(path1, f'{temp}_testLabel.xlsx'))
                predictLabelDF = pd.read_excel(os.path.join(path1, f'{temp}_predictLabel.xlsx'))
                # 假设第一列包含要绘制的数据
                actual_values = testLabelDF.iloc[:, 0]
                predicted_values = predictLabelDF.iloc[:, 0]
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
                            f'图{st.session_state.IMAGECOUNT} {temp}模型精度评价散点图',
                            ha='center', fontsize=16)
                # 精度结果直接显示在图中
                metrics_text = "\n".join(
                    [f"{key}={round(value, 3)}" for key, value in eval(evaluationIndex[indexT1]).items()])
                plt.text(0.05, 0.95, metrics_text, transform=ax.transAxes, fontsize=10,
                         verticalalignment='top', bbox=dict(facecolor='white', alpha=0.2))
                st.pyplot(fig)
        else:
            for temp in pages_utils.TempDataSetField[4]['模型'].tolist():
                path1 = os.path.join(RESOURCE_MODELRESULT_PATH, 'predict')
                testLabelDF = pd.read_excel(os.path.join(path1, f'{temp}_testLabel.xlsx'))
                predictLabelDF = pd.read_excel(os.path.join(path1, f'{temp}_predictLabel.xlsx'))
                # 绘制混淆矩阵图
                fig, ax = plt.subplots()
                conf_matrix = confusion_matrix(testLabelDF, predictLabelDF)
                sns.heatmap(conf_matrix, annot=True, cmap='plasma', fmt='g', ax=ax)
                ax.set_xlabel('实际病害发生程度')
                ax.set_ylabel('预测病害发生程度')
                plt.title(f'{temp}模型混淆矩阵图')
                st.pyplot(fig)
        # cc1, colMBPart1, colMBPart2 = st.columns([0.7, 0.3, 0.3])
        # cc1.metric('特征集', 'class-AREA_MN、land-FRAC_MN、class-FRAC_MN、01-01_01-31降雨日数、07-19_08-23_降水累积量')
        # colMBPart1.metric('标签', '病害峰值')
        # colMBPart2.metric('特征大小', '5*90')
        #
        # cc2, colMBPart3, colMBPart4 = st.columns([0.7, 0.3, 0.3])
        # cc2.metric('模型', 'PLSR')
        # colMBPart3.metric('评价指标', 'MSE、R方')
        # colMBPart4.metric('数据集分配比例', '5:6')
        # if btnMB:
        #     st.session_state.hideBtnDict['mb'] = True

with hideBtnWG.container():
    if len(st.session_state.modelReportWeatherInfo['模型']):
        category("🌐 天气情景生成器")
        wgInfo1 = st.session_state.modelReportWeatherInfo['经度']
        wgInfo2 = st.session_state.modelReportWeatherInfo['纬度']
        wgInfo3 = st.session_state.modelReportWeatherInfo['年限']
        wgInfo4 = '、'.join(st.session_state.modelReportWeatherInfo['情景'])
        wgInfo5 = '、'.join(st.session_state.modelReportWeatherInfo['模型'])
        st.markdown(f'##### &emsp;&emsp;本模块基于经度:<u>{wgInfo1}</u>、纬度:<u>{wgInfo2}</u>地区的历史气象数据，'
                    f'利用天气情景生成器模拟生成了为期<u>{wgInfo3}</u>年的<u>{wgInfo4}</u>气象情景，'
                    f'各情景部分气象数据具体内容如下：',
                    unsafe_allow_html=True)

        # 获取目录下的所有条目
        path1 = os.path.join(RESOURCE_PROCESS_PATH, 'weatherGeneratorOutput')
        for root, dirs, files in os.walk(path1):
            # 获取当前文件夹名称
            current_folder = os.path.basename(root)
            for j, file in enumerate(files):
                if file == '第1年.xlsx':
                    # 读取表格
                    df = pd.read_excel(os.path.join(root, file))
                    # 创建一个新的图形对象
                    plt.figure(figsize=(12, 6))
                    # 使用 Seaborn 绘制折线图
                    sns.lineplot(data=df, x="DayOfYear", y="最高温度", label="最高温度")
                    sns.lineplot(data=df, x="DayOfYear", y="最低温度", label="最低温度")
                    # 设置 x 和 y 轴标签、标题、图例等
                    plt.xlabel('日期 (Day of Year)')
                    plt.ylabel('温度 (℃)')
                    plt.title(f'({current_folder}) 每日最高温度和最低温度')
                    # 保存图片到本地
                    # plt.savefig(f'{label_list[j]}_温度.png', dpi=300, bbox_inches='tight')  # 保存为高分辨率 PNG 文件
                    # 添加图例
                    plt.legend()
                    # 显示图表
                    st.pyplot(plt)
                    # 创建一个新的图形对象
                    plt.figure(figsize=(12, 6))
                    # 使用 Seaborn 绘制折线图
                    sns.barplot(data=df, x="DayOfYear", y="降水", label="每日降水量")

                    # 设置 x 和 y 轴标签、标题、图例等
                    plt.xlabel('日期 (Day of Year)')
                    plt.ylabel('降水量(mm)')
                    plt.title(f'({current_folder}) 每日降水量')
                    # 设置 x 轴的刻度间隔为每 30 天显示一次
                    plt.xticks(ticks=range(1, 365, 30))
                    # 添加图例
                    plt.legend()
                    # 显示图表
                    st.pyplot(plt)

        # colWG1, colWG2 = st.columns(2)
        # with colWG1:
        #     st.metric('地区', '湖南省湘阴县')
        #     st.metric('模型', 'RF、SVM')
        # with colWG2:
        #     st.metric('天气情景', '高温少雨、低温多雨')
        #     st.metric('年限长度', '3年')
        # if btnWG:
        #     st.session_state.hideBtnDict['wg'] = True


# # 控制隐藏
# for key, btn in st.session_state.hideBtnDict.items():
#     if st.session_state.hideBtnDict.get(key, False):
#         if key == 'brief':
#             hideBtnBrief.empty()
#         elif key == 'raw':
#             hideBtnRaw.empty()
#         elif key == 'pre':
#             hideBtnPre.empty()
#         elif key == 'fc':
#             hideBtnFC.empty()
#         elif key == 'fo':
#             hideBtnFO.empty()
#         elif key == 'mb':
#             hideBtnMB.empty()
#         elif key == 'wg':
#             hideBtnWG.empty()


def displayLocalGIF1(placeholder, localImagePath, caption):
    imgFile = open(localImagePath, "rb")
    contents = imgFile.read()
    imgData = base64.b64encode(contents).decode("utf-8")
    imgFile.close()

    # Define CSS styles for the container and caption
    container_style = (
        "position: relative;"  # Enable relative positioning
        "display: inline-block;"  # Display as inline-block to align with placeholder
    )

    caption_style = (
        "font-size: 20px;"  # Adjust the font size as needed
        "color: #888888;"  # Dimmer color
        "text-align: center;"  # Center the caption text
    )

    # Display the GIF and caption with positioning relative to the placeholder
    placeholder.markdown(f"""<div style="{container_style}">
                    <img src="data:image/gif;base64,{imgData}" width='610' height='610'>
                    <p style="{caption_style}">{caption}</p>
                    </div>""", unsafe_allow_html=True)


def displayLocalGIF2(placeholder, localImagePath1, localImagePath2, caption1, caption2):
    # Function to generate the base64 encoded image data
    def get_img_data(image_path):
        with open(image_path, "rb") as img_file:
            contents = img_file.read()
            return base64.b64encode(contents).decode("utf-8")

    imgData1 = get_img_data(localImagePath1)
    imgData2 = get_img_data(localImagePath2)

    # Define CSS styles for the container and images
    container_style = (
        "display: flex;"  # Use flexbox layout for side-by-side alignment
        "justify-content: center;"  # Center the container content
        "gap: 20px;"  # Add space between the GIFs
    )

    img_style = "width: 610px; height: 610px;"  # Set image size

    caption_style = (
        "font-size: 20px;"  # Adjust the font size as needed
        "color: #888888;"  # Dimmer color
        "text-align: center;"  # Center the caption text
    )

    # Display the GIFs and captions side by side
    placeholder.markdown(f"""
        <div style="{container_style}">
            <div>
                <img src="data:image/gif;base64,{imgData1}" style="{img_style}">
                <p style="{caption_style}">{caption1}</p>
            </div>
            <div>
                <img src="data:image/gif;base64,{imgData2}" style="{img_style}">
                <p style="{caption_style}">{caption2}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


category("🌑 模型应用与评估")

if len(st.session_state.modelReportWeatherInfo['模型']):
    st.markdown(f'##### &emsp;&emsp;针对经度:<u>{wgInfo1}</u>、纬度:<u>{wgInfo2}</u>地区，'
                f'基于气象多情景仿真器输出各情景的的应用结果如下：',
                unsafe_allow_html=True)
    items = list(st.session_state.modelSituationIndexResult.items())
    if '峰值' in pages_utils.TempDataSetField[4]['标签'].tolist():
        pass
    else:
        for i, (metric_name, metric_value) in enumerate(items):
            path = os.path.join(
                RESOURCE_MODELRESULT_PATH,
                'modelsSimulateWeatherIndexResult',
                metric_name +
                '_applicationPredict' +
                '.xlsx')
            weatherNameT = metric_name.split('_')[1]
            df = pd.read_excel(path)
            # Plotting
            fig, ax = plt.subplots(figsize=(10, 6))

            # Bar chart for Predicted_value
            ax.bar(df['年'] - 0.2, df['Predicted_value'], width=0.4, label='预测病害发生程度', color='b',
                   align='center')

            # Bar chart for 病害发生程度
            ax.bar(df['年'] + 0.2, df['病害发生程度'], width=0.4, label='实际病害发生程度', color='r', align='center')
            # 添加标题和标签
            plt.title(f'{weatherNameT}情景下实际与预测病害发生程度对比图')
            plt.xlabel('年')
            plt.ylabel('病害发生程度')
            # Set x-ticks to be integers
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            # 添加图例
            plt.legend()
            st.pyplot(plt)

    endInfo1 = st.session_state.modelingName
    # pages_utils.TempDataSetFacet[4] = pd.DataFrame({'标签': ['病害峰值', 2, 3]})
    endInfo2 = pages_utils.TempDataSetField[4]['标签'].tolist()[0]
    endInfo3 = '、'.join(st.session_state.modelReportWeatherInfo['情景'])
    st.markdown(
        f'##### &emsp;&emsp;本次建模场景为<u>{endInfo1}</u>，模型输出为<u>{endInfo2}</u>。'
        f'基于静态预测模型评价方法计算可得<u>{endInfo3}</u>情景下各模型预测输出的偏差指标分别如下：  \n',
        unsafe_allow_html=True)
    # 创建 DataFrame
    df = pd.DataFrame(aInfoGap10).T.fillna('')  # 转置并填充空值
    st.table(df)
    st.markdown(
        f'##### &emsp;&emsp;根据上述计算结果进行综合评估，可认为上述模型<u>可靠性较高</u>，参数设置较为合理，具有良好的预测效果和鲁棒性。',
        unsafe_allow_html=True)
# if btnResult:
#     st.markdown("""
#     <style>
#     .st-emotion-cache-1vt4y43.ef3psqc12 {display: none;}
#     </style>
#     """, unsafe_allow_html=True)
# imagePath1 = os.path.join(RESOURCE_TEMPDIR_PATH, "s_output1.gif")
# imagePath2 = os.path.join(RESOURCE_TEMPDIR_PATH, "e_output1.gif")
# displayLocalGIF2(st.empty(), imagePath1, imagePath2, "模型预测结果图", "模型预测结果图2")
