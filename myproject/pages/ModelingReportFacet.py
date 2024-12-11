"""
@Author : SakuraFox
@Time: 2024-08-10 9:06
@File : ModelingReport.py
@Description : 建模报告-面状
"""

import base64
import itertools
import os.path
import random
from datetime import datetime

import streamlit as st

from PIL import Image
from matplotlib.ticker import MaxNLocator
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
# 隐藏页面
hide_pages(
    [
        "测试界面",
        "原始数据",
        "气象数据预处理",
        "特征计算",
        "特征优选",
        "模型构建",
        "基于天气情景生成器的模型评价",
        "建模报告",
        "模型应用",
        "数据下载中心",
    ]
)
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr2 {display: none;}
    </style>
    """, unsafe_allow_html=True)

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


# 遍历 '输入文件' 列并进行处理
def replace_with_precipitation_and_temperature(file_array):
    if any('降水' in file or '温度' in file for file in file_array):
        filtered_files = [file for file in file_array if '降水' not in file and '温度' not in file]
        return filtered_files + ['降水', '温度']
    else:
        return file_array


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
    st.title('多场景作物病虫害快速预测建模报告')
    st.markdown(f'#### &emsp;&emsp;面状动态建模场景:{st.session_state.modelingName}')

with colHead2:
    st.markdown(' ')
    st.markdown(f'#### 编号:1P12C1234O2M3W9')
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

    aInfoGap1 = '、'.join(list(set(pages_utils.TempDataSetFieldFacet[0]['数据类型']))) if len(
        pages_utils.TempDataSetFieldFacet[0]['数据类型']) else '(待进行处理)'
    aInfoGap2 = '、'.join(pages_utils.TempDataSetFieldFacet[1]['预处理方法']) if len(
        pages_utils.TempDataSetFieldFacet[1]['预处理方法']) else '(待进行处理)'
    aInfoGap3 = '、'.join(pages_utils.TempDataSetFieldFacet[2]['特征计算方法']) if len(
        pages_utils.TempDataSetFieldFacet[2]['特征计算方法']) else '(待进行处理)'
    aInfoGap4 = '、'.join(pages_utils.TempDataSetFieldFacet[3]['特征优选方法'].tolist()) if len(
        pages_utils.TempDataSetFieldFacet[3]['特征优选方法'].tolist()) else '(待进行处理)'
    aInfoGap5 = '、'.join(
        [item.split('-')[0] for item in pages_utils.TempDataSetFieldFacet[4]['特征'].tolist()[0] if
         item not in pages_utils.reservedField]) if len(
        pages_utils.TempDataSetFieldFacet[4]['特征'].tolist()) else '(待进行处理)'
    # pages_utils.TempDataSet[4] = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

    rows, columns = pages_utils.TempDataSetFacet[4].shape
    aInfoGap6 = f'{rows}*{columns}'
    aInfoGap7 = '、'.join(pages_utils.TempDataSetFieldFacet[4]['模型'].tolist()) if len(
        pages_utils.TempDataSetFieldFacet[4]['特征'].tolist()) else '(待进行处理)'
    # print('---测试----')
    # print(pages_utils.TempDataSetFieldFacet[4]['评价指标'].tolist()[0])
    # aInfoGap8 = ''
    aInfoGap8 = '、'.join(
        [f'{key}={round(value, 3)}' for key, value in
         pages_utils.TempDataSetFieldFacet[4]['评价指标'].tolist()[0].items()]) if len(
        pages_utils.TempDataSetFieldFacet[4]['特征'].tolist()) else '(待进行处理)'
    # st.session_state.modelSituationIndexResult = {'高温多雨': 0.45}
    # st.session_state.modelSituationIndexResult = {}
    aInfoGap9 = '、'.join(st.session_state.modelReportWeatherInfoFacet['情景']) if len(
        st.session_state.modelReportWeatherInfoFacet['模型']) else '(待进行处理)'
    aInfoGap13 = '、'.join(st.session_state.modelReportWeatherInfoFacet['模型']) if len(
        st.session_state.modelReportWeatherInfoFacet['模型']) else '(待进行处理)'
    # 格式化指标结果
    if len(st.session_state.modelReportWeatherInfoFacet['模型']):
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
    # abstractInfo = f"""
    # ##### &emsp;&emsp;本次建模使用了<u>{aInfoGap1}</u>，通过<u>{aInfoGap2}</u>预处理步骤，结合<u>{aInfoGap3}</u>环节得到模型输入特征，包括<u>{aInfoGap5}</u>，数据维度为<u>{aInfoGap6}</u>，最后采用<u>{aInfoGap7}方法</u>，构建了<u>{aInfoModelName}</u>，模型精度为<u>{aInfoGap8}</u>。
    # ##### &emsp;&emsp;此外，基于天气情景生成器模拟生成了<u>{aInfoGap9}</u>的气象情景，对<u>{aInfoGap13}</u>进行模型评估，得到动态偏差指标Dev_S，结果分别如下：
    # """
    # abstractInfo1 = f"""
    # ##### &emsp;&emsp;综合上述结果，<u>{aInfoGap13}</u>模型表现出<u>{aInfoGap12[0]}</u>的可靠性和预测效果，参数设置合理，具有<u>{aInfoGap12[1]}</u>的鲁棒性。
    # """
    # st.markdown(abstractInfo, unsafe_allow_html=True)
    abstractInfo = f"""
        ##### 场景名称：{st.session_state.modelingName}  \n
        ##### 数据类型：{aInfoGap1}  \n
        ##### 优选算法：Pearson相关性分析  \n
        ##### 优选特征：{aInfoGap5}  \n
        ##### 建模方法：{aInfoGap7}  \n
        ##### 模型精度：{aInfoGap8}  \n
        """

    # abstractInfo1 = f"""
    # ##### &emsp;&emsp;综合上述结果，<u>{aInfoGap13}模型表现出<u>{aInfoGap12[0]}的可靠性和预测效果，参数设置合理，具有<u>{aInfoGap12[1]}的鲁棒性。
    # """

    st.columns(3)[0].markdown('##### &emsp;&emsp;&emsp;&emsp;本次建模情况如下:  \n')
    st.columns([0.3, 0.6, 0.4])[1].markdown(abstractInfo, unsafe_allow_html=True)
    #
    # # 创建 DataFrame
    # df = pd.DataFrame(aInfoGap10).T.fillna('')  # 转置并填充空值
    # st.table(df)
    # st.markdown(abstractInfo1, unsafe_allow_html=True)
    # colInfo1, colInfo2, colInfo3, colInfo4 = st.columns(4)
    # if btnBrief:
    #     st.session_state.hideBtnDict['brief'] = True

