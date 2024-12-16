"""
@Author : SakuraFox
@Time: 2024-02-29 15:40
@File : FeatureCalculationMethod.py
@Description : 特征计算方法
"""
from datetime import datetime
from typing import Union

import numpy as np
import pandas as pd


class FeatureCalculationMethod:

    def __init__(self, dataFrame, reservedField):
        self.dataFrame = dataFrame.copy()
        self.reservedField = reservedField
        self.newColumn = []

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
        # newColumn = '降水累积量'
        inputField = inputFields[0]
        flag = timeRation[0]
        if flag == '月累积降水量':
            # self.dataFrame['日期'] = pd.to_datetime(
            #     self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
            # # 提取月份
            # self.dataFrame['月'] = self.dataFrame['日期'].dt.month

            # 计算每月降水量总和
            monthly_precipitation_sum = self.dataFrame.groupby(['经度', '纬度', '年', '月'])[
                inputField].sum().reset_index(
                name='月_降水累积量')
            # 将月降水量总和合并回原始DataFrame
            temp = pd.merge(self.dataFrame, monthly_precipitation_sum, on=['经度', '纬度', '年', '月'], how='left')

            # 根据数据集提取月份列并去除重复值和排序
            unique_months = sorted(temp['月'].drop_duplicates().to_numpy().tolist())
            # print(unique_months)
            # print(temp.columns)
            # 将每月降水量总和作为新列
            # temp = temp.loc[:, ~temp.columns.str.endswith('_x')]
            for month in unique_months:
                col_name = f'{month}月_累积降水量'
                temp[col_name] = temp['月_降水累积量'].where(temp['月'] == month, None)
                # print(col_name)
                self.newColumn.append(col_name)
            # 删除'月','旬' '日期'字段
            temp = temp.drop(['月_降水累积量'], axis=1)
            # temp = temp.drop(['月', '日期'], axis=1)
        elif flag == '旬累积降水量':
            # # 转换DayOfYear为日期，以便提取月份
            # self.dataFrame['日期'] = pd.to_datetime(
            #     self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
            #
            # # 提取月份
            # self.dataFrame['月'] = self.dataFrame['日期'].dt.month
            #
            # # 计算每天所在的旬，假设1-10日为第一旬，11-20日为第二旬，21日至月末为第三旬
            #
            # self.dataFrame['旬'] = self.dataFrame['日期'].dt.day.apply(FeatureCalculationMethod.get_decade)

            # 计算每旬的累积降水量
            decade_precipitation_sum = self.dataFrame.groupby(['经度', '纬度', '年', '月', '旬'])[
                inputField].sum().reset_index(
                name='旬_降水累积量')
            # 根据数据集提取月份列并去除重复值和排序
            unique_months = sorted(self.dataFrame['月'].drop_duplicates().to_numpy().tolist())
            # 将旬累积降水量合并回原始DataFrame
            temp = pd.merge(self.dataFrame, decade_precipitation_sum, on=['经度', '纬度', '年', '月', '旬'], how='left')
            # print(decade_precipitation_sum)
            # 将每旬降水量总和作为新列
            decade_names = {1: "上旬", 2: "中旬", 3: "下旬"}

            for month in unique_months:
                for decade in range(1, 4):  # 假设每个月有3个旬
                    col_name = f'{month}月{decade_names[decade]}_降水累积量'
                    temp[col_name] = temp['旬_降水累积量'].where((temp['月'] == month) & (temp['旬'] == decade), None)
                    self.newColumn.append(col_name)

            # 删除不再需要的字段
            temp = temp.drop(['旬_降水累积量'], axis=1)
            # temp = temp.drop(['月', '旬', '日期'], axis=1)
            # 删除'月','旬' '日期'字段
            # temp = temp.drop(['旬', '日期'], axis=1)
        elif flag == '指定日期':
            startDate = timeRation[1]
            endDate = timeRation[2]
            # 指定日期范围（每年相同的日期）
            start_day = startDate
            end_day = endDate
            # self.dataFrame['日期'] = pd.to_datetime(
            #     self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
            #
            # # 转换日期到年内的日期格式，忽略年份
            # self.dataFrame['年内日期'] = self.dataFrame['日期'].dt.strftime('%m-%d')

            # 过滤数据，只保留在指定日期范围内的记录
            date_filter = (self.dataFrame['年内日期'] >= start_day) & (self.dataFrame['年内日期'] <= end_day)
            filtered_df = self.dataFrame.loc[date_filter]

            # 计算每个分组在指定日期范围内的降水累积量
            sums = filtered_df.groupby(['经度', '纬度', '年'])['降水'].sum()

            # 在原 DataFrame 上创建一个新列 '降水累积量'，初始值设置为 NaN
            newColumn = startDate + '_' + endDate + '_' + '降水累积量'
            self.dataFrame[newColumn] = pd.NA

            # 只为符合指定日期条件的行赋值累积降水量
            for index, total_precip in sums.items():
                match_condition = (self.dataFrame['经度'] == index[0]) & (
                        self.dataFrame['纬度'] == index[1]) & (
                                          self.dataFrame['年'] == index[2]) & date_filter
                self.dataFrame.loc[match_condition, newColumn] = total_precip
            self.newColumn.append(newColumn)
            temp = self.dataFrame
        # 删除还没生成的字段
        # tempReservedField = [field for field in self.reservedField if field in temp.columns]
        # print(f'==============降水累积量-筛选特征{tempReservedField}================')
        # tempData = temp[list(set(tempReservedField + ['降水累积量']))]
        return temp, ','.join(self.newColumn)

    # 计算降雨日数
    def rainfallDaysAccumulation(self, inputFields, param):
        # 复制新的变量
        # print('===========接收参数===========')
        # print(param)
        # print(inputFields)
        startMD = param[0]
        tempS = startMD.split('-')
        startM, startD = int(tempS[1]), int(tempS[2])
        endMD = param[1]
        tempE = endMD.split('-')
        endM, endD = int(tempE[1]), int(tempE[2])
        rule = param[2]
        minNum = param[3]
        newColumn = str(startM) + '-' + str(startD) + '_' + str(endM) + '-' + str(endD) + '_' + '降雨日数'
        # duration = param[0][4]  # 暂未使用,默认1天
        # print(self.fieldName)
        if rule == '单日降水量':
            # 转换DayOfYear为日期
            # self.dataFrame['日期'] = pd.to_datetime(
            #     self.dataFrame['年'].astype(str) +
            #     self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
            # 根据"经度", "纬度"、年分类
            grouped = self.dataFrame.groupby(['经度', '纬度', '年'])
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
                mask = (self.dataFrame['经度'] == key[0]) & (self.dataFrame['纬度'] == key[1]) & (
                        self.dataFrame['日期'] >= start_date_range) & (
                               self.dataFrame['日期'] <= end_date_range)
                self.dataFrame.loc[mask, newColumn] = rainy_days_count

            # # 删除还没生成的字段
            # tempReservedField = [field for field in self.reservedField if field in self.dataFrame.columns]
            # print(f'==============降雨日数-筛选特征{tempReservedField}================')
            # tempData = self.dataFrame[list(set(tempReservedField + ['降雨日数']))]
            # 删除'月','旬' '日期'字段
            # self.dataFrame = self.dataFrame.drop(['日期'], axis=1)
            self.newColumn.append(newColumn)
            return self.dataFrame, ','.join(self.newColumn)

    # 基于活动积温的生育期计算
    def growthPeriodCalculation(self, inputFields, param):
        # 复制新的变量
        # print('===========接收参数===========')
        # print(param)
        # print(inputFields)
        growthPeriod = param[0]

        start_day = param[1]
        end_day = param[2]
        threshold = int(param[3])
        # # 根据"经度", "纬度"、年分类
        # self.dataFrame['日期'] = pd.to_datetime(
        #     self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
        #
        # # 转换日期到年内的日期格式，忽略年份
        # self.dataFrame['年内日期'] = self.dataFrame['日期'].dt.strftime('%m-%d')

        # 过滤数据，只保留在指定日期范围内的记录
        date_filter = (self.dataFrame['年内日期'] >= start_day) & (self.dataFrame['年内日期'] <= end_day)
        filtered_df = self.dataFrame.loc[date_filter]

        grouped = filtered_df.groupby(['经度', '纬度', '年'])
        for (key, group) in grouped:
            # Calculate the cumulative temperature for each day in the range
            group['累计温度'] = np.cumsum(group['温度'])
            mask = group['累计温度'] >= threshold
            if mask.any():
                # 获取mask为True的行索引
                true_indices = group[mask].index[0]
                # 获取true_indices对应的DayOfYear值
                doy = group.loc[true_indices, 'DayOfYear']
                # 为该组的"经度", "纬度", '年'赋值
                self.dataFrame.loc[(self.dataFrame['经度'] == key[0]) &
                                   (self.dataFrame['纬度'] == key[1]) &
                                   (self.dataFrame['年'] == key[2]), growthPeriod] = doy
        # self.dataFrame = self.dataFrame.drop(['日期'], axis=1)
        # 若设定积温未到达,则返回错误
        if growthPeriod not in self.dataFrame.columns.tolist():
            self.newColumn.append('错误')
        else:
            self.newColumn.append(growthPeriod)

        return self.dataFrame, ','.join(self.newColumn)

    # 活动积温计算
    def activeAccumulatedTemperature(self, inputFields, param):
        # 复制新的变量
        # print('===========接收参数===========')
        # print(param)
        # print(inputFields)
        startMD = param[0]
        tempS = startMD.split('-')
        startM, startD = int(tempS[1]), int(tempS[2])
        endMD = param[1]
        tempE = endMD.split('-')
        endM, endD = int(tempE[1]), int(tempE[2])
        newColumn = str(startM) + '-' + str(startD) + '_' + str(endM) + '-' + str(endD) + '_' + '活动积温'

        # # 根据"经度", "纬度"、年分类
        # self.dataFrame['日期'] = pd.to_datetime(
        #     self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
        # # 转换日期到年内的日期格式，忽略年份
        # self.dataFrame['年内日期'] = self.dataFrame['日期'].dt.strftime('%m-%d')
        # 过滤数据，只保留在指定日期范围内的记录
        date_filter = (self.dataFrame['年内日期'] >= datetime.strptime(startMD, '%Y-%m-%d').strftime('%m-%d')) & (
                self.dataFrame['年内日期'] <= datetime.strptime(endMD, '%Y-%m-%d').strftime('%m-%d'))
        filtered_df = self.dataFrame.loc[date_filter]

        grouped = filtered_df.groupby(['经度', '纬度', '年'])
        # 创建新的列用于存储结果
        self.dataFrame[newColumn] = np.nan
        # 遍历每个分组并计算累计温度
        for (key, group) in grouped:
            # 计算累计温度
            tempAAT = np.cumsum(group['温度']).iloc[-1]

            # 更新原始 DataFrame 中对应的行
            self.dataFrame.loc[group.index, newColumn] = tempAAT
        self.newColumn.append(newColumn)
        return self.dataFrame, ','.join(self.newColumn)

    # 气象指标均值计算
    def meteorologicalMeanAccumulation(self, inputFields, timeRation):
        temp = None
        # newColumn = '降水累积量'
        inputField = inputFields[0]
        flag = timeRation[0]
        if flag == '月均值':
            # 计算每月均值
            monthly_precipitation_mean = self.dataFrame.groupby(['经度', '纬度', '年', '月'])[
                inputField].mean().reset_index(name='月均值')
            # 将月降水量总和合并回原始DataFrame
            temp = pd.merge(self.dataFrame, monthly_precipitation_mean, on=['经度', '纬度', '年', '月'], how='left')

            # 根据数据集提取月份列并去除重复值和排序
            unique_months = sorted(temp['月'].drop_duplicates().to_numpy().tolist())
            # print(unique_months)
            # print(temp.columns)
            # 将每月降水量总和作为新列
            # temp = temp.loc[:, ~temp.columns.str.endswith('_x')]
            for month in unique_months:
                col_name = f'{month}月_{inputField}均值'
                temp[col_name] = temp['月均值'].where(temp['月'] == month, None)
                # print(col_name)
                self.newColumn.append(col_name)
            # 删除'月','旬' '日期'字段
            temp = temp.drop(['月均值'], axis=1)
            # temp = temp.drop(['月', '日期'], axis=1)
        elif flag == '旬均值':
            # 计算每旬均值
            decade_precipitation_mean = self.dataFrame.groupby(['经度', '纬度', '年', '月', '旬'])[inputField].mean().reset_index(name='旬均值')
            temp = pd.merge(self.dataFrame, decade_precipitation_mean, on=['经度', '纬度', '年', '月', '旬'], how='left')
            # 根据数据集提取月份列并去除重复值和排序
            unique_months = sorted(temp['月'].drop_duplicates().to_numpy().tolist())
            # print(decade_precipitation_sum)
            # 将每旬降水量总和作为新列
            decade_names = {1: "上旬", 2: "中旬", 3: "下旬"}

            for month in unique_months:
                for decade in range(1, 4):  # 假设每个月有3个旬
                    col_name = f'{month}月{decade_names[decade]}_{inputField}均值'
                    temp[col_name] = temp['旬均值'].where((temp['月'] == month) & (temp['旬'] == decade), None)
                    self.newColumn.append(col_name)
            # 删除不再需要的字段
            temp = temp.drop(['旬均值'], axis=1)
        return temp, ','.join(self.newColumn)
