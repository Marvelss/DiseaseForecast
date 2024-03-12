"""
@Author : SakuraFox
@Time: 2024-02-29 15:40
@File : FeatureCalculationMethod.py
@Description : 特征计算方法
"""
from datetime import datetime

import pandas as pd


class FeatureCalculationMethod:
    def __init__(self, dataFrame, fieldName, reservedField):
        self.dataFrame = dataFrame
        self.fieldName = fieldName
        self.reservedField = ['上级单位', '测报站点', "年", "DayOfYear"] + reservedField

    # 旬值获取
    @staticmethod
    def get_decade(day):
        if day <= 10:
            return 1
        elif day <= 20:
            return 2
        else:
            return 3

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
            newDataFrame['日期'] = pd.to_datetime(
                newDataFrame['年'].astype(str) + newDataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 提取月份
            newDataFrame['月'] = newDataFrame['日期'].dt.month

            # 计算每月降水量总和
            monthly_precipitation_sum = newDataFrame.groupby(['年', '月'])['降水'].sum().reset_index(
                name='降水累积量')

            # 将月降水量总和合并回原始DataFrame
            # 使用左连接保证所有原始记录都被保留
            temp = pd.merge(newDataFrame, monthly_precipitation_sum, on=['年', '月'], how='left')
        elif timeRation[0][0] == '旬累积降水量':
            # 转换DayOfYear为日期，以便提取月份
            newDataFrame['日期'] = pd.to_datetime(
                newDataFrame['年'].astype(str) + newDataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 提取月份
            newDataFrame['月'] = newDataFrame['日期'].dt.month

            # 计算每天所在的旬，假设1-10日为第一旬，11-20日为第二旬，21日至月末为第三旬

            newDataFrame['旬'] = newDataFrame['日期'].dt.day.apply(FeatureCalculationMethod.get_decade)

            # 计算每旬的累积降水量
            decade_precipitation_sum = newDataFrame.groupby(['年', '月', '旬'])['降水'].sum().reset_index(
                name='降水累积量')

            # 将旬累积降水量合并回原始DataFrame
            temp = pd.merge(newDataFrame, decade_precipitation_sum, on=['年', '月', '旬'], how='left')

        tempData = temp[list(set(self.reservedField + ['降水累积量']))]
        return tempData

    # 计算降雨日数
    def rainfallDaysAccumulation(self, param):
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        print('===========接收参数===========')
        print(param)
        startMD = param[0][0]
        tempS = startMD.split('-')
        startM, startD = int(tempS[1]), int(tempS[2])
        endMD = param[0][1]
        tempE = endMD.split('-')
        endM, endD = int(tempE[1]), int(tempE[2])
        rule = param[0][2]
        minNum = param[0][3]
        duration = param[0][4]  # 暂未使用,默认1天
        print(self.fieldName)
        if rule == '单日降水量':
            # 转换DayOfYear为日期
            newDataFrame['日期'] = pd.to_datetime(
                newDataFrame['年'].astype(str) +
                newDataFrame['DayOfYear'].astype(str), format='%Y%j')
            # 根据上级单位、测报站点、年分类
            grouped = newDataFrame.groupby(['上级单位', '测报站点', '年'])
            for (key, group) in grouped:
                start_date_range = datetime(key[2], startM, startD)
                end_date_range = datetime(key[2], endM, endD)
                rainy_days_count = len(
                    group[
                        (group['日期'] >= start_date_range) &
                        (group['日期'] <= end_date_range) &
                        (group[self.fieldName] > float(minNum))]
                )
                # print(key, rainy_days_count)

                # Assign the calculated rainy days count to the '降雨日数' column within the specified date range
                mask = (newDataFrame['上级单位'] == key[0]) & (newDataFrame['测报站点'] == key[1]) & (
                        newDataFrame['日期'] >= start_date_range) & (
                               newDataFrame['日期'] <= end_date_range)
                newDataFrame.loc[mask, '降雨日数'] = rainy_days_count
            # print(newDataFrame)
            tempData = newDataFrame[list(set(self.reservedField + ['降雨日数']))]
            return tempData
