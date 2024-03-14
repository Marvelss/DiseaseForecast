import streamlit as st

from st_pages import Page, show_pages

# add_page_title()


# Adjust the width of the Streamlit page
st.set_page_config(
    page_title="病虫害预测系统",
    layout="wide"
)

# Establish communication between pygwalker and streamlit
# init_streamlit_comm()

# 控制界面显示
show_pages(
    [
        Page("pages/App.py", "主页"),
        Page("pages/DataSet.py", "数据集"),
        Page("pages/DataPreparation.py", "数据预处理"),
        Page("pages/FeatureCalculation.py", "特征计算"),
        Page("pages/FeatureOptimization.py", "特征优选"),
        Page("pages/ModelBuilding.py", "模型构建"),
        Page("pages/ModelApplication.py", '模型应用'),
        Page("pages/Visualization.py", '可视化及数据下载'),
        Page("pages/ModelEvaluation.py", "测试界面")
    ]
)
# 初始化控制各环节左侧内容展示
if 'page12' not in st.session_state:
    st.session_state.page12 = 0
# 左侧内容标题
if "leftTabs" not in st.session_state:
    st.session_state["leftTabs"] = ['原始数据']

# 设置网页标题
st.title('多场景病虫害预测系统')
st.subheader('简介')
# # 纯文本
st.text("""
基于WEB的多场景病虫害预测系统是指利用网络技术搭建的用于预测农作物病虫害发生和蔓延情况的系统。这类系统通常结合了农业领域的专业知识、气象数据、植物病虫害生态学等多方面的信息，以实现对病虫害的准确预测和预警。

""")
st.subheader('关键功能和特点')
st.text("""
1.数据收集和整合：系统通过网络技术实时获取气象数据、农作物生长数据、土壤状况等相关信息，并对这些数据进行整合和存储。
2.多场景模型建立：系统利用机器学习、数据挖掘等技术建立病虫害预测模型，这些模型可以基于不同的场景和地区进行灵活调整，以适应不同作物和环境条件下的病虫害预测需求。
3.可视化展示和分析：系统提供直观的图表展示和数据分析功能，将预测结果以可视化的方式呈现给用户，帮助用户快速了解病虫害发生的可能性和趋势。
4.实时预警和建议：系统具有实时监测功能，能够根据预测模型输出的结果，及时向农户或专业人士发出预警信息，提示可能的病虫害发生风险，并提供相应的防治建议。
5.云端服务：由于使用基于WEB的技术，多场景病虫害预测系统可以部署在云端平台上，提供灵活的访问和使用方式，用户可以通过智能手机、平板电脑等设备随时随地获取相关信息。
""")
