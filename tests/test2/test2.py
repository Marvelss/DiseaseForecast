"""
@Author : SakuraFox
@Time: 2024-03-19 17:08
@File : test2.py
@Description : 测试特征计算-降雨日数计算(通过)
"""
import unittest

import pandas as pd

from pages.modelandmethod.FeatureCalculationMethod import FeatureCalculationMethod


# import the class containing the method to be tested


class TestRainfallDaysAccumulation(unittest.TestCase):
    def setUp(self):
        # 加载数据
        data = pd.read_excel('气象数据.xlsx')
        # 预留字段
        reservedField = ['上级单位', '测报站点', "年", "DayOfYear", '降水']
        # Initialize the test data or create mock objects if needed
        self.obj = FeatureCalculationMethod(data,
                                            reservedField)  # create an instance of the class that contains the method

    def test_rainfallDaysAccumulation(self):
        # 输入字段
        inputFields = ["降水"]
        # 输入参数
        param = ["2024-01-01", "2024-01-30", "单日降水量", "0.1"]
        # 运行方法
        result = self.obj.rainfallDaysAccumulation(inputFields, param)

        # 测试返回值是否空
        self.assertIsNotNone(result)
        # Add more specific assertions based on the expected behavior of the method


if __name__ == '__main__':
    unittest.main()
