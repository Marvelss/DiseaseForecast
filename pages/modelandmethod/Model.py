"""
@Author : SakuraFox
@Time: 2024-02-29 15:41
@File : Model.py
@Description : 模型训练算法及相关设置参数
"""
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score, cohen_kappa_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


class Model:
    def __init__(self, dataFrame, featureVariable, targetVariable,
                 dataPartitioning, modelParam, evaluationIndicator):
        self.dataFrame = dataFrame
        self.targetVariable = targetVariable
        self.featureVariable = featureVariable
        self.dataPartitioning = dataPartitioning
        self.evaluationIndicator = evaluationIndicator
        self.modelParam = modelParam

    def onSVM(self):
        print(self.evaluationIndicator)
        print(self.dataPartitioning)
        # 训练模型
        # =======================获取数据集=======================
        df11 = self.dataFrame
        print(self.featureVariable)
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # =======================划分训练集和测试集=======================
        partition = 0.2
        if self.dataPartitioning[0] == '8:2':
            partition = 0.2
        elif self.dataPartitioning[0] == '7:3':
            partition = 0.3
        elif self.dataPartitioning[0] == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        # 使用SVM回归模型进行拟合
        model1 = SVR(kernel='rbf')
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)

        # =======================获取评价指标=======================
        print('======================模型构建-精度指标======================')
        result = {}
        # print('X_test:')
        # print(X_test)
        # print('y_pred:')
        # print(y_pred)
        tempIndicator = self.evaluationIndicator
        if ',' in self.evaluationIndicator[0]:
            tempIndicator = self.evaluationIndicator[0].split(',')
        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'MSE':
                result['MSE'] = mean_squared_error(y_test, y_pred)
            # 计算R方
            elif temp == 'R2':
                result['R2'] = r2_score(y_test, y_pred)
            # 计算OA
            elif temp == 'OA':
                result['OA'] = accuracy_score(y_test, y_pred)
            # 计算Kappa
            elif temp == 'Kappa':
                result['Kappa'] = cohen_kappa_score(y_test, y_pred)
        return result
