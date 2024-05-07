"""
@Author : SakuraFox
@Time: 2024-05-07 21:06
@File : test20.py
@Description : 测试-基于活动积温的生育期计算
输入：地点、年、DOY、温度
输出：抽穗期、孕育期
"""
import numpy as np
import pandas as pd


# ==========================特征计算==========================
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
    def growthPeriodCalculation(self, inputFields, param):

        # 复制新的变量
        print('===========接收参数===========')
        print(param)
        print(inputFields)
        start_day = param[0]
        end_day = param[1]
        growthPeriod = param[2]
        threshold = param[3]
        print(start_day, end_day)
        # 根据上级单位、测报站点、年分类
        self.dataFrame['日期'] = pd.to_datetime(
            self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

        # 转换日期到年内的日期格式，忽略年份
        self.dataFrame['年内日期'] = self.dataFrame['日期'].dt.strftime('%m-%d')

        # 过滤数据，只保留在指定日期范围内的记录
        date_filter = (self.dataFrame['年内日期'] >= start_day) & (self.dataFrame['年内日期'] <= end_day)
        filtered_df = self.dataFrame.loc[date_filter]
        print(filtered_df)

        grouped = filtered_df.groupby(['上级单位', '测报站点', '年'])
        for (key, group) in grouped:

            # Calculate the cumulative temperature for each day in the range
            group['累计温度'] = np.cumsum(group['温度'])
            mask = group['累计温度'] >= threshold
            print('-------------')
            print(group['累计温度'])
            print(group['温度'])
            if mask.any():
                # 获取mask为True的行索引
                true_indices = group[mask].index[0]
                # 获取true_indices对应的DayOfYear值
                doy = group.loc[true_indices, 'DayOfYear']
                # 为该组的'上级单位', '测报站点', '年'赋值
                self.dataFrame.loc[(self.dataFrame['上级单位'] == key[0]) &
                                   (self.dataFrame['测报站点'] == key[1]) &
                                   (self.dataFrame['年'] == key[2]), growthPeriod] = doy
            # # 删除还没生成的字段
            # tempReservedField = [field for field in self.reservedField if field in self.dataFrame.columns]
            # print(f'==============降雨日数-筛选特征{tempReservedField}================')
            # tempData = self.dataFrame[list(set(tempReservedField + ['降雨日数']))]
            # 删除'月','旬' '日期'字段
        self.dataFrame = self.dataFrame.drop(['日期'], axis=1)
        self.dataFrame.to_excel('result.xlsx', index=False)
        return self.dataFrame


df1 = pd.read_excel('气象数据-六省.xlsx')
# 特征计算
afterHandleData = FeatureCalculationMethod(
    df1, df1.columns).growthPeriodCalculation(
    ['上级单位', '测报站点', '年', 'DayOfYear', '温度'],
    ['01-01', '08-20', '抽穗期', 50])
afterHandleData1 = FeatureCalculationMethod(
    afterHandleData, afterHandleData.columns).growthPeriodCalculation(
    ['上级单位', '测报站点', '年', 'DayOfYear', '温度'],
    ['01-01', '08-20', '孕育期', 150])
