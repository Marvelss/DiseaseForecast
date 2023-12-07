import streamlit as st
import numpy as np
import pandas as pd
from st_pages import add_page_title
from streamlit_tree_select import tree_select

from pages_utils import multiselect_all
from streamlit_modal import Modal

nodes = [
    {"label": "气象数据", "value": "folder_a"},
    {
        "label": "植保数据",
        "value": "folder_b",
        "children": [
            {"label": "feature1", "value": "sub_a"},
            {"label": "feature2", "value": "sub_b"},
            {"label": "feature3", "value": "sub_c"},
        ],
    },
    {
        "label": "农学数据",
        "value": "folder_c",
        "children": [
            {"label": "晚稻移栽期", "value": "sub_d"},
            {
                "label": "预测峰值",
                "value": "sub_e",
                "children": [
                    {"label": "测报站点", "value": "sub_sub_a"},
                    {"label": "生化指标", "value": "sub_sub_b"},
                ],
            },
            {"label": "生化指标", "value": "sub_f"},
        ],
    },
]

st.header('特征提取')
# st
# tab3, tab4 = st.columns(2)
tab3, tab4 = st.tabs(["气象", "其他"])
with tab3:
    # st.subheader('气象')
    option14 = st.checkbox('时间(温度)分辨率转换')
    option15 = st.checkbox('降雨日数计算')
    option16 = st.checkbox('降水累积量计算')
    if option14:
        option1 = st.sidebar.selectbox(
            '分辨率转换',
            ('日值温度', '旬平均温度', '月平均温度'))
    # option2 = st.selectbox(
    #     '雨日数计算',
    #     ('月雨日数', '年雨日数'))
    if option15:
        d1 = st.sidebar.date_input("开始时间", value=None)
        d2 = st.sidebar.date_input("结束时间", value=None)
        option = st.sidebar.selectbox(
            '计算阈值方式',
            ('总降水量', '单日降水量'))
        if option == '总降水量':
            number1 = st.sidebar.number_input("总降水量数值(mm)", value=100)
        if option == '单日降水量':
            number2 = st.sidebar.text_input("单日降水量数值(mm)", value=0.1)
        number1 = st.sidebar.number_input("连续降雨日数时长(天数)", value=1, min_value=1)
        # option2 = st.sidebar
    if option16:
        option3 = st.sidebar.selectbox(
            '降水累积量计算',
            ('日累积降水量', '旬累积降水量', '月累积降水量'))

with tab4:
    # st.subheader('其他')
    option17 = st.checkbox('基于活动积温的生育期计算')
    option18 = st.checkbox('时空抽取')
    if option17:
        # option5 = st.sidebar.selectbox(
        #     '地区',
        #     ('湘阴县', '桂阳县'))
        d1 = st.sidebar.date_input("开始时间", value=None)
        d2 = st.sidebar.date_input("结束时间", value=None)
        j4 = st.sidebar.selectbox(
            '生育期',
            ('抽穗期', '孕穗期'))
        if j4 == '抽穗期':
            number = st.sidebar.number_input(
                "积温阈值温度(50-300℃)", value=50, step=50,
                min_value=50, max_value=300)
        if j4 == '孕穗期':
            number = st.sidebar.number_input(
                "积温阈值温度(50-300℃)", value=100, step=50,
                min_value=50, max_value=300)

    if option18:
        # st.sidebar.
        option = st.sidebar.selectbox(
            '抽取因子',
            ('降水', '温度'))
        # option6 = st.selectbox(
        #     '时空抽取-地区',
        #     ('湘阴县', '桂阳县'))
        option4 = st.sidebar.selectbox(
            '计算方式',
            ('平均值', '累积值'))
        j3 = st.sidebar.selectbox(
            '起始日期',
            ('基于活动积温的生育期计算', '指定日期'))
        if j3 == '指定日期':
            d3 = st.sidebar.date_input("起始日期", value=None, label_visibility='collapsed')
        if j3 == '基于活动积温的生育期计算':
            pass
        d4 = st.sidebar.date_input("结束日期", value=None)
        number1 = st.sidebar.number_input("步长(天)", value=1, min_value=1)

    # with st.expander("活动积温计算"):
    #     option5 = st.selectbox(
    #         '地区',
    #         ('湘阴县', '桂阳县'))
    #     d1 = st.date_input("开始时间", value=None)
    #     d2 = st.date_input("结束时间", value=None)
    #     number = st.number_input("积温阈值温度(50-300℃)", value=50, step=50,
    #                              min_value=50, max_value=300)
    #
    # with st.expander("时空抽取"):
    #     option = st.selectbox(
    #         '抽取因子',
    #         ('降水', '温度'))
    #     # option6 = st.selectbox(
    #     #     '时空抽取-地区',
    #     #     ('湘阴县', '桂阳县'))
    #     option4 = st.selectbox(
    #         '计算方式',
    #         ('平均值', '累积值'))
    #     d3 = st.date_input("生育期", value=None)
    #     number1 = st.number_input("步长(天)", value=1, min_value=1)