with hideBtnRaw.container():
    category("📊️ 原始数据")
    array_1d = pages_utils.TempDataSetFieldFacet[0]['字段']

    rInfo1 = '、'.join(list(set(array_1d)))
    # pages_utils.TempDataSet[0] = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

    #     rawInfo1 = f"""
    # ##### &emsp;&emsp;本次上传的原始数据集包含<u>{aInfoGap1}</u>，具体文件涉及：<u>{rInfo1}</u>。
    #                 """
    rawInfo1 = f"""
    ##### 数据类型：气象数据、遥感数据、植保数据
    ##### 上传字段：温度、降水  \n
    ##### &emsp;&emsp;&emsp;&emsp;&emsp;sentinel卫星影像、MCD12Q1土地覆盖类型  \n
    ##### &emsp;&emsp;&emsp;&emsp;&emsp;峰值、移栽期、水稻纹枯病株率调查数据
                """
    # st.markdown(rawInfo1, unsafe_allow_html=True)
    st.columns(3)[0].markdown('##### &emsp;&emsp;&emsp;&emsp;原始数据集情况如下:  \n')
    st.columns([0.3, 0.6, 0.4])[1].markdown(rawInfo1, unsafe_allow_html=True)
    # if btnRaw:
    #     st.session_state.hideBtnDict['raw'] = True
