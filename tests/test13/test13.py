"""
@Author : SakuraFox
@Time: 2024-04-26 9:24
@File : test13.py
@Description : 测试-降雨日数计算-指定日期计算和月计算(PASS)
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
            # self.dataFrame = self.dataFrame.drop(['日期'], axis=1)
            return self.dataFrame


# ====================指定日期====================

# 湖南省各县市
df1 = pd.read_excel('气象数据-湖南省.xlsx')
afterHandleData = FeatureCalculationMethod(
    df1, df1.columns).rainfallDaysAccumulation(
    ['降水'], ['2020-4-1', '2020-4-20', '单日降水量', 0.1, 1])
afterHandleData.to_excel('result-HuNan Province.xlsx', index=False)

# 六省各县市
df1 = pd.read_excel('气象数据-六省.xlsx')
afterHandleData = FeatureCalculationMethod(
    df1, df1.columns).rainfallDaysAccumulation(
    ['降水'], ['2020-4-1', '2020-4-20', '单日降水量', 0.1, 1])
afterHandleData.to_excel('result-Six Province.xlsx', index=False)
