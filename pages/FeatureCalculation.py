import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

from streamlit_tree_select import tree_select

import pages_utils

if 'page13' not in st.session_state: st.session_state.page13 = 0
if 'df12' not in st.session_state:
    st.session_state.df12 = pages_utils.FeatureDataSet


checkBoxNum = 5


def simulate_temperature_data():
    # 模拟生成温度数据
    data = {
        'City': ['City1', 'City2', 'City3'],
        'Temperature': np.append([
            np.random.normal(25, 5, 10),
            np.random.normal(20, 3, 10),
            np.random.normal(30, 7, 10)
        ])
    }
    df = pd.DataFrame(data)
    return df


# 取消所有选项按钮
def clear_all():
    for i in range(checkBoxNum):
        st.session_state[f'checkbox{i}'] = False
    return


# 取消其他选项按钮
def clear_other(key):
    for i in range(checkBoxNum):
        if i != key:
            st.session_state[f'checkbox{i}'] = False
    return


def nextPage():
    st.session_state["leftTabs"].append('被选特征')
    st.session_state.page13 += 1
    data11 = {"选择特征": False, "数据集": "气象数据", "特征": "降雨日数",
              "大小": '1*3', "处理方法": "降水累积量计算", "时间": '22:10:20',
              "下载数据集": True}
    data12 = {"选择特征": False, "数据集": "气象数据", "特征": "降水累积量",
              "大小": '1*5', "处理方法": "降水累积量计算", "时间": '22:10:21',
              "下载数据集": True}
    st.session_state.df12.loc[len(st.session_state.df12)] = data11
    st.session_state.df12.loc[len(st.session_state.df12)] = data12


# nodes = [
#     {"label": "气象数据", "value": "气象数据"},
#     {
#         "label": "植保数据",
#         "value": "植保数据",
#         "children": [
#             {"label": "feature1", "value": "sub_a"},
#             {"label": "feature2", "value": "sub_b"},
#             {"label": "feature3", "value": "sub_c"},
#         ],
#     },
#     {
#         "label": "农学数据",
#         "value": "folder_c",
#         "children": [
#             {"label": "晚稻移栽期", "value": "sub_d"},
#             {
#                 "label": "预测峰值",
#                 "value": "sub_e",
#                 "children": [
#                     {"label": "测报站点", "value": "sub_sub_a"},
#                     {"label": "生化指标", "value": "sub_sub_b"},
#                 ],
#             },
#             {"label": "生化指标", "value": "sub_f"},
#         ],
#     },
# ]
# nodes1 = [
#     {"label": "气象数据", "value": "气象数据"},
#     {
#         "label": "植保数据",
#         "value": "植保数据",
#         "children": [
#             {"label": "feature1", "value": "sub_a"},
#             {"label": "feature2", "value": "sub_b"},
#             {"label": "feature3", "value": "sub_c"},
#         ],
#     },
#     {
#         "label": "农学数据",
#         "value": "folder_c",
#         "children": [
#             {"label": "晚稻移栽期", "value": "sub_d"},
#             {
#                 "label": "预测峰值",
#                 "value": "sub_e",
#                 "children": [
#                     {"label": "测报站点", "value": "sub_sub4"},
#                     {"label": "生化指标", "value": "sub_s5"},
#                 ],
#             },
#             {"label": "生化指标", "value": "sub_f"},
#         ],
#     },
# ]
# nodes2 = [
#     {"label": "气象数据", "value": "气象数据"},
#     {
#         "label": "植保数据",
#         "value": "植保数据",
#         "children": [
#             {"label": "feature1", "value": "sub_4"},
#             {"label": "feature2", "value": "sub_3"},
#             {"label": "feature3", "value": "sub_2"},
#         ],
#     },
#     {
#         "label": "农学数据",
#         "value": "folder_c",
#         "children": [
#             {"label": "晚稻移栽期", "value": "sub_d"},
#             {
#                 "label": "预测峰值",
#                 "value": "sub_e",
#                 "children": [
#                     {"label": "测报站点", "value": "sub_sub_a"},
#                     {"label": "生化指标", "value": "sub_sub_b"},
#                 ],
#             },
#             {"label": "生化指标", "value": "sub_f"},
#         ],
#     },
# ]
# st.header('特征计算')
# st.markdown('---')
featureCCV, featureCCM = st.columns([0.5, 0.7])
with featureCCV:
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
                        height=720, width=800,
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
                        height=720, width=800,
                        column_config={
                            "选择字段": st.column_config.CheckboxColumn(
                                help="选择用于数据处理的字段",
                                default=False,
                            )
                        })