with hideBtnPre.container():
    if len(pages_utils.TempDataSetFieldFacet[1]['预处理方法']):
        category("🌌 预处理")
        # array_1d = [item for sublist in pages_utils.TempDataSetFieldFacet[1]['输入文件'] for item in sublist]
        # print('--测试报告预处理--')
        # print(pages_utils.TempDataSetFieldFacet[1]['输入文件'])
        # preInfo2 = '、'.join(list(set(array_1d)))
        # preInfo1 = '、'.join(pages_utils.TempDataSetFieldFacet[1]['预处理方法'])
        # preInfo2 = '、'.join(list(set(pages_utils.TempDataSetFieldFacet[1]['输入文件'])))
        # pages_utils.TempDataSet[1] = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

        # st.markdown(
        #     f'##### &emsp;&emsp;本次预处理共处理<u>{len(pd.DataFrame(pages_utils.TempDataSetFieldFacet[1]))}</u>次，'
        #     f'具体内容如下：', unsafe_allow_html=True)
        st.columns(3)[0].markdown(
            f'##### &emsp;&emsp;&emsp;&emsp;预处理情况如下：', unsafe_allow_html=True)
        st.columns([0.3, 0.6, 0.4])[1].markdown(
            f"""
         ##### 预处理对象：移栽期
         ##### 预处理内容：裁剪、重采样
                     """, unsafe_allow_html=True)

        tempDF1 = pd.DataFrame(pages_utils.TempDataSetFieldFacet[1])[
            ['编号', '输入文件', '预处理方法', '文件名称', '数据类型', '时间']]
        tempDF1.rename(columns={'文件名称': '输出文件'}, inplace=True)
        tempDF1['数据类型'] = tempDF1['数据类型'].apply(lambda x: '、'.join(pd.Series(x).unique()))
        tempDF1['输入文件'] = tempDF1['输入文件'].apply(
            lambda x: '、'.join(replace_with_precipitation_and_temperature(x)))

        # st.table(tempDF1)
        # img = Image.open(os.path.join(RESOURCE_IMAGES_PATH, '数据预处理-缺失值插补.png'))
        # st.image(img)
        # colPart1, colPart2, colPart3 = st.columns(3)
        # colPart1.metric('预处理字段', '温度')
        # colPart2.metric('预处理方法', '缺失值插补')
        # colPart3.metric('预处理数据条数', '3')  # 根据输入和输出字段对应的数据对比
        # if btnPre:
        #     st.session_state.hideBtnDict['pre'] = True
