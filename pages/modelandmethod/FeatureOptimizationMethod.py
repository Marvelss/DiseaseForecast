"""
@Author : SakuraFox
@Time: 2024-02-29 15:41
@File : FeatureOptimizationMethod.py
@Description : 特征优化方法
"""
from scipy.stats import stats


class FeatureOptimizationMethod:
    def __init__(self, dataFrame, fieldName):
        self.dataFrame = dataFrame
        self.fieldName = fieldName

    # t检验
    def tTest(self, methodParam):
        pValue = methodParam[0][0]
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 创建一个空列表来存储显著的降水特征
        # significant_features = []
        # 计算 t 检验的 p 值，并选择 p < 0.05 的特征
        # print(fieldName)
        # print('--------------fieldName--------------')
        if pValue == '0.05':
            pass
        t_stat, p_value = stats.ttest_ind(
            newDataFrame[self.fieldName[0]],
            newDataFrame[self.fieldName[1]])
        print('======================特征优选-t检验结果======================')
        print(t_stat, p_value)
        tempData = newDataFrame[['上级单位', '测报站点',
                                 "年", "MonthOfYear",
                                 "DecadeOfYear", "DayOfYear"]]
        return tempData
