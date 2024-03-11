"""
@Author : SakuraFox
@Time: 2024-02-29 15:41
@File : FeatureOptimizationMethod.py
@Description : 特征优化方法
"""
import pandas as pd
from scipy.stats import stats
import numpy as np
from sklearn.model_selection import train_test_split
from skrebate import ReliefF


class FeatureOptimizationMethod:
    def __init__(self, dataFrame, fieldName, reservedField):
        self.dataFrame = dataFrame
        self.fieldName = fieldName
        self.reservedField = ['上级单位', '测报站点', "年", "DayOfYear"] + reservedField

    # t检验
    def tTest(self, methodParam):
        pValue = methodParam[0][0]
        # print(pValue)
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        print('============测试============')
        print(newDataFrame)
        print(self.fieldName[0])
        print(self.fieldName[1])
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
        tempData = newDataFrame[self.reservedField + self.fieldName]
        return tempData

    # t检验
    def ReliefF(self, methodParam):
        name = methodParam[0][0]
        proportion = methodParam[0][1]
        target = methodParam[0][2]

        print('--调用--')
        # print(name, proportion, target)
        # 复制新的变量
        df = self.dataFrame.copy()
        print(df)
        X = df.drop(target, axis=1).values  # 假设最后一列是目标变量
        y = df[target].values
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in df.columns.tolist():
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # 初始化ReliefF算法
        fs = ReliefF(n_neighbors=10, n_features_to_select=4)  # n_neighbors参数根据数据集大小调整，n_features_to_keep是你想要保留的特征数量

        # 训练ReliefF模型以找到最重要的特征
        fs.fit(X_train, y_train)
        # 假设 fs.feature_importances_ 包含了特征的重要性得分
        feature_scores = fs.feature_importances_
        selected_features_indices = None
        # 按照Top百分比选取特征
        if name == '按百分比选取':
            # 计算得分阈值，只选择前30%的特征
            q = proportion
            threshold = np.percentile(feature_scores, q)  # 100% - 30% = 70%，因为是选择前30%
            # 选取得分高于阈值的特征
            selected_features_indices = np.where(feature_scores >= threshold)[0]
        elif name == '按权重值计算':
            # 按照权重阈值选取特征
            # 设置得分阈值
            score_threshold = proportion
            # 选取得分高于阈值的特征
            selected_features_indices = np.where(feature_scores > score_threshold)[0]
            # 使用选定的特征来转换数据集
        # X_train_transformed = X_train[:, selected_features_indices]
        # X_test_transformed = X_test[:, selected_features_indices]
        selected_features = df.columns[selected_features_indices]
        tempData = df[selected_features + self.reservedField]
        print('--调用--')
        print(tempData)
        return tempData
