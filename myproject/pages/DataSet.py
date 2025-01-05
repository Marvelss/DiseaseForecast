# page2.py
import os.path
from datetime import datetime

import pandas as pd
import streamlit as st
from st_pages import hide_pages
import streamlit_antd_components as sac

from lib.share import RESOURCE_TEMPLATE_PATH, RESOURCE_TEMPDIR_PATH
from pages import pages_utils
from streamlit_pills import pills
from warnings import simplefilter

simplefilter(action="ignore", category=FutureWarning)
st.set_page_config(
    layout="wide"
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
# 取消链接跳转
st.markdown("""
    <style>
    .st-emotion-cache-gi0tri.e1nzilvr2 {display: none;}
    </style>
    """, unsafe_allow_html=True)
st.markdown(("""
<style>
div.stButton button {
    border-radius: 0;
}
</style>
"""), unsafe_allow_html=True)
if 'page12' not in st.session_state:
    st.toast('请先跳转至主页进行系统初始化', icon="⚠️")

# 模型应用数据
if 'modelApplicationData' not in st.session_state:
    st.session_state.modelApplicationData = None
# 模板路径及注释信息
path1 = os.path.join(RESOURCE_TEMPLATE_PATH, '气象数据-模板.xlsx')
path2 = os.path.join(RESOURCE_TEMPLATE_PATH, '植保数据-模板.xlsx')
path3 = os.path.join(RESOURCE_TEMPLATE_PATH, '地理遥感数据-模板.xlsx')

warningInfo = '''
注意事项
1. 先上传气象数据，后上传植保等其他数据

2. 建议建模数据中植保数据量大于50条，以免影响模型的稳定性
3. 请将数据中的文字描述转为数字，如病害发生程度，若为健康输入0，轻度输入1，重度输入2
4. 模版中表头行不可删除，且字段名称不能包含 '-' , '_' 和数字字符;
5. 删除示例数据后,按需填充或删减字段与数据.
6. 完成数据添加后，删除注意事项两行单元格，并对数据检查，保证无大面积缺失和异常情况，以免影响建模.
'''


st.markdown(
    """
    <style>
    h2 {
        margin-top: -100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.header('多场景作物病虫害快速预测建模系统')
sac.steps(
    items=[
        sac.StepsItem(title='数据集', subtitle='extra msg', description='description text', disabled=True),
        sac.StepsItem(title='气象数据预处理', disabled=True),
        sac.StepsItem(title='特征计算', disabled=True),
        sac.StepsItem(title='特征优选', disabled=True),
        sac.StepsItem(title='模型构建', disabled=True),
        sac.StepsItem(title='模型应用', disabled=True),
    ], index=0
)
# st.markdown("<h1 style='text-align: left; color: red;'>Some title</h1>", unsafe_allow_html=True)

emptyHeadDSP = st.empty()
# ==============================文件上传显示==============================
dataSCM, dataSCR = st.columns([0.7, 0.4])
with dataSCM:
    st.markdown("##### 上传数据集")
    selectedTemplate = pills("选择数据集", ['气象数据', '植保数据', '地理遥感数据'],
                             ["🌨️️", "🌾", "🌎"])

    uploaded_files = st.file_uploader(
        "上传数据集",
        accept_multiple_files=False,
        label_visibility='collapsed',
        type=['xlsx', 'csv', 'txt', 'xls', 'zip'],
        help='help')

    # st.markdown('''
    #     <style>
    #         .uploadedFile {display: none}
    #     <style>''',
    #             unsafe_allow_html=True)

    st.markdown('---')
    # ==============================右侧数据模板下载及注意事项==============================
    st.markdown("##### 数据模板下载及注意事项")
    placeholder1 = st.empty()
    if selectedTemplate == '气象数据':
        with placeholder1.container():
            st.warning(warningInfo, icon="⚠️")
            with open(path1, "rb") as file:
                st.download_button(
                    label="下载气象数据模板",
                    data=file,
                    file_name="气象数据-模板.xlsx",
                    mime="application/octet-stream"
                )
    if selectedTemplate == '植保数据':
        with placeholder1.container():
            st.warning(warningInfo, icon="⚠️")
            with open(path2, "rb") as file:
                st.download_button(
                    label="下载植保数据模板",
                    data=file,
                    file_name="植保数据-模板.xlsx",
                    mime="application/octet-stream"
                )
    if selectedTemplate == '地理遥感数据':
        with placeholder1.container():
            st.warning(warningInfo, icon="⚠️")
            with open(path3, "rb") as file:
                st.download_button(
                    label="下载地理遥感数据模板",
                    data=file,
                    file_name="地理遥感数据-模板.xlsx",
                    mime="application/octet-stream"
                )

    # if selectedTemplate == '模型应用数据':
    #     with placeholder1.container():
    #         st.warning(warningInfo1, icon="⚠️")
    #         with open(path3, "rb") as file:
    #             st.download_button(
    #                 label="下载模型应用数据模板",
    #                 data=file,
    #                 file_name="模型应用数据-模板.xlsx",
    #                 mime="application/octet-stream"
    #             )
    # ==============================控制文件上传逻辑==============================
    with emptyHeadDSP:
        with st.spinner('处理数据中...'):
            if uploaded_files:
                # print(uploaded_files)
                try:
                    bytes_data = uploaded_files.read()
                    data33 = pd.read_excel(bytes_data)
                    # # 设定保存路径
                    # save_path = f"./{uploaded_files.name}"
                    #
                    # # 将文件保存到本地
                    # with open(save_path, "wb") as f:
                    #     f.write(bytes_data)
                    #
                    # st.success(f"文件已保存到: {save_path}")
                    isErrorData = False
                    # 检测非数值型输入
                    # 取前10行
                    subset = data33.head(10)

                    # 检测每一列是否包含非数值型数据，并显示对应的列名
                    non_numeric_columns = []

                    for column in subset.columns:
                        non_null_data = subset[column].dropna()
                        if not pd.to_numeric(non_null_data, errors='coerce').notna().all():
                            non_numeric_columns.append(column)
                    # 去除经度、纬度(固定)
                    tempT1 = [col for col in non_numeric_columns if col not in ['经度', '纬度']]

                    # 防止重复添加
                    if (pages_utils.TempDataSetField[0]['文件名称'] == uploaded_files.name).any():
                        pass
                    # 存在非数值型输入
                    elif len(tempT1):
                        tempT2 = ' '.join(tempT1)
                        st.toast(f'以下列存在非数值型数据,请转换为数值后重新上传  \n字段:{tempT2}', icon="⚠️")
                    # 正确情况
                    else:
                        new_data = {
                            "编号": pages_utils.generateID(),
                            "数据类型": selectedTemplate, "文件名称": uploaded_files.name, "传输状态": "已上传",
                            "上传时间": datetime.now().strftime("%H:%M:%S"),
                            "字段": data33.columns.tolist()}
                        # 添加并合并至原始数据集
                        pages_utils.TempDataSetField[0].loc[len(pages_utils.TempDataSetField[0])] = new_data
                        # 若为模型应用数据，不合并
                        if selectedTemplate == '模型应用数据':
                            pass
                            # st.session_state.modelApplicationData = data33
                        else:
                            # 获取两个DataFrame列名的交集
                            intersection_cols = pages_utils.getIntersectionCols(
                                data33, pages_utils.TempDataSet[0]
                            )
                            # 合并数据
                            pages_utils.TempDataSet[0] = pd.merge(
                                data33, pages_utils.TempDataSet[0],
                                on=intersection_cols, how="outer")
                # 上传出错提示
                except BaseException as e:
                    st.toast('上传错误  \n请检查文件内容及格式无误后重新上传', icon="⚠️")
                    print(e)
                    # new_data = {
                    #     "编号": pages_utils.generateID(),
                    #     "数据类型": selectedTemplate, "文件名称": uploaded_files.name, "传输状态": "上传出错",
                    #     "上传时间": datetime.now().strftime("%H:%M:%S"),
                    #     "字段": '未识别'}
                    # pages_utils.TempDataSetField[0].loc[len(pages_utils.TempDataSetField[0])] = new_data
                print('======================原始数据集======================')
                print(pages_utils.TempDataSet[0])
# ==============================右侧文件上传状态显示==============================
with dataSCR:
    st.markdown("##### 文件上传状态显示")
    placeholder = st.empty()
    with placeholder.container():
        st.data_editor(
            pages_utils.TempDataSetField[0], height=390, width=800,
            disabled=["数据集", "文件名称", "传输状态", "上传时间"],
            column_order=["数据类型", "文件名称", "传输状态", "上传时间"],
            hide_index=False, )
