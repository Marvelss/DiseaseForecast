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

    # 加工字段名称
    def getHandledField(self, fieldName):
        # 若字段为原始数据
        if '_预' not in fieldName:
            return f"{fieldName}_预处理后"
        # 若字段已处理,则末尾数字+1
        if '_预' in fieldName:
            return (fieldName.split('后')[0] + '后' +
                    str(int(fieldName.split('后')[1]) + 1))

    # 线性插补
    def linearInterpolation(self):
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 复制原处理字段,并在名称后添加_预处理后
        newDataColumn = self.getHandledField(self.fieldName)
        print(f'线性插补:{self.fieldName}-{newDataColumn}')

        newDataFrame[newDataColumn] = newDataFrame[self.fieldName]
        missingValueBefore = newDataFrame[newDataColumn].isnull().sum()
        newDataFrame[newDataColumn] = newDataFrame[newDataColumn].interpolate()
        missingValueAfter = newDataFrame[newDataColumn].isnull().sum()
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

        newDataColumn = self.getHandledField(self.fieldName)
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
