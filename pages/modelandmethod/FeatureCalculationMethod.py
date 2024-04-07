"""
@Author : SakuraFox
@Time: 2024-02-29 15:40
@File : FeatureCalculationMethod.py
@Description : 特征计算方法
"""
from datetime import datetime

import pandas as pd


class FeatureCalculationMethod:
    def __init__(self, dataFrame, reservedField):
        self.dataFrame = dataFrame.copy()
        self.reservedField = reservedField

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
    def precipitationAccumulation(self, inputFields, timeRation):
        temp = None
        inputField = inputFields[0]
        flag = timeRation[0]

        if flag == '月累积降水量':
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 提取月份
            self.dataFrame['月'] = self.dataFrame['日期'].dt.month

            # 计算每月降水量总和
            monthly_precipitation_sum = self.dataFrame.groupby(['年', '月'])[inputField].sum().reset_index(
                name='降水累积量')

            # 将月降水量总和合并回原始DataFrame
            # 使用左连接保证所有原始记录都被保留
            temp = pd.merge(self.dataFrame, monthly_precipitation_sum, on=['年', '月'], how='left')
            # 删除'月','旬' '日期'字段
            temp = temp.drop(['月', '日期'], axis=1)
        elif flag == '旬累积降水量':
            # 转换DayOfYear为日期，以便提取月份
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 提取月份
            self.dataFrame['月'] = self.dataFrame['日期'].dt.month

            # 计算每天所在的旬，假设1-10日为第一旬，11-20日为第二旬，21日至月末为第三旬

            self.dataFrame['旬'] = self.dataFrame['日期'].dt.day.apply(FeatureCalculationMethod.get_decade)

            # 计算每旬的累积降水量
            decade_precipitation_sum = self.dataFrame.groupby(['年', '月', '旬'])[inputField].sum().reset_index(
                name='降水累积量')

            # 将旬累积降水量合并回原始DataFrame
            temp = pd.merge(self.dataFrame, decade_precipitation_sum, on=['年', '月', '旬'], how='left')
            # 删除'月','旬' '日期'字段
            temp = temp.drop(['旬', '日期'], axis=1)
        # 删除还没生成的字段
        # tempReservedField = [field for field in self.reservedField if field in temp.columns]
        # print(f'==============降水累积量-筛选特征{tempReservedField}================')
        # tempData = temp[list(set(tempReservedField + ['降水累积量']))]
        return temp

    # 计算降雨日数
    def rainfallDaysAccumulation(self, inputFields, param):
        # 复制新的变量
        print('===========接收参数===========')
        print(param)
        print(inputFields)
        startMD = param[0]
        tempS = startMD.split('-')
        startM, startD = int(tempS[1]), int(tempS[2])
        endMD = param[1]
        tempE = endMD.split('-')
        endM, endD = int(tempE[1]), int(tempE[2])
        rule = param[2]
        minNum = param[3]
        # duration = param[0][4]  # 暂未使用,默认1天
        # print(self.fieldName)
        if rule == '单日降水量':
            # 转换DayOfYear为日期
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) +
                self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
            # 根据上级单位、测报站点、年分类
            grouped = self.dataFrame.groupby(['上级单位', '测报站点', '年'])
            for (key, group) in grouped:
                start_date_range = datetime(key[2], startM, startD)
                end_date_range = datetime(key[2], endM, endD)
                rainy_days_count = len(
                    group[
                        (group['日期'] >= start_date_range) &
                        (group['日期'] <= end_date_range) &
                        (group[inputFields[0]] >= float(minNum))]
                )
                # print('==========具体明细==========')
                # print(group[
                #         (group['日期'] >= start_date_range) &
                #         (group['日期'] <= end_date_range) &
                #         (group[inputFields[0]] >= float(minNum))])
                # print(f'长度{rainy_days_count}')
                # Assign the calculated rainy days count to the '降雨日数' column within the specified date range
                mask = (self.dataFrame['上级单位'] == key[0]) & (self.dataFrame['测报站点'] == key[1]) & (
                        self.dataFrame['日期'] >= start_date_range) & (
                               self.dataFrame['日期'] <= end_date_range)
                self.dataFrame.loc[mask, '降雨日数'] = rainy_days_count

            # # 删除还没生成的字段
            # tempReservedField = [field for field in self.reservedField if field in self.dataFrame.columns]
            # print(f'==============降雨日数-筛选特征{tempReservedField}================')
            # tempData = self.dataFrame[list(set(tempReservedField + ['降雨日数']))]
            # 删除'月','旬' '日期'字段
            self.dataFrame = self.dataFrame.drop(['日期'], axis=1)
            return self.dataFrame