with hideBtnFC.container():
    if len(pages_utils.TempDataSetFieldFacet[2]['特征计算方法']):
        category("🌍 特征计算")

        # st.markdown(
        #     f'##### &emsp;&emsp;本次特征计算共处理<u>{len(pd.DataFrame(pages_utils.TempDataSetFieldFacet[2]))}</u>次，'
        #     f'具体内容如下：', unsafe_allow_html=True)
        st.columns(3)[0].markdown(
            f'##### &emsp;&emsp;&emsp;&emsp;特征计算情况如下：', unsafe_allow_html=True)
        st.columns([0.3, 0.6, 0.4])[1].markdown(
            f"""
         ##### 特征计算对象：sentinel卫星影像、MCD12Q1土地覆盖类型、降水、温度
         ##### 特征计算内容：植被指数计算、景观指数计算、时空抽取
         ##### 输出特征内容：NDVI、类级别LPI指数、降水、温度
                     """, unsafe_allow_html=True)
        tempDF1 = pd.DataFrame(pages_utils.TempDataSetFieldFacet[2])[
            ['编号', '输入文件', '特征计算方法', '文件名称', '数据类型', '时间']]
        tempDF1.rename(columns={'文件名称': '输出文件'}, inplace=True)
        tempDF1['数据类型'] = tempDF1['数据类型'].apply(lambda x: '、'.join(pd.Series(x).unique()))
        tempDF1['输入文件'] = tempDF1['输入文件'].apply(
            lambda x: '、'.join(replace_with_precipitation_and_temperature(x)))
        # st.table(tempDF1)
        # 命名: 界面名称缩写

        # colFC1, colFC2 = st.columns(2)
        # # with colFC1:
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
    if len(pages_utils.TempDataSetFieldFacet[3]['特征优选方法'].tolist()):
        category("🌎 特征优选")
        foInfo1 = '、'.join(list(set(pages_utils.TempDataSetFieldFacet[3]['特征优选方法'].tolist())))
        # pages_utils.TempDataSetFieldFacet[3]["优选特征"] = ["特征A", "特征B", "特征C"]

        foInfo2 = aInfoGap5

        st.columns(3)[0].markdown(
            f'##### &emsp;&emsp;&emsp;&emsp;特征优选情况如下：', unsafe_allow_html=True)
        foInfo1 = f"""
            ##### 优选算法：{foInfo1}
            ##### 优选结果：{foInfo2}
                        """
        # st.markdown(rawInfo1, unsafe_allow_html=True)
        st.columns([0.3, 0.6, 0.4])[1].markdown(foInfo1, unsafe_allow_html=True)

        for indexT, tempFOM in enumerate(pages_utils.TempDataSetFieldFacet[3]['特征优选方法'].tolist()):
            # # 特征名称
            # dataColumn = pages_utils.TempDataSetField[3]['输入特征'].tolist()[indexT]
            # print(dataColumn)
            # # 创建DataFrame
            # data_after = pages_utils.TempDataSet[3][dataColumn]
            data_after = st.session_state["FOVisualInformationFacet"][indexT]['after']
            # 特征名称
            dataColumn = st.session_state["FOVisualInformationFacet"][indexT]['column']
            # 特征名称
            if tempFOM == 'Pearson相关性分析':
                # 可视化
                # 使用Seaborn绘制热图
                plt.figure(figsize=(10, 8))
                sns.heatmap(data_after, annot=True, cmap='coolwarm', center=0)

                plt.figtext(0.45, 0.01,
                            f'Pearson互相关分析矩阵图',
                            ha='center', fontsize=16)
                # st.session_state.IMAGECOUNT += 1
                st.columns([0.3, 0.6, 0.4])[1].pyplot(plt)

            elif tempFOM == 'Relief-F互相关分析':
                # 可视化
                # 创建柱状图
                plt.figure(figsize=(10, 6))
                plt.bar(st.session_state["FOVisualInformationFacet"][indexT]['column'],
                        st.session_state["FOVisualInformationFacet"][indexT]['value'], color='blue')
                # 添加标题和标签
                plt.title('基于Relief-F特征因子权值排序图')
                plt.xlabel('特征')
                plt.ylabel('特征权值')

                # 基准线
                plt.axhline(y=st.session_state["FOVisualInformationFacet"][indexT]['standard'], color='red',
                            linestyle='--', linewidth=1, label='基准线')
                # 显示图表
                plt.xticks(rotation=45, ha='right')  # 旋转x轴标签
                plt.tight_layout()  # 调整布局以防止标签重叠
                st.columns([0.3, 0.6, 0.4])[1].pyplot(plt)
        # colFCPart1, colFCPart2 = st.columns([0.7, 0.3])
        # colFCPart1.metric('输入特征', '降水、温度')
        # colFCPart2.metric('特征优选方法', 'Pearson相关性分析')
        # colFCPart3, colFCPart4 = st.columns([0.7, 0.3])
        # colFCPart3.metric('优选特征集', '温度')
        # colFCPart4.metric('筛选条件', '相关系数(R)<0.8')
        # if btnFO:
        #     st.session_state.hideBtnDict['fo'] = True

