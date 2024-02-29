"""
@Author : SakuraFox
@Time: 2024-02-29 15:41
@File : Model.py
@Description : 模型训练算法及相关设置参数
"""
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error
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
        # 训练模型
        # =======================获取数据集=======================
        df11 = self.dataFrame
        # print('--------训练表----------')
        # print(df11)
        # 提取特征和目标变量
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        X = pd.get_dummies(X, columns=['上级单位', '测报站点'])

        # =======================划分训练集和测试集=======================
        # X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, train_size=0.8, random_state=0)

        # =======================获取评价指标=======================

        # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 划分数据集为训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=0.2, random_state=42)

        print('======================模型构建-开始训练======================')
        # 使用SVM回归模型进行拟合
        model1 = SVR(kernel='rbf')
        model1.fit(X_train, y_train)

        # 进行预测
        y_pred = model1.predict(X_test)

        # 计算均方误差
        # mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        print(r2)
        # st.markdown('---')
        # st.markdown(y_test)
        # st.markdown(y_pred)
        print('======================模型构建-精度指标======================')
        # 计算Overall Accuracy
        # OA = accuracy_score(y_test, y_pred)
        # print(y_test)
        print('X_test:')
        print(X_test)
        print('y_pred:')
        print(y_pred)
        # kappa = cohen_kappa_score(y_test, y_pred)
        # st.markdown(mse)
        # print("Overall Accuracy:", OA)
        mse = mean_squared_error(y_test, y_pred)
        print("均方误差 :", mse)
        # print("均方误差:", mse)
