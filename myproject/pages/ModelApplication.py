import os.path
import tempfile

import joblib
import streamlit as st
import pandas as pd
from st_pages import hide_pages
from lib.share import RESOURCE_MODELRESULT_PATH
from pages.modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod
import streamlit_antd_components as sac
from pages import pages_utils
import leafmap.foliumap as leafmap
from lib.utils import excelToJson, filterUnique

st.set_page_config(
    layout="wide",
    initial_sidebar_state='collapsed'
)
# 隐藏页面
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
        "模型应用-面状",
        "数据下载中心-面状",
    ]
)

st.header('多场景作物病虫害快速预测建模系统')
emptyHeadFCP = st.empty()

# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr2 {display: none;}
    </style>
    """, unsafe_allow_html=True)

sac.steps(
    items=[
        sac.StepsItem(title='原始建模数据', subtitle='',
                      description='上传建模数据集', disabled=True),
        sac.StepsItem(title='气象数据预处理',
                      disabled=True,
                      description='清洗气象数据如异常和缺失值，以免影响建模'),
        sac.StepsItem(title='特征计算', disabled=True,
                      description='提取相关特征，增强模型表现'),
        sac.StepsItem(title='特征优选', disabled=True,
                      description='筛选有用特征，提升训练质量'),
        sac.StepsItem(title='模型构建', disabled=True,
                      description='训练并验证模型'),
        sac.StepsItem(title='模型应用', disabled=True,
                      description='应用模型进行作物病虫害预测'),
    ], index=5, color='#008000'
)

# colTemp1, colTemp2, colTemp3 = st.columns([0, 0.8, 0])
# with colTemp1:
#     pass
# with colTemp3:
#     pass
# with colTemp2:
col2, col3 = st.columns([0.6, 0.4])
with col2:
    # 默认获取最优模型进行应用
    st.markdown("##### 加载模型(已默认选用精度最优模型)")
    best_model = None
    best_oa = -float('inf')
    best_kappa = -float('inf')
    if pages_utils.TempDataSetField[4]['模型'].tolist():
        for idx, row in pages_utils.TempDataSetField[4].iterrows():
            metrics = row['评价指标']  # 提取评价指标
            if not isinstance(metrics, dict):  # 确保是字典
                metrics = eval(metrics)
            oa = metrics.get('OA', 0)
            kappa = metrics.get('Kappa', 0)

            # 优先比较 OA
            if oa > best_oa or (oa == best_oa and kappa > best_kappa):
                best_oa = oa
                best_kappa = kappa
                best_model = row['模型']  # 假设模型列存在

        # 输出最优精度和对应的模型
        print("最优模型:", best_model)
        print("最优OA:", best_oa)
        print("最优KAPPA:", best_kappa)
        tempModels = pages_utils.TempDataSetField[4]['模型'].tolist()
        tempModels.remove(best_model)
        tempModels.insert(0, best_model)
        # 默认最优模型放置第一个
        st.selectbox('加载模型',
                     options=tempModels,
                     label_visibility='collapsed')
        model = joblib.load(
            os.path.join(RESOURCE_MODELRESULT_PATH, 'structure',
                         f'{best_model}_structure.pkl'))
    st.markdown("##### 清单列表")
    st.data_editor(
        pages_utils.TempDataSetField[4], height=274, width=1200, use_container_width=True,
        column_order=["模型", "标签", "特征", "评价指标", "数据集划分比例", "时间"],
        disabled=["时间", '处理状态'], num_rows="fixed", )
with col3:
    st.markdown("##### 上传数据")
    uploaded_dataSet = st.file_uploader(
        "输入原始字段",
        accept_multiple_files=False,
        label_visibility='collapsed')
    # 获取特征字段
    # feature_names = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else None
    # st.info(f"模型输入特征:{'、'.join(feature_names)}")

    warningInfo1 = '''
    注意事项
    1. 根据提供的模板填充数据，将该数据上传后，系统自动输入已训练的模型，完成目标变量的预测;

    2. 上传内容应为未来数据，其中气象数据量至少一年以上，并确保无缺失值
    '''

    # 下载模板
    if model:
        # 创建一个 DataFrame，其中包含特征字段作为表头
        # 创建一个 DataFrame，其中包含特征字段作为表头
        weatherNameT0, plantNameT0, agricultureNameT0 = pages_utils.getDataFiled(0, pages_utils.TempDataSetField[0])
        tempColumns = ['经度', '纬度', '年', 'DayOfYear'] + filterUnique(
            pages_utils.TempDataSet[0].columns,
            plantNameT0 + ['DayOfYear'])
        df = pd.DataFrame(columns=tempColumns)

        # 将 DataFrame 保存为 Excel 文件
        file_path = "features.xlsx"  # 文件路径可以根据需要调整
        # df.to_excel(file_path, index=False)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        # 将 DataFrame 保存到临时文件中
        df.to_excel(tmp.name, index=False)
        # 获取临时文件的路径
        file_path = tmp.name

    # 使用 Streamlit 提供下载按钮
    st.markdown("##### 模型应用数据模板下载")
    st.warning(warningInfo1, icon="⚠️")

    with open(file_path, "rb") as file:
        st.download_button(
            label="模板下载",
            data=file,
            file_name="模型应用数据模板.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# st.table(dataFrameTemp)

# 地图可视化
# 获取经度和纬度的最小值和最大值
# min_longitude = dataFrameTemp["经度"].min()
# max_longitude = dataFrameTemp["经度"].max()
# min_latitude = dataFrameTemp["纬度"].min()
# max_latitude = dataFrameTemp["纬度"].max()
# geoJsonPredict = excelToJson(dataFrameTemp, '经度', '纬度', '预测结果')
# # m = leafmap.Map(center=[30.314207, 120.343200], zoom_start=16)
# m = leafmap.Map(zoom_start=16)
# m.add_basemap('SATELLITE')
#
# m.add_geojson(geoJsonPredict, layer_name="模型应用结果")
# m.to_streamlit()

if uploaded_dataSet:
    st.markdown("##### 预测结果")
    bytes_data = uploaded_dataSet.read()
    modelApplicationData = pd.read_excel(bytes_data)

    # 自动模型应用
    # 获取原始上传数据
    dataFrameTemp = modelApplicationData
    # dataFrameTemp.to_excel('原始书.xlsx', index=False)
    # print(dataFrameTemp)
    # 自动计算特征
    # ===============计算月、旬===============
    # 计算旬、月、年内日期和日期字段
    dataFrameTemp['日期'] = pd.to_datetime(
        dataFrameTemp['年'].astype(str) + dataFrameTemp['DayOfYear'].astype(str), format='%Y%j')
    dataFrameTemp['年内日期'] = dataFrameTemp['日期'].dt.strftime('%m-%d')
    # 提取月份
    dataFrameTemp['月'] = dataFrameTemp['日期'].dt.month
    # 计算每天所在的旬，假设1-10日为第一旬，11-20日为第二旬，21日至月末为第三旬
    dataFrameTemp['旬'] = dataFrameTemp['日期'].dt.day.apply(FeatureCalculationMethod.get_decade)

    # ===============获取特征计算任务清单内容===============

    predictDF = None
    fields = pages_utils.TempDataSetField[2]["输入特征"].tolist()
    methodParam = pages_utils.TempDataSetField[2]["方法参数"].tolist()
    methodList = pages_utils.TempDataSetField[2]["特征计算方法"].tolist()

    with emptyHeadFCP:
        with st.spinner('处理数据中...'):
            afterHandleData = None
            newColumn = '错误'
            # ===============根据名称匹配调用并执行各个处理方法===============
            # 初始化特征计算方法
            # methodTool = FeatureCalculationMethod(
            #     pages_utils.TempDataSet[1],
            #     reservedField + outFields)
            for indexT, tempMethod in enumerate(methodList):
                # 使用处理后最新的字段内容
                reservedField = pages_utils.TempDataSet[1].columns.tolist()
                # print(f'=============测试保留字段-{reservedField}=============')
                if tempMethod == '时间(温度)分辨率转换':
                    pass
                elif tempMethod == '降雨日数计算':
                    afterHandleData, newColumn = FeatureCalculationMethod(
                        dataFrameTemp, reservedField).rainfallDaysAccumulation(
                        fields[indexT], methodParam[indexT])
                elif tempMethod == '降水累积量计算':
                    afterHandleData, newColumn = FeatureCalculationMethod(
                        dataFrameTemp, reservedField).precipitationAccumulation(
                        fields[indexT], methodParam[indexT])
                elif tempMethod == '基于活动积温的生育期计算':
                    afterHandleData, newColumn = FeatureCalculationMethod(
                        dataFrameTemp, reservedField).growthPeriodCalculation(
                        fields[indexT], methodParam[indexT])
                elif tempMethod == '气象指标均值计算':
                    afterHandleData, newColumn = FeatureCalculationMethod(
                        dataFrameTemp, reservedField).meteorologicalMeanAccumulation(
                        fields[indexT], methodParam[indexT])
                elif tempMethod == '活动积温计算':
                    afterHandleData, newColumn = FeatureCalculationMethod(
                        dataFrameTemp, reservedField).activeAccumulatedTemperature(
                        fields[indexT], methodParam[indexT])
                # afterHandleData.to_excel(f'处理{tempMethod}.xlsx')
                # ===============合并处理后数据集===============
                row_size = len(afterHandleData)
                intersection_cols = pages_utils.getIntersectionCols(
                    dataFrameTemp, afterHandleData
                )
                dataFrameTemp = pd.merge(
                    afterHandleData, dataFrameTemp,
                    on=intersection_cols, how="left")
                st.toast(f"完成{tempMethod}计算", icon="ℹ️️")

    # 保留优选特征
    # dataFrameTemp.to_excel('计算完特征.xlsx')
    dataFrameTemp = dataFrameTemp[['经度', '纬度', '年'] + st.session_state.preferenceFeature]
    # dataFrameTemp.to_excel('计算完特征并删减.xlsx')
    # 提取非空值
    dataFrameTemp = dataFrameTemp.groupby(['经度', '纬度', '年']).first().reset_index()
    # dataFrameTemp.to_excel('提取非空值.xlsx')
    # 去重
    dataFrameTemp = dataFrameTemp.drop_duplicates()
    # dataFrameTemp.to_excel('去重.xlsx')
    predictDF = dataFrameTemp[pages_utils.TempDataSetField[4]['特征'][0]]
    # predictDF.to_excel('输入.xlsx')

    predictions = model.predict(predictDF)
    dataFrameTemp['预测结果'] = predictions
    st.toast(f"模型应用完成", icon="ℹ️️")
    st.dataframe(dataFrameTemp, use_container_width=True)

    # dem = r'E:\a_python\program\diseaseForecastStreamlit\myproject\resource\tempdir\CHN_Wheat_2010.tif'
    # m = leafmap.Map(zoom_start=16)
    # m.add_basemap('SATELLITE')
    #
    # m.add_raster(dem, cmap='RdYlGn', layer_name="DEM", nodata=0, attribution='由杭电数字农业团队提供')
    # m.add_colorbar(
    #     cmap="terrain",
    #     vmin=0,
    #     vmax=1,
    #     label="Elevation (m)",
    #     position="bottom-right",
    #     width=1,
    #     height=3,
    #     orientation="vertical", colors=["red", 'yellow', 'blue']
    # )
    # m.to_streamlit()
