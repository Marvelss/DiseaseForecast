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
from sklearn.preprocessing import StandardScaler
from skrebate import ReliefF


class FeatureOptimizationMethod:
    def __init__(self, dataFrame, reservedField):
        self.dataFrame = dataFrame.copy()
        self.reservedField = reservedField

    # 加工字段名称
    def getHandledField(self, fieldName):
        # 若字段为原始数据
        if '_优' not in fieldName:
            return f"{fieldName}_优选特征"
        # 若字段已处理,则末尾数字+1
        if '_优' in fieldName:
            return (fieldName.split('征')[0] + '征' +
                    str(int(fieldName.split('征')[1]) + 1))

    # t检验
    def tTest(self, methodParam):
        # param:['年', 'DayOfYear 上级单位 测报站点', '0.02']
        # param1:目标变量
        # param2:被比较变量
        # param3:提取条件
        targetVariable = methodParam[0]
        comparedVariableList = methodParam[1].split(' ')
        condition = methodParam[2]
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        tempResult = {}
        # t检验并获取每个变量p-value结果
        for feature in comparedVariableList:
            rainfall = np.array(newDataFrame[feature].tolist())
            disease = np.array(newDataFrame[targetVariable].tolist())
            t_stat, p_value = stats.ttest_ind(
                rainfall,
                disease)
            tempResult[feature] = p_value

        # 删选p-value符合条件的特征
        filtered_data = {key: value for key, value in tempResult.items() if value <= condition}
        # 获取优选特征集
        optimalFeatureList = list(filtered_data.keys())
        newColumnsList = []
        for feature in optimalFeatureList:
            new_column_name = self.getHandledField(feature)
            self.dataFrame[new_column_name] = self.dataFrame[feature]
            newColumnsList.append(new_column_name)
        return self.dataFrame, tempResult, newColumnsList

    # RF互相关分析
    def ReliefF(self, inputFields, methodParam):
        target = methodParam[0][0]
        name = methodParam[0][1]
        proportion = methodParam[0][2]
        # =========================提取有效值=========================
        # 使用groupby分组并提取每个分组的第一个非空值
        ultimateFeatures = self.dataFrame.groupby(['上级单位', '测报站点', '年']).first().reset_index()
        # ******删除包含缺失值的行******
        df_cleaned = ultimateFeatures.dropna()
        # 准备数据
        X = df_cleaned[inputFields].drop(columns=[target])  # 假设我们已经从df中删除了目标列和不需要的列
        y = df_cleaned[target]
        # print('设置检查和处理缺失值')
        # print(X.index)
        # X = X.dropna()
        # print(X.index)
        # y = y.loc[X.index]  # 保持 y 和 X 的索引一致

        # 确保所有列的数据类型一致
        # X = X.astype(float)
        # 找到包含缺失值的行
        # missing_rows = X.isnull().any(axis=1)
        # 数据标准化
        # scaler = StandardScaler()
        # X_scaled = scaler.fit_transform(X)
        # print(X_scaled)
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

        # 重置索引并转换为NumPy数组
        X_train = X_train.reset_index(drop=True).to_numpy()
        y_train = y_train.reset_index(drop=True).to_numpy()
        fs = ReliefF(n_features_to_select=len(X.columns))

        # 训练ReliefF模型以找到最重要的特征
        fs.fit(X_train, y_train)
        # 假设 fs.feature_importances_ 包含了特征的重要性得分
        feature_scores = fs.feature_importances_
        print(f'特征重要性:{feature_scores}')

        selected_features_indices = None
        # 按照Top百分比选取特征
        if name == '按百分比选取':
            # 计算得分阈值，只选择前30%的特征
            q = 100 - int(proportion)
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

        selected_features = self.dataFrame.columns[selected_features_indices]
        newColumnsList = []
        for feature in selected_features:
            new_column_name = self.getHandledField(feature)
            self.dataFrame[new_column_name] = self.dataFrame[feature]
            newColumnsList.append(new_column_name)
        return self.dataFrame, ','.join(newColumnsList)

    # Pearson相关分析
    def Pearson(self, methodParam):
        # param:['年 DayOfYear 上级单位 测报站点', '0.9']
        # param1:所有变量
        # param2:提取条件

        # 保存字段名称对应系数值,用于返回热力图显示
        tempDict = {}
        # 筛选后的字段
        newColumns = []
        print('============测试============')
        print(methodParam)
        fieldList = methodParam[0].split(' ')
        condition = methodParam[1]
        # print(pValue)
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 遍历输入变量进行pearson分析
        tempResultP = {}
        # 选择需要计算相关性的列
        data = newDataFrame[fieldList]

        # 计算相关性矩阵
        correlation_matrix = data.corr()

        for i in range(len(fieldList)):
            for j in range(i + 1, len(fieldList)):
                var1 = fieldList[i]
                var2 = fieldList[j]
                correlation = correlation_matrix.loc[var1, var2]
                # print(f"变量 '{var1}' 和 '{var2}' 之间的相关系数: {correlation}")
                tempResultP[(var1, var2)] = correlation

        # 删选p-value符合条件的特征
        # 提取所有特征
        features = set()
        for key_pair in tempResultP.keys():
            features.update(key_pair)

        # 初始化保留的特征集合
        selected_features = set(features)

        # 遍历相关系数字典，移除相关系数大于(0.8)的特征
        for (feature1, feature2), correlation in tempResultP.items():
            if abs(correlation) > float(condition):
                # 默认移除后一个特征
                if feature2 in selected_features:
                    selected_features.remove(feature2)
        # 获取优选特征集
        newColumnsList = []
        selected_features_list = list(selected_features)
        for feature in selected_features_list:
            new_column_name = self.getHandledField(feature)
            self.dataFrame[new_column_name] = self.dataFrame[feature]
            newColumnsList.append(new_column_name)
        return self.dataFrame, correlation_matrix, newColumnsList