with featureCCM:
    # tab3, tab4 = st.tabs(["气象", "其他"])
    # with tab3:
    # st.subheader('气象')
    st.markdown("##### 特征计算方法")
    col1, col2 = st.columns(2)
    # st.dataframe(df.style.highlight_null(null_color='yellow'))
    with col1:
        option14 = st.checkbox('时间(温度)分辨率转换', key='checkbox0', on_change=clear_other, args=[0])
        option15 = st.checkbox('降雨日数计算', key='checkbox1', on_change=clear_other, args=[1])
        option16 = st.checkbox('降水累积量计算', key='checkbox2', on_change=clear_other, args=[2])
    with col2:
        option17 = st.checkbox('基于活动积温的生育期计算', key='checkbox3', on_change=clear_other, args=[3])
        option18 = st.checkbox('时空抽取', key='checkbox4', on_change=clear_other, args=[4])

    # with tab4:
    # st.subheader('其他')

    st.markdown('---')
    # st.markdown("##### 方法参数设置")
    if option14:
        option1 = st.selectbox(
            '分辨率转换',
            ('日值温度', '旬平均温度', '月平均温度'))
        # option2 = st.selectbox(
        #     '雨日数计算',
        #     ('月雨日数', '年雨日数'))
        # st.markdown('---')
    if option15:
        d1 = st.date_input("开始时间", value=None)
        d2 = st.date_input("结束时间", value=None)
        option = st.selectbox(
            '计算阈值方式',
            ('总降水量', '单日降水量'))
        if option == '总降水量':
            number1 = st.number_input("总降水量数值(mm)", value=100)
        if option == '单日降水量':
            number2 = st.text_input("单日降水量数值(mm)", value=0.1)
        number1 = st.number_input("连续降雨日数时长(天数)", value=1, min_value=1)
        # option2 = st.sidebar
        # st.markdown('---')
    if option16:
        option3 = st.selectbox(
            '降水累积量计算',
            ('日累积降水量', '旬累积降水量', '月累积降水量'))
        # st.markdown('---')
    if option17:
        # option5 = st.sidebar.selectbox(
        #     '地区',
        #     ('湘阴县', '桂阳县'))
        d1 = st.date_input("开始时间", value=None)
        d2 = st.date_input("结束时间", value=None)
        j4 = st.selectbox(
            '生育期',
            ('抽穗期', '孕穗期'))
        if j4 == '抽穗期':
            number = st.number_input(
                "积温阈值温度(50-300℃)", value=50, step=50,
                min_value=50, max_value=300)
        if j4 == '孕穗期':
            number = st.number_input(
                "积温阈值温度(50-300℃)", value=100, step=50,
                min_value=50, max_value=300)
        # st.markdown('---')

    if option18:
        # st.sidebar.
        option = st.selectbox(
            '抽取因子',
            ('降水', '温度'))
        # option6 = st.selectbox(
        #     '时空抽取-地区',
        #     ('湘阴县', '桂阳县'))
        option4 = st.selectbox(
            '计算方式',
            ('平均值', '累积值'))
        j3 = st.selectbox(
            '起始日期',
            ('基于活动积温的生育期计算', '指定日期'))
        if j3 == '指定日期':
            d3 = st.date_input("起始日期", value=None, label_visibility='collapsed')
        if j3 == '基于活动积温的生育期计算':
            pass
        d4 = st.date_input("结束日期", value=None)
        number1 = st.number_input("步长(天)", value=1, min_value=1)
        # st.markdown('---')
    interval_col1, interval_col2 = st.columns([5, 1])
    btn = interval_col2.button('保存', on_click=clear_all)
    if btn:
        # update dataframe state
        # st.markdown(type(st.session_state.df))
        new_data = {"数据集": "气象数据", "输入特征": "温度", "输出特征": "旬平均温度",
                    "特征计算方法": "时间(温度)分辨率转换", "时间": '22:20:20'}
        st.session_state.df2.loc[len(st.session_state.df2)] = new_data
        st.rerun()
    st.markdown('---')
    data = pd.DataFrame(columns=["数据集", "输入特征", "输出特征", "特征计算方法", '时间'])
    # with every interaction, the script runs from top to bottom
    # resulting in the empty dataframe
    if 'df2' not in st.session_state:
        st.session_state.df2 = data
    placeholder = st.empty()
    if st.session_state.page13 == 0:
        with placeholder.container():
            st.markdown('##### 任务清单')
            edited_df28 = st.data_editor(
                st.session_state.df2, height=190, width=800,
                disabled=["数据集", "特征", "时间"],
                num_rows="dynamic")
            interval_col34, interval_col33 = st.columns([5, 1])
            btn2 = interval_col33.button('运行', on_click=nextPage)
    elif st.session_state.page13 == 1:
        with placeholder.container():
            st.markdown('##### 可视化')
            tab1, tab2 = st.tabs(["1", "2"])
            with tab1:
                precipitation_data = np.random.normal(50, 10, 20)
                chart_data = pd.DataFrame({
                    "Precipitation": precipitation_data,
                    "月份": np.arange(1, 21),  # 月份从1到20
                    "图例": np.random.randint(1, 5, 20)  # 随机生成图例数据
                })
                st.vega_lite_chart(
                    chart_data,
                    {
                        "mark": {"type": "circle", "tooltip": True},
                        "encoding": {
                            "x": {"field": "月份", "type": "quantitative"},
                            "y": {"field": "Precipitation", "type": "quantitative"},
                            "size": {"field": "图例", "type": "quantitative"},
                            "color": {"field": "图例", "type": "quantitative"},
                        },
                    },
                )
            with tab2:
                pass

                # df = simulate_temperature_data()
                # # 创建子图和轴
                # fig, ax = plt.subplots()
                # # 使用Seaborn的barplot生成柱状图
                # sns.barplot(x='City', y='Temperature', data=df, ax=ax)
                # # 设置图形标题
                # plt.title('Barplot of Temperature Data')
                # st.pyplot(fig)
