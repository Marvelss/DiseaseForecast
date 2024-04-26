"""
@Author : SakuraFox
@Time: 2024-04-24 9:51
@File : test12.py
@Description : 测试-降水累积量计算-指定日期计算和月计算(PASS)
"""

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

    def precipitationAccumulation(self, inputFields, timeRation):
        temp = None
        inputField = inputFields[0]
        flag = timeRation[0]
        # print(self.dataFrame)
        if flag == '月累积降水量':

            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 提取月份
            self.dataFrame['月'] = self.dataFrame['日期'].dt.month
            # 计算降水累积量
            self.dataFrame['降水累积量'] = self.dataFrame.groupby([
                '上级单位', '测报站点', '年', '月'])['降水'].transform('sum')
            temp = self.dataFrame
            # 使用左连接保证所有原始记录都被保留
            # temp = pd.merge(self.dataFrame, monthly_precipitation_sum, on=['年', '月'], how='left')
            # 删除'月','旬' '日期'字段
            # temp = temp.drop(['月', '日期'], axis=1)
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
            # temp = temp.drop(['旬', '日期'], axis=1)
        elif flag == '指定日期':
            # 指定日期范围（每年相同的日期）
            start_day = '08-01'
            end_day = '08-20'
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 转换日期到年内的日期格式，忽略年份
            self.dataFrame['年内日期'] = self.dataFrame['日期'].dt.strftime('%m-%d')

            # 过滤数据，只保留在指定日期范围内的记录
            date_filter = (self.dataFrame['年内日期'] >= start_day) & (self.dataFrame['年内日期'] <= end_day)
            filtered_df = self.dataFrame.loc[date_filter]

            # 计算每个分组在指定日期范围内的降水累积量
            sums = filtered_df.groupby(['上级单位', '测报站点', '年'])['降水'].sum()

            # 在原 DataFrame 上创建一个新列 '降水累积量'，初始值设置为 NaN
            self.dataFrame['降水累积量'] = pd.NA

            # 只为符合指定日期条件的行赋值累积降水量
            for index, total_precip in sums.items():
                match_condition = (self.dataFrame['上级单位'] == index[0]) & (
                        self.dataFrame['测报站点'] == index[1]) & (
                                          self.dataFrame['年'] == index[2]) & date_filter
                self.dataFrame.loc[match_condition, '降水累积量'] = total_precip
            temp = self.dataFrame
        return temp


# ====================月累积降水量====================

# 湖南省各县市
df1 = pd.read_excel('气象数据-湖南省.xlsx')
afterHandleData = FeatureCalculationMethod(
    df1, df1.columns).precipitationAccumulation(
    ['降水'], ['月累积降水量'])
afterHandleData.to_excel('result-HuNan Province.xlsx', index=False)

# 六省各县市
df1 = pd.read_excel('气象数据-六省.xlsx')
afterHandleData = FeatureCalculationMethod(
    df1, df1.columns).precipitationAccumulation(
    ['降水'], ['月累积降水量'])
afterHandleData.to_excel('result-Six Province.xlsx', index=False)

# ====================指定日期====================

# 湖南省各县市
df1 = pd.read_excel('气象数据-湖南省.xlsx')
afterHandleData = FeatureCalculationMethod(
    df1, df1.columns).precipitationAccumulation(
    ['降水'], ['指定日期'])
afterHandleData.to_excel('result-HuNan Province.xlsx', index=False)

# 六省各县市
df1 = pd.read_excel('气象数据-六省.xlsx')
afterHandleData = FeatureCalculationMethod(
    df1, df1.columns).precipitationAccumulation(
    ['降水'], ['指定日期'])
afterHandleData.to_excel('result-Six Province.xlsx', index=False)
