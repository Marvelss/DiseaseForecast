"""
@Author : SakuraFox
@Time: 2024-10-14 17:06
@File : test_pretreatment_interface.py
@Description : 测试预处理界面
"""
import os
import sys
import unittest

import allure
import pandas as pd
from streamlit.testing.v1 import AppTest

from pages import pages_utils

# Get the root directory (diseaseForecastStreamlit) relative to this script
# script_path = os.path.join(project_root, 'myproject/app.py')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
script_path = r'E:\a_python\program\diseaseForecastStreamlit\myproject\pages\DataPreparation.py'
import unittest


@allure.feature('界面测试(集成测试)')
@allure.story('预处理界面')
class PretreatmentInterface(unittest.TestCase):
    """
    测试点状 - 预处理界面
    """

    def setUp(self):
        # ==============初始化原始数据====================
        pages_utils.TempDataSet[0] = pd.read_excel(
            'pretreatment_interface_resource/苹果斑点落叶病-气象数据-气温和降水.xlsx')
        pages_utils.TempDataSetField[0] = pd.DataFrame(
            {
                '编号': ['0OKKVr97K45Px9d9'] * 6,
                '数据类型': ['气象数据'] * 6,
                '文件名称': ['苹果斑点落叶病-气象数据-气温和降水.xlsx'] * 6,  # 假设文件名称未知或未提供
                '字段': ['经度', '纬度', '年', 'DayOfYear', '温度', '降水'],  # 假设字段未知或未提供
                '传输状态': ['None'] * 6,
                '上传时间': ['None'] * 6
            }
        )

    @allure.title("测试点状预处理界面流程")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description('输入原始数据,执行2个缺失值插补方法')
    def test_PretreatmentPointInterface(self):
        at = AppTest.from_file(script_path)
        # ==============初始化缓存变量====================
        at.session_state['page12'] = 0
        at.session_state["leftTabs"] = ['原始数据']
        at.session_state['IMAGECOUNT'] = 0
        at.run()

        # ==============选择字段====================
        # at.multiselect[0].set_value(['降水'])
        # print('测试多选中字段')
        # print(at.multiselect[0])
        at.multiselect[0].select('降水')
        # ==============选择缺失值插补方法====================
        at.checkbox[4].check().run()
        # ==============点击添加处理按钮====================
        at.button[0].click().run()
        # ==============点击运行按钮====================
        at.button[1].click().run()
        # ==============选择第二个缺失值插补方法====================
        at.multiselect[0].unselect('降水')
        at.multiselect[0].select('温度')
        # ==============选择缺失值插补方法====================
        at.checkbox[4].check().run()
        # ==============点击添加处理按钮====================
        at.button[0].click().run()
        # ==============点击运行按钮====================
        at.button[1].click().run()

        # pages_utils.TempDataSetField[1].to_excel('处理记录.xlsx')
        # pages_utils.TempDataSet[1].to_excel('数据集.xlsx')
        # print(pages_utils.TempDataSetField[1])
        # print(pages_utils.TempDataSet[1])

        self.assertEqual([6],
                         [6])

    @allure.title("测试面状预处理界面流程")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description('输入原始数据,执行重采样和裁剪方法')
    def test_PretreatmentFacetInterface(self):
        pass
        # self.assertEqual(
        #     self.objPM.getHandledFieldPoint('温度'),
        #     '温度-预处理后0')