# with featureCCR:
#     tabb2, tabb3 = st.tabs(['可视化', '历史记录及数据下载'])
# with tabb1:
#     st.markdown('##### 数据摘要')
#     col111, col222 = st.columns(2)
#
#     with col111:
#         st.markdown('特征名称:温度')
#         st.markdown('类型:整数')
#         st.markdown('个数:19')
#         st.markdown('最小值:50')
#         st.markdown('最大值:100')
#     with col222:
#         st.data_editor(pd.DataFrame(
#             data={
#                 "温度": [1, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4],
#             }
#         ), height=190)
# with tabb2:
#     st.subheader('展示数据处理前与处理后的图表')
#     t1, t2 = st.columns(2)
#     with t1:
#         st.image('resource/image/0.png')
#     with t2:
#         st.image('resource/image/1.png')
# with tabb3:
#     st.markdown('###### 历史记录')
#     df = pd.DataFrame(
#         {
#             "数据集": ["气象数据", "植保数据", "农学数据"],
#             "特征": ["降雨日数", "基于活动积温的生育期", "预测峰值"],
#             "大小": ["1*3", "1*6", "1*5"],
#             '处理方法': ['时间分辨率转换', '降雨日数计算', '降水累积量计算'],
#             "时间": ['22:10:20', '20:10:20', '21:10:20'],
#         }
#     )
#     edited_df = st.data_editor(df)
#     st.markdown('---')
#     st.markdown('###### 数据下载')
#     option = st.selectbox(
#         '历史记录编号',
#         (1, 2, 3))
#     pages_utils.multiselect_all(st, ['气温', '降雨日数', '生育期'], '特征',"collapsed")
#     interval_col13, interval_col12 = st.columns([5, 1])
#     interval_col12.button('下载')
