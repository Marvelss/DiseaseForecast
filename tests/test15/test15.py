"""
@Author : SakuraFox
@Time: 2024-04-28 15:11
@File : test15.py
@Description : 测试-特征优选
"""

import pandas as pd
from scipy.stats import stats, pearsonr
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
        print(f'接收参数-{target}-{name}-{proportion}-'
              f'{inputFields.to_list()}')
        newList = [item for item in inputFields.to_list() if item != '发生程度']
        print(self.dataFrame['发生程度'].value_counts())
        # 准备数据
        X = self.dataFrame.drop(columns=['发生程度'])  # 假设我们已经从df中删除了目标列和不需要的列
        y = self.dataFrame[['发生程度']]
        # X = self.dataFrame[newList]
        # y = self.dataFrame[[target]]
        # y= self.dataFrame[[target]].values.ravel()  # 如果y_train是DataFrame
        print(X)
        print(y)
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in self.dataFrame.columns.tolist():
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, stratify=y, random_state=42)

        # 初始化ReliefF算法
        fs = ReliefF(n_neighbors=4)  # n_neighbors参数根据数据集大小调整，n_features_to_keep是你想要保留的特征数量

        # 修改优选特征名称
        newDataColumn = self.getHandledField(inputFields)

        # 训练ReliefF模型以找到最重要的特征
        fs.fit(X_train, y_train)
        # 假设 fs.feature_importances_ 包含了特征的重要性得分
        feature_scores = fs.feature_importances_
        print(feature_scores)
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
        selected_features = self.dataFrame.columns[selected_features_indices]
        return self.dataFrame[selected_features + self.reservedField]

    # Pearson相关分析
    def Pearson(self, methodParam):
        # 保存字段名称对应系数值,用于返回热力图显示
        tempDict = {}
        # 筛选后的字段
        newColumns = []
        # print(methodParam[0])
        print(methodParam)
        objectField = methodParam[0][0]
        print(objectField)
        selectedFeature = methodParam[1]
        coefficientStandard = methodParam[2].split('>')[1]
        # print(pValue)
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()

        # print('============测试============')
        # 遍历输入变量进行pearson分析
        for temp in selectedFeature:
            df_cleaned = df[['上级单位', '测报站点', '年', temp, objectField]].dropna()
            df_cleaned.to_excel('dropped_' + temp + '.xlsx')
            print(temp, objectField)
            # print(len(df_cleaned[temp]))
            # print(len(df_cleaned[objectField]))
            pearson_corr_value, a = stats.pearsonr(
                df_cleaned[temp], df_cleaned[objectField])
            # print(pearson_corr_value)
            # print(coefficientStandard)
            tempDict[temp] = pearson_corr_value
            # 判断是否符合筛选条件
            print(pearson_corr_value, a)
            if pearson_corr_value < float(coefficientStandard):
                # 字段名称添加_优选
                newDataColumn = self.getHandledField(temp)
                newDataFrame[newDataColumn] = newDataFrame[temp]
                newColumns.append(newDataColumn)
        # print(newDataFrame)
        # print(newColumns)
        # # 返回包含筛选前的所有字段相关系数
        # pearson_corr = df[inputFields].corr(method='pearson')
        # # 绘制热力图
        # plt.rcParams['font.sans-serif'] = 'Microsoft Yahei'
        # sns.heatmap(pearson_corr, vmax=.8, square=True, annot=True)  # 画热力图   annot=True 显示系数
        # plt.show()

        return newDataFrame[self.reservedField.tolist() + newColumns]


df = pd.read_excel('merged.xlsx')

afterHandleData = FeatureOptimizationMethod(
    df, df.columns).Pearson(
    [['病害峰值'],
     ['01-01_01-20_降水累积量', '01-21_01-31_降水累积量'],
     '相关系数的绝对值>0.8'])
afterHandleData.to_excel('optimalResult.xlsx')