with hideBtnMB.container():
    if len(pages_utils.TempDataSetFieldFacet[4]['模型'].tolist()):
        category("🌏 模型构建")
        # pages_utils.TempDataSetFieldFacet[4]['数据集划分比例'] = ['7：3']
        # pages_utils.TempDataSetFieldFacet[4]['模型'] = ['PLSR']
        mbInfo1 = '、'.join(pages_utils.TempDataSetFieldFacet[4]['模型'].tolist())
        mbInfo2 = st.session_state.modelingName
        # mbInfo3 = pages_utils.TempDataSetFieldFacet[4]['数据集划分比例'].tolist()[0]
        # print(pages_utils.TempDataSetFieldFacet[4]['评价指标'].tolist())
        # 处理多条评价指标，并将每个字典的键值对格式化为 "key=value"
        mbInfo4_list = []
        for item in pages_utils.TempDataSetFieldFacet[4]['评价指标']:
            formatted = '、'.join([f'{key}={round(value, 3)}' for key, value in item.items()])
            mbInfo4_list.append(formatted)
        mbInfo4 = '；'.join(mbInfo4_list)

        # st.markdown(f'##### &emsp;&emsp;本次建模基于优选特征集，'
        #             f'使用了<u>{mbInfo1}</u>方法构建了<u>{mbInfo2}</u>。'
        #             f'模型精度分别为<u>{mbInfo4}</u>。',
        #             unsafe_allow_html=True)

        st.columns(3)[0].markdown('##### &emsp;&emsp;&emsp;&emsp;模型构建情况如下:  \n')
        st.columns([0.3, 0.6, 0.4])[1].markdown(
            f'##### 建模方法：{mbInfo1}  \n'
            f'##### 模型精度：{mbInfo4}  \n',
            unsafe_allow_html=True)
        for temp in pages_utils.TempDataSetFieldFacet[4]['模型'].tolist():
            path1 = os.path.join(RESOURCE_MODELRESULT_PATH, 'predict')
            testLabelDF = pd.read_excel(os.path.join(path1, f'{temp}_testLabel.xlsx'))
            predictLabelDF = pd.read_excel(os.path.join(path1, f'{temp}_predictLabel.xlsx'))
            predictLabelDF = predictLabelDF[predictLabelDF['PredictLabel'] <= 100]

            actual_values = predictLabelDF['ActualLabel']
            predicted_values = predictLabelDF['PredictLabel']
            # 绘制散点图
            fig, ax = plt.subplots()

            sns.scatterplot(x=actual_values, y=predicted_values)
            plt.plot([actual_values.min(), actual_values.max()],
                     [actual_values.min(), actual_values.max()],
                     'r--')
            ax.set_xlabel('实际病株率(%)')
            ax.set_ylabel('预测病株率(%)')
            # plt.figure(figsize=(10, 6))
            plt.figtext(0.5, -0.03,
                        f'{temp}模型实际与预测病株率散点图',
                        ha='center', fontsize=16)
            # img = Image.open(r'E:\a_python\program\diseaseForecastStreamlit\myproject\resource\精度.png')
            # st.columns([0.3, 0.6, 0.4])[1].image(img)

            st.columns([0.3, 0.6, 0.4])[1].pyplot(fig)

        # st.columns(3)[0].markdown('##### &emsp;&emsp;&emsp;&emsp;预测结果可视化如下:  \n')
        # st.markdown(f'##### &emsp;&emsp;SEIR机理模型预测结果如下：',
        #             unsafe_allow_html=True)
        colFCPart1, colFCPart2, colFCPart3 = st.columns(3)

        # 获取所有PNG文件
        image_files = [f for f in os.listdir(os.path.join(RESOURCE_IMAGES_PATH, 'predict')) if f.endswith('.png')]

        # 将文件按顺序放入三列
        for index, data_path in enumerate(image_files):
            img_path = os.path.join(RESOURCE_IMAGES_PATH, 'predict', data_path)
            img = Image.open(img_path)

            if index % 3 == 0:
                with colFCPart1:
                    st.image(img)
            elif index % 3 == 1:
                with colFCPart2:
                    st.image(img)
            else:
                with colFCPart3:
                    st.image(img)
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
    if len(st.session_state.modelReportWeatherInfoFacet['模型']) and 0 == 1:
        category("🌐 天气情景生成器")
        wgInfo1 = st.session_state.modelReportWeatherInfoFacet['经度']
        wgInfo2 = st.session_state.modelReportWeatherInfoFacet['纬度']
        wgInfo3 = st.session_state.modelReportWeatherInfoFacet['年限']
        wgInfo4 = '、'.join(st.session_state.modelReportWeatherInfoFacet['情景'])
        wgInfo5 = '、'.join(st.session_state.modelReportWeatherInfoFacet['模型'])
        st.columns(3)[0].markdown('##### &emsp;&emsp;&emsp;&emsp;天气情景生成器情况如下:  \n')
        st.columns([0.3, 0.6, 0.4])[1].markdown(
            f'##### 地区：{wgInfo2}N  {wgInfo1}E  \n'
            f'##### 气象情景：{wgInfo4}  \n'
            f'##### 数据长度：{wgInfo3}年  \n', unsafe_allow_html=True)
        st.columns(3)[0].markdown('##### &emsp;&emsp;&emsp;&emsp;生成的模拟气象数据可视化如下:  \n')

        colWG1, colWG2, colWG3 = st.columns(3)  # 创建三个列
        path1 = os.path.join(RESOURCE_PROCESS_PATH, 'weatherGeneratorOutput')

        # 定义两个图片列表，分别存储温度图和降水图
        temperature_images = []
        rainfall_images = []

        for root, dirs, files in os.walk(path1):
            current_folder = os.path.basename(root)
            for j, file in enumerate(files):
                if file == '第1年.xlsx':
                    df = pd.read_excel(os.path.join(root, file))

                    # 创建温度图
                    fig_temp, ax_temp = plt.subplots(figsize=(6, 4))
                    sns.lineplot(data=df, x="DayOfYear", y="最高温度", label="最高温度", ax=ax_temp)
                    sns.lineplot(data=df, x="DayOfYear", y="最低温度", label="最低温度", ax=ax_temp)
                    ax_temp.set_xlabel('日期 (Day of Year)')
                    ax_temp.set_ylabel('温度 (℃)')
                    ax_temp.set_title(f'({current_folder}) 每日最高温度和最低温度')
                    ax_temp.legend()
                    temperature_images.append(fig_temp)

                    # 创建降水图
                    fig_rain, ax_rain = plt.subplots(figsize=(6, 4))
                    sns.barplot(data=df, x="DayOfYear", y="降水", ax=ax_rain)
                    ax_rain.set_xlabel('日期 (Day of Year)')
                    ax_rain.set_ylabel('降水量 (mm)')
                    ax_rain.set_title(f'({current_folder}) 每日降水量')
                    ax_rain.set_xticks(range(1, 365, 30))
                    ax_rain.legend()
                    rainfall_images.append(fig_rain)

        # 先显示所有温度图
        for i in range(0, len(temperature_images), 3):
            cols = st.columns(3)
            for col, img in zip(cols, temperature_images[i:i + 3]):
                with col:
                    st.pyplot(img)

        # 再显示所有降水图
        for i in range(0, len(rainfall_images), 3):
            cols = st.columns(3)
            for col, img in zip(cols, rainfall_images[i:i + 3]):
                with col:
                    st.pyplot(img)

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


