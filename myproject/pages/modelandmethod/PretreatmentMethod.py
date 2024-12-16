"""
@Author : SakuraFox
@Time: 2024-02-29 15:04
@File : PretreatmentMethod.py
@Description : 预处理方法
"""
import numpy as np


class PretreatmentMethod:
    def __init__(self, dataFrame, fieldName, reservedField):
        self.dataFrame = dataFrame
        self.fieldName = fieldName
        self.reservedField = reservedField

    @staticmethod
    # 加工字段名称
    def getHandledFieldPoint(fieldName):
        # 若字段为原始数据
        if fieldName[-1].isdigit():
            return fieldName[:-1] + str(int(fieldName[-1]) + 1)
        # 若字段已处理,则末尾数字+1
        else:
            return f"{fieldName}-预处理后0"

    # 检测缺失值插剔除参数最小值>最大值
    @staticmethod
    def detectLinearInterpolationParam(methodParam):
        # 检测最小值>最大值
        if methodParam[0] < methodParam[1]:
            return True
        else:
            return False

    # 检测异常值(基于四分位数)
    @staticmethod
    def detect_outliers_iqr(dataT, exceptList):
        data = dataT.drop(exceptList, axis=1)
        lower_bound_list, upper_bound_list = [], []
        lower_outliers_list, upper_outliers_list = [], []
        for column in data.columns.tolist():
            # 计算四分位数
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1

            # 定义异常值范围
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # print(lower_bound)
            # print(upper_bound)
            # 检测异常值
            lower_outliers = data[data[column] < lower_bound]
            upper_outliers = data[data[column] > upper_bound]
            # print(min(lower_outliers[column].tolist()))
            # print(max(upper_outliers[column].tolist()))
            if len(lower_outliers) != 0 or len(upper_outliers) != 0:
                lower_bound_list.append(lower_bound)
                upper_bound_list.append(upper_bound)
                lower_outliers_list.append(len(lower_outliers))
                upper_outliers_list.append(len(upper_outliers))
        return data.columns.tolist(), lower_bound_list, upper_bound_list, lower_outliers_list, upper_outliers_list

    # 检测通用-数值
    @staticmethod
    def detectGeneralNumber(dfT1, fieldTemp1, specific_value):
        # 检查是否含有指定的值或NaN
        if specific_value is not None:
            if specific_value != 'nan':
                specific_value = float(specific_value)
                specific_value_count = dfT1[dfT1[fieldTemp1] == specific_value].shape[0]
            else:
                specific_value_count = len(dfT1[dfT1[fieldTemp1].isna()])
        else:
            specific_value_count = 0
        return specific_value_count

    # 检测通用-范围
    @staticmethod
    def detectGeneralScope(dfT1, fieldTemp1, upBound, lowBound):
        lower_outliers = dfT1[dfT1[fieldTemp1] < lowBound]
        upper_outliers = dfT1[dfT1[fieldTemp1] > upBound]
        return len(lower_outliers), len(upper_outliers)

    # 检测温度
    @staticmethod
    def detectLinearInterpolationWeather(dfT1):
        result = ''
        max_temp = dfT1['温度'].max()
        min_temp = dfT1['温度'].min()
        # 最高温度>45 最低温度<-15
        if max_temp > 50:
            result += '温度最大值>45 '
        if min_temp < -15:
            result += '温度最大值<-15 '
        return result

    # 检测降水
    @staticmethod
    def detectLinearInterpolationRain(dfT1):
        result = ''
        max_temp = dfT1['降水'].max()
        min_temp = dfT1['降水'].min()
        # 最大降水量>1500 最小降水量<0
        if max_temp > 1500:
            result += '降水最大值>1500 '
        if min_temp < 0:
            result += '降水最小值<0 '
        return result

    # 缺失值插补
    def linearInterpolation(self, methodParam):
        print(f'预处理方法参数:{methodParam}')
        missingValueBefore, missingValueAfter = None, None
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 复制原处理字段,并在名称后添加_预处理后
        newDataColumn = self.fieldName
        # print(f'线性插补:{self.fieldName}-{newDataColumn}')
        # 线性插值
        if methodParam[0] == '线性插值':
            newDataFrame[newDataColumn] = newDataFrame[self.fieldName]
            missingValueBefore = newDataFrame[newDataColumn].isnull().sum()
            newDataFrame[newDataColumn] = newDataFrame[newDataColumn].interpolate()
            missingValueAfter = newDataFrame[newDataColumn].isnull().sum()
        # 自定义插值
        elif methodParam[0] == '自定义':
            missValue, filledValue = methodParam[1], methodParam[2]
            newDataFrame[newDataColumn] = newDataFrame[self.fieldName]
            # 若指定字段为空
            if missValue == 'nan':
                missingValueBefore = (newDataFrame[newDataColumn] == np.nan).sum()
                newDataFrame[newDataColumn] = newDataFrame[newDataColumn].fillna(float(filledValue))
                missingValueAfter = (newDataFrame[newDataColumn] == np.nan).sum()
            else:
                missingValueBefore = (newDataFrame[newDataColumn] == float(missValue)).sum()
                newDataFrame[newDataColumn] = newDataFrame[newDataColumn].replace(float(missValue), float(filledValue))
                missingValueAfter = (newDataFrame[newDataColumn] == float(missValue)).sum()
        # 检查是否还有缺失值
        tempData = newDataFrame
        # tempData = newDataFrame[self.reservedField + [self.fieldName + '_预处理后']]
        return tempData, missingValueBefore, missingValueAfter, newDataColumn

    # 剔除异常值
    def outlierEliminator(self, methodParam):
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        minNum, maxNum = float(methodParam[1]), float(methodParam[0])
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()

        newDataColumn = self.fieldName

        # print(f'剔除异常值:{self.fieldName}-{newDataColumn}')
        newDataFrame[newDataColumn] = newDataFrame[self.fieldName]

        # 获取原始记录数
        lengthBefore = len(newDataFrame)
        # newDataFrame[self.fieldName] = newDataFrame[self.fieldName].clip(minNum, maxNum)
        newDataFrame = newDataFrame[
            (newDataFrame[self.fieldName] >= minNum) &
            (newDataFrame[self.fieldName] <= maxNum)]
        lengthAfter = len(newDataFrame)
        # 检查是否还有缺失值
        tempData = newDataFrame
        return tempData, lengthBefore, lengthAfter, newDataColumn

    # 剔除异常值及插补
    def outlierEliminatorInterpolation(self, methodParam):
        print('-----------测试5------------')
        print(methodParam)
        # 处理单值或范围
        flagSingle = methodParam[0]
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        newDataColumn = self.fieldName
        if flagSingle == '具体数值':
            missValue = methodParam[1]
            filledValue = methodParam[2]
            # 若指定字段为空
            if missValue == 'nan':
                missingValueBefore = (newDataFrame[newDataColumn] == np.nan).sum()
                newDataFrame[newDataColumn] = newDataFrame[newDataColumn].fillna(float(filledValue))
                missingValueAfter = (newDataFrame[newDataColumn] == np.nan).sum()
            else:
                missingValueBefore = (newDataFrame[newDataColumn] == float(missValue)).sum()
                newDataFrame[newDataColumn] = newDataFrame[newDataColumn].replace(float(missValue), float(filledValue))
                missingValueAfter = (newDataFrame[newDataColumn] == float(missValue)).sum()
        elif flagSingle == '范围数值':
            maxValue = float(methodParam[1])
            minValue = float(methodParam[2])
            # 剔除超出范围的异常值
            newDataFrame[self.fieldName] = newDataFrame[self.fieldName].where(
                (newDataFrame[self.fieldName] >= minValue) & (newDataFrame[self.fieldName] <= maxValue), np.nan)

            newDataFrame.to_excel('剔除.xlsx')
            # 使用线性插值填补NaN值
            newDataFrame[self.fieldName] = newDataFrame[self.fieldName].interpolate(method='linear',
                                                                                  limit_direction='both')
            newDataFrame.to_excel('插补.xlsx')

        return newDataFrame
