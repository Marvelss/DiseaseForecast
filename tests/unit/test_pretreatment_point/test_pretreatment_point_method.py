"""
@Author : SakuraFox
@Time: 2024-04-07 9:41
@File : test_pretreatment_point_method.py
@Description : 测试-预处理界面方法-点状
"""
import os
import sys

import allure
import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

# Add 'myproject' to sys.path based on the correct root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from myproject.pages.modelandmethod.PretreatmentMethod import PretreatmentMethod
import unittest


@allure.feature('单元测试(功能测试)')
@allure.story('预处理界面 - 点状数据')
# ===================测试处理后字段名称变化===================
class PretreatmentPointMethod(unittest.TestCase):
    """
    测试点状 - 预处理界面
    """

    def setUp(self):
        self.objPM = PretreatmentMethod(
            None, None, None)
        self.objPM1 = PretreatmentMethod(
            pd.read_excel(os.path.join(os.path.dirname(__file__), '苹果斑点落叶病-气象数据-气象数据.xlsx')),
            ['4月下旬温度'], ['4月下旬温度'])
        self.verifyData = pd.read_excel(os.path.join(os.path.dirname(__file__), 'verifyData_MVIL.xlsx'))

    @allure.title("测试预处理前后字段名称变化-中文名称-首次处理")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description('名称末尾添加预处理0')
    def test_ChineseField(self):
        self.assertEqual(
            self.objPM.getHandledFieldPoint('温度'),
            '温度-预处理后0')

    @allure.title("测试预处理前后字段名称变化-英文名称-首次处理")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description('名称末尾添加预处理0')
    def test_EnglishField(self):
        self.assertEqual(
            self.objPM.getHandledFieldPoint('temperature'),
            'temperature-预处理后0')

    @allure.title("测试预处理前后字段名称变化-多次处理后")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description('名称末尾添加的数字+1')
    def test_MultiHandledField(self):
        self.assertEqual(
            self.objPM.getHandledFieldPoint('温度-预处理后3'),
            '温度-预处理后4')

    # ===================测试预处理方法===================
    # 缺失值插补-自定义
    @allure.title("测试预处理方法-自定义输入")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description('自定义输入完成插补')
    def test_MissingValueInterpolation_Custom(self):
        self.objPM.dataFrame = ''
        methodParam = ['线性插值']

        tempData, _, _, _ = self.objPM.linearInterpolation(methodParam)

    # 缺失值插补-线性插值
    @allure.title("测试预处理方法-自动线性插补")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description('基于pandas的线性插补')
    def test_MissingValueInterpolation_LinearInterpolation(self):
        methodParam = ['线性插值']
        tempData, _, _, _ = self.objPM1.linearInterpolation(methodParam)
        assert_frame_equal(
            pd.DataFrame(tempData[self.objPM1.getHandledFieldPoint(self.objPM1.fieldName)]),
            self.verifyData)

    # 异常值剔除
    @allure.title("测试预处理方法-异常值剔除")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description('基于pandas的线性插补')
    def test_OutlierEliminator(self):
        self.assertEqual(
            self.objPM.outlierEliminator('温度-预处理3'),
            '温度-预处理4')

    # 异常值检测
    @allure.title("测试预处理方法-异常值检测")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description('基于四分位点')
    def test_DetectOutliers(self):
        pass
        # assert_frame_equal(
        #     dataFrame[[newColumn]].head(365),
        #     self.verifyData.head(365))
        # self.assertEqual(
        #     self.objPM.detect_outliers_iqr('温度-预处理3'),
        #     '温度-预处理4')


if __name__ == '__main__':
    unittest.main()
