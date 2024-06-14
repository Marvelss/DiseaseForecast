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
    def tTest(self, inputFields, methodParam):
        pValue = methodParam[0][1]
        # print(pValue)
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        print('============测试============')
        print(newDataFrame)
        print(inputFields[0])
        print(inputFields[1])
        # 创建一个空列表来存储显著的降水特征
        # significant_features = []
        # 计算 t 检验的 p 值，并选择 p < 0.05 的特征
        # print(fieldName)
        # print('--------------fieldName--------------')
        # 修改优选特征名称
        newDataColumn = self.getHandledField(inputFields)
        if pValue == '0.05':
            pass
        t_stat, p_value = stats.ttest_ind(
            newDataFrame[inputFields[0]],
            newDataFrame[inputFields[1]])
        print('======================特征优选-t检验结果======================')
        print(t_stat, p_value)
        tempData = newDataFrame[self.reservedField + inputFields]
        return tempData

    # RF互相关分析
    def ReliefF(self, inputFields, methodParam):
        target = methodParam[0][0]
        name = methodParam[0][1]
        proportion = methodParam[0][2]
        # 准备数据
        X = self.dataFrame[inputFields].drop(columns=[target])  # 假设我们已经从df中删除了目标列和不需要的列
        y = self.dataFrame[target]
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
        # 保存字段名称对应系数值,用于返回热力图显示
        tempDict = {}
        # 筛选后的字段
        newColumns = []
        print('============测试============')
        print(methodParam)
        objectField = methodParam[0]
        selectedFeature = methodParam[1].split(' ')
        coefficientStandard = methodParam[2].split('>')[1]
        # print(pValue)
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 遍历输入变量进行pearson分析
        for temp in selectedFeature:
            df_cleaned = newDataFrame[['上级单位', '测报站点', '年', temp, objectField]].dropna()
            # print(df_cleaned)
            pearson_corr_value, a = stats.pearsonr(
                df_cleaned[temp], df_cleaned[objectField])
            # print(pearson_corr_value)
            # print(coefficientStandard)
            tempDict[temp] = pearson_corr_value
            # 判断是否符合筛选条件
            if pearson_corr_value < float(coefficientStandard):
                # 字段名称添加_优选
                newDataColumn = self.getHandledField(temp)
                newDataFrame[newDataColumn] = newDataFrame[temp]
                newColumns.append(newDataColumn)
        return newDataFrame[self.reservedField + newColumns], newColumns