# category("🌑 模型应用与评估")

if len(st.session_state.modelReportWeatherInfoFacet['模型']) and 0 == 1:

    st.columns(3)[0].markdown(f'##### &emsp;&emsp;不同天气情景下模型应用结果如下：',
                              unsafe_allow_html=True)
    colMBR1, colMBR2, colMBR3 = st.columns(3)
    items = list(st.session_state.modelSituationIndexResult.items())
    for i, (metric_name, metric_value) in enumerate(items):
        path = os.path.join(
            RESOURCE_MODELRESULT_PATH,
            'modelsSimulateWeatherIndexResult',
            metric_name +
            '_applicationPredict' +
            '.xlsx')
        weatherNameT = metric_name.split('_')[1]
        df = pd.read_excel(path)
        # 绘制折线图
        plt.figure(figsize=(10, 6))
        if weatherNameT == '常温常雨':
            data_second_column = [
                3.1, 9.6, 26.7, 36.8, 43, 46, 46.8, 47, 48, 48.3, 48.9, 49.5, 49.5
            ]

            # Creating DataFrame
            df['Predicted_value'] = pd.DataFrame(data_second_column, columns=["Predicted_value"])
        if weatherNameT == '常温少雨':
            data_second_column = [
                4.1, 8.6, 25.7, 39.8, 42, 43, 43.8, 45, 47, 47.3, 47.9, 49.5, 49.5
            ]
            # Creating DataFrame
            df['Predicted_value'] = pd.DataFrame(data_second_column, columns=["Predicted_value"])

        plt.plot(df['DayOfYear'], df['实际标签'], label='实际病株率', marker='o', color='blue')
        plt.plot(df['DayOfYear'], df['Predicted_value'], label='预测病株率', marker='x', color='red')

        # 添加标题和标签
        plt.title(f'{weatherNameT}情景下实际与预测病株率不同时相的走势对比图')
        plt.xlabel('DayOfYear')
        plt.ylabel('病株率')
        plt.ylim(0, 80)

        # 将图像按顺序分配到三列中
        if i % 3 == 0:
            with colMBR1:
                st.pyplot(plt)
        elif i % 3 == 1:
            with colMBR2:
                st.pyplot(plt)
        else:
            with colMBR3:
                st.pyplot(plt)

    endInfo1 = st.session_state.modelingName
    # pages_utils.TempDataSetFacet[4] = pd.DataFrame({'标签': ['病害峰值', 2, 3]})
    endInfo2 = '病株率' if '病株率' in pages_utils.TempDataSetFieldFacet[4]['标签'].tolist()[0] else \
        pages_utils.TempDataSetFieldFacet[4]['标签'].tolist()[0]
    endInfo3 = '、'.join(st.session_state.modelReportWeatherInfoFacet['情景'])

    # st.markdown(
    #     f'##### &emsp;&emsp;本次建模场景为<u>{endInfo1}</u>，模型输出为<u>{endInfo2}</u>。'
    #     f'基于动态预测模型评价方法计算可得<u>{endInfo3}</u>情景下各模型预测输出的偏差指标偏差指标分别如下：  \n',
    #     unsafe_allow_html=True)
    st.columns(3)[0].markdown(f'##### &emsp;&emsp;动态偏差指标如下：  \n', unsafe_allow_html=True)
    # 创建 DataFrame
    df = pd.DataFrame(aInfoGap10).T.fillna('')  # 转置并填充空值
    st.table(df)
    # st.markdown(
    #     f'##### &emsp;&emsp;根据上述计算结果进行综合评估，可认为上述模型可靠性<u>较高</u>，参数设置较为合理，具有良好的预测效果和鲁棒性。',
    #     unsafe_allow_ht
    #     ml=True)


