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

    # 检测缺失值插补具体可能错误
    @staticmethod
    def detectLinearInterpolation(methodParam):
        if methodParam[0] != '0.1':
            return False

    # 缺失值插补
    def linearInterpolation(self, methodParam):
        print(f'预处理方法参数:{methodParam}')
        missingValueBefore, missingValueAfter = None, None
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 复制原处理字段,并在名称后添加_预处理后
        newDataColumn = self.getHandledFieldPoint(self.fieldName)
        print(f'线性插补:{self.fieldName}-{newDataColumn}')
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

        newDataColumn = self.getHandledFieldPoint(self.fieldName)

        print(f'剔除异常值:{self.fieldName}-{newDataColumn}')
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
        return tempData, str(lengthBefore - lengthAfter), lengthAfter, newDataColumn
