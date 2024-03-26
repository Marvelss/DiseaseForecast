"""
@Author : SakuraFox
@Time: 2024-02-29 15:04
@File : PretreatmentMethod.py
@Description : 预处理方法
"""


class PretreatmentMethod:
    def __init__(self, dataFrame, fieldName, reservedField):
        self.dataFrame = dataFrame
        self.fieldName = fieldName
        self.reservedField = reservedField

    # 线性插补
    def linearInterpolation(self):
        print('==========接收self.fieldName==========')
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 复制原处理字段,并在名称后添加_预处理后
        newDataColumn = f"{self.fieldName}_预处理后"
        newDataFrame[newDataColumn] = newDataFrame[self.fieldName]
        missingValueBefore = newDataFrame[newDataColumn].isnull().sum()
        newDataFrame[newDataColumn] = newDataFrame[newDataColumn].interpolate()
        missingValueAfter = newDataFrame[newDataColumn].isnull().sum()
        # 检查是否还有缺失值
        print(F'=========检查数组并情况=========')
        # print(self.reservedField)
        print(self.fieldName)
        # print(self.reservedField + [self.fieldName])
        tempData = newDataFrame
        # tempData = newDataFrame[self.reservedField + [self.fieldName + '_预处理后']]
        return tempData, missingValueBefore, missingValueAfter

    # 剔除异常值
    def outlierEliminator(self, methodParam):
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        print(methodParam)
        minNum, maxNum = float(methodParam[1]), float(methodParam[0])
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        print(newDataFrame)

        # 获取原始记录数
        lengthBefore = len(newDataFrame)
        # newDataFrame[self.fieldName] = newDataFrame[self.fieldName].clip(minNum, maxNum)
        newDataFrame = newDataFrame[
            (newDataFrame[self.fieldName] >= minNum) &
            (newDataFrame[self.fieldName] <= maxNum)]
        lengthAfter = len(newDataFrame)
        # 检查是否还有缺失值
        print('======到处理完数据集')
        print(newDataFrame)
        tempData = newDataFrame[self.reservedField + [self.fieldName + '_预处理后']]
        return tempData, str(lengthBefore - lengthAfter), lengthAfter
