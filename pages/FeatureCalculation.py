import streamlit as st

from streamlit_tree_select import tree_select

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
st.header('特征计算')
st.markdown('---')
featureCCV, featureCCM, featureCCR = st.columns([0.3, 0.7, 0.7])
with featureCCV:
    st.markdown("##### 变量")
    tree_select(nodes)
with featureCCM:
    tab3, tab4 = st.tabs(["气象", "其他"])
    with tab3:
        # st.subheader('气象')
        option14 = st.checkbox('时间(温度)分辨率转换')
        option15 = st.checkbox('降雨日数计算')
        option16 = st.checkbox('降水累积量计算')
    with tab4:
        # st.subheader('其他')
        option17 = st.checkbox('基于活动积温的生育期计算')
        option18 = st.checkbox('时空抽取')
    st.markdown('---')
    st.markdown("##### 参数设置")
    if option14:
        option1 = st.selectbox(
            '分辨率转换',
            ('日值温度', '旬平均温度', '月平均温度'))
    # option2 = st.selectbox(
    #     '雨日数计算',
    #     ('月雨日数', '年雨日数'))
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
    if option16:
        option3 = st.selectbox(
            '降水累积量计算',
            ('日累积降水量', '旬累积降水量', '月累积降水量'))
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
    st.button('运行')
with featureCCR:
    tabb1, tabb2 = st.tabs(['结果', '可视化'])
    with tabb1:
        st.json(({
            '气象数据': {
                'type': 'feature',
                'count': '2',
                '降雨日数': {
                    'type': 'int',
                    'count': '1',
                    'value': 10
                },
                '月累积降水量': {
                    'type': 'int',
                    'count': '5',
                    'value': [
                        '10',
                        '100',
                        '110',
                        '120',
                        '120'
                    ]
                }
            }}))
    with tabb2:
        st.subheader('展示数据处理前与处理后的图表')
        t1, t2 = st.columns(2)
        with t1:
            st.image('resource/image/0.png')
        with t2:
            st.image('resource/image/1.png')
