"""
@Author : SakuraFox
@Time: 2024-02-29 15:04
@File : PretreatmentMethod.py
@Description : file description
"""


class PretreatmentMethod:
    def __init__(self, dataFrame, fieldName):
        self.dataFrame = dataFrame
        self.fieldName = fieldName

    # 线性插补
    def linearInterpolation(self):
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        missingValueBefore = newDataFrame[self.fieldName].isnull().sum()
        newDataFrame[self.fieldName] = newDataFrame[self.fieldName].interpolate()
        missingValueAfter = newDataFrame[self.fieldName].isnull().sum()
        # 检查是否还有缺失值
        tempData = newDataFrame[['上级单位', '测报站点',
                                 "年", "DayOfYear",
                                 self.fieldName]]
        return tempData, missingValueBefore, missingValueAfter

    # 剔除异常值
    def outlierEliminator(self, methodParam):
        minNum, maxNum = float(methodParam[1]), float(methodParam[0])
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 获取原始记录数
        lengthBefore = len(newDataFrame)
        newDataFrame[self.fieldName] = newDataFrame[self.fieldName].clip(minNum, maxNum)
        newDataFrame = newDataFrame[
            (newDataFrame[self.fieldName] >= minNum) &
            (newDataFrame[self.fieldName] <= maxNum)]
        lengthAfter = len(newDataFrame)
        # 检查是否还有缺失值
        tempData = newDataFrame[['上级单位', '测报站点',
                                 "年", "DayOfYear",
                                 self.fieldName]]
        return tempData, str(lengthBefore - lengthAfter), lengthAfter
