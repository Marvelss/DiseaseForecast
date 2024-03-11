"""
@Author : SakuraFox
@Time: 2024-02-29 15:40
@File : FeatureCalculationMethod.py
@Description : 特征计算方法
"""
import pandas as pd


class FeatureCalculationMethod:
    def __init__(self, dataFrame, fieldName, reservedField):
        self.dataFrame = dataFrame
        self.fieldName = fieldName
        self.reservedField = ['上级单位', '测报站点', "年", "DayOfYear"] + reservedField

    # 降水累积量计算
    def precipitationAccumulation(self, timeRation):
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        temp = None
        # newDataFrame['月降水累积量'] = newDataFrame[fieldName].sum()

        # 单独计算插补所用的总和
        # sum_value = newDataFrame[fieldName].sum()
        # print(f"均值为: {sum_value}")
        # newDataFrame['降水累积量'].fillna(sum_value, inplace=True)
        if timeRation[0][0] == '月累积降水量':
            month_precipitation = (newDataFrame.groupby('MonthOfYear')['降水'].
                                   sum().reset_index(name='月累积降水量'))
            temp = pd.merge(newDataFrame, month_precipitation, on='MonthOfYear', how='left')
        tempData = temp[self.reservedField + [self.fieldName]]
        return tempData