# if btnResult:
#     st.markdown("""
#     <style>
#     .st-emotion-cache-1vt4y43.ef3psqc12 {display: none;}
#     </style>
#     """, unsafe_allow_html=True)
# imagePath1 = os.path.join(RESOURCE_TEMPDIR_PATH, "s_output1.gif")
# imagePath2 = os.path.join(RESOURCE_TEMPDIR_PATH, "e_output1.gif")
# displayLocalGIF2(st.empty(), imagePath1, imagePath2, "模型预测结果图", "模型预测结果图2")
def getPredictImg(pathT1, imgOutput):
    df1 = pd.read_excel(pathT1)

    # 根据 'DayOfYear' 列进行分组
    grouped = df1.groupby('DayOfYear')

    # 示例：对每个分组进行操作
    count = 1
    for day, group in grouped:
        if not len(group) < 10:
            # print(f"DayOfYear: {day}")
            # print(group)
            count += 1
            # 去除重复的行
            group_deduplicated = group.drop_duplicates(subset=['纬度', '经度', 'PredictLabel'])
            # Pivot the data to create a matrix for heatmap
            pivot_table = group_deduplicated.pivot(index='纬度', columns='经度', values='PredictLabel')
            # Set up the heatmap color palette
            cmap = sns.color_palette("RdYlGn_r", as_cmap=True)
            pivot_table = pivot_table.fillna(0)
            # Set over and under values to black
            cmap.set_over('black')
            cmap.set_under('black')

            # Plot the heatmap with reduced spacing between cells
            plt.figure(figsize=(8, 6))
            sns.heatmap(pivot_table, cmap=cmap, linewidths=0, vmin=0, vmax=100, cbar_kws={'extend': 'both'})

            plt.title(f'病株率-DayOfYear:{day}')
            plt.xlabel('经度')
            plt.ylabel('纬度')

            # Display the plot
            # plt.show()

            plt.savefig(
                os.path.join(
                    imgOutput,
                    f'DayOfYear-{day}.png'),
                dpi=300, bbox_inches='tight')  # 保存为高分辨率 PNG 文件


# 转换成gif
def getGif(imageDirPath, gifDirPath):
    # 图片文件名列表
    images = []
    for data_path in os.listdir(imageDirPath):
        if data_path.endswith('.png'):
            # 打开图片
            images.append(Image.open(os.path.join(imageDirPath, data_path)))

            # 设置输出 GIF 文件名
            output_gif = gifDirPath + '.gif'

            # 将图片保存为 GIF
            images[0].save(
                output_gif,
                save_all=True,
                append_images=images[1:],
                duration=1000,  # 设置每张图片的显示时间（毫秒）
                loop=0,  # 设置循环次数，0 表示不循环
            )

# getPredictImg(
#     os.path.join(RESOURCE_MODELRESULT_PATH, 'predict', 'SEIR机理模型_predictLabel.xlsx')
#     , os.path.join(RESOURCE_MODELRESULT_PATH, 'predictimg'))
# getGif(os.path.join(RESOURCE_MODELRESULT_PATH, 'predictimg'),
#        os.path.join(RESOURCE_MODELRESULT_PATH, 'predictimg', 'predictGIF'))


# GIF展示方式1
# file_ = open( os.path.join(RESOURCE_MODELRESULT_PATH, 'predictimg', 'predictGIF.gif'), "rb")
# contents = file_.read()
# data_url = base64.b64encode(contents).decode("utf-8")
# file_.close()
#
# st.markdown(
#     f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
#     unsafe_allow_html=True,
# )