st.markdown('---')
st.subheader('展示数据处理前与处理后的图表')
t1, t2 = st.columns(2)
with t1:
    st.image('resource/image/0.png')
with t2:
    st.image('resource/image/1.png')
st.markdown('---')
st.subheader('特征优选')
st.markdown("##### 因子选择")
value_list = ['气温', '降水', '病害峰值', '地区']
multiselect_all(st, value_list, '特征因子选择')
# st.markdown('---')
# st.write('You selected:', options)
st.markdown("##### 分析方法")
# tab1, tab2 = st.tabs(["单因子敏感性分析", "多因子组合优化"])
colt1, colt2 = st.columns(2)
with colt1:
    tab1, tab2 = st.tabs(["单因子敏感性分析", "多因子组合优化"])
    with tab1:
        genre = st.radio(
            label="",
            label_visibility="collapsed",
            options=["Person相关性分析", "t检验"],
            # captions=["t检验", "Person相关性分析"]
        )
    # btn1 = st.button('预览')
    if genre == 't检验':
        st.sidebar.markdown('提取条件')
        genre2 = st.sidebar.radio(
            label='',
            horizontal=True,
            label_visibility="collapsed",
            options=['p-value<0.001', 'p-value<0.005', 'p-value<0.01']
        )
    with tab2:
        # st.markdown('多因子组合优化')
        genre1 = st.radio(
            label="",
            label_visibility="collapsed",
            options=['', "Relief-F互相关分析"],
            # captions=["t检验", "Person相关性分析"]
        )
        if genre1 == 'Relief-F互相关分析':
            # st.markdown('提取条件')
            option = st.sidebar.selectbox(
                '提取条件',
                ('按百分比选取', '按权重值计算'))
            if option == '按百分比选取':
                number1 = st.sidebar.number_input("TOP(%)", value=5, min_value=5, step=5)
            if option == '按权重值计算':
                number2 = st.sidebar.number_input("权重阈值", value=10, min_value=10)

        # btn2 = st.button('提取')

with colt2:
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["p-value", "月份", "图例"])

    st.vega_lite_chart(
        chart_data,
        {
            "mark": {"type": "circle", "tooltip": True},
            "encoding": {
                "x": {"field": "月份", "type": "quantitative"},
                "y": {"field": "p-value", "type": "quantitative"},
                "size": {"field": "图例", "type": "quantitative"},
                "color": {"field": "图例", "type": "quantitative"},
            },
        },
    )
btn2 = st.sidebar.button('运行')
st.sidebar.button('添加')

# st.sidebar.subheader('参数设置')
# option8 = st.sidebar.selectbox(
#     '分辨率',
#     ('日值温度', '旬平均温度', '月平均温度'))
# st.sidebar.button('运行', on_click='')
# st.sidebar.button('预览')
