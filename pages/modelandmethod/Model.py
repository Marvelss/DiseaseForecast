"""
@Author : SakuraFox
@Time: 2024-02-29 15:41
@File : Model.py
@Description : 模型训练算法及相关设置参数
"""
import os

import joblib
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.cross_decomposition import PLSRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score, cohen_kappa_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import math
import operator
from scipy.stats import norm
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
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in self.featureVariable:
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # =======================划分训练集和测试集=======================
        partition = 0.2
        if self.dataPartitioning == '8:2':
            partition = 0.2
        elif self.dataPartitioning == '7:3':
            partition = 0.3
        elif self.dataPartitioning == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]

        # 转换参数格式
        if 'C' in parameters_dict:
            parameters_dict['C'] = float(parameters_dict['C'])
        # print(parameters_dict)
        # 使用SVM回归模型进行拟合
        model1 = svm.SVC(**parameters_dict)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        print('y_pred:')
        print(actualAndPredictResult)
        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        if ',' in self.evaluationIndicator:
            tempIndicator = self.evaluationIndicator.split(',')
        else:
            tempIndicator = [tempIndicator]
        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'MSE':
                precision['MSE'] = mean_squared_error(y_test, y_pred)
            # 计算R方
            elif temp == 'R方':
                precision['R方'] = r2_score(y_test, y_pred)
            # 计算OA
            elif temp == 'OA':
                precision['OA'] = accuracy_score(y_test, y_pred)
            # 计算Kappa
            elif temp == 'Kappa':
                precision['Kappa'] = cohen_kappa_score(y_test, y_pred)

        # =======================保存结果-模型结构+预测结果+评价指标结果=======================
        # 保存模型
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelsResults')
        joblib.dump(model1, os.path.join(
            rootPath, 'modelsStructure', 'SVM_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath, 'predictAndTestLabel')
        savePath1 = os.path.join(savePathDir, 'SVM_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'SVM_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath, 'precision', 'SVM_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult

    def onKNN(self):

        # 训练模型
        # =======================获取数据集=======================
        df11 = self.dataFrame
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in self.featureVariable:
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # =======================划分训练集和测试集=======================
        partition = 0.2
        if self.dataPartitioning == '8:2':
            partition = 0.2
        elif self.dataPartitioning == '7:3':
            partition = 0.3
        elif self.dataPartitioning == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)
        # 使用SVM回归模型进行拟合
        model1 = KNeighborsClassifier(n_neighbors=3)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        print('y_pred:')
        print(actualAndPredictResult)
        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        if ',' in self.evaluationIndicator:
            tempIndicator = self.evaluationIndicator.split(',')
        else:
            tempIndicator = [tempIndicator]
        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'MSE':
                precision['MSE'] = mean_squared_error(y_test, y_pred)
            # 计算R方
            elif temp == 'R方':
                precision['R方'] = r2_score(y_test, y_pred)
            # 计算OA
            elif temp == 'OA':
                precision['OA'] = accuracy_score(y_test, y_pred)
            # 计算Kappa
            elif temp == 'Kappa':
                precision['Kappa'] = cohen_kappa_score(y_test, y_pred)

        # =======================保存结果-模型结构+预测结果+评价指标结果=======================
        # 保存模型
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelsResults')
        joblib.dump(model1, os.path.join(
            rootPath, 'modelsStructure', 'KNN_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath, 'predictAndTestLabel')
        savePath1 = os.path.join(savePathDir, 'KNN_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'KNN_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath, 'precision', 'KNN_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult

    def onFLDA(self):
        # 训练模型
        # =======================获取数据集=======================
        df11 = self.dataFrame
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in self.featureVariable:
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # =======================划分训练集和测试集=======================
        partition = 0.2
        if self.dataPartitioning == '8:2':
            partition = 0.2
        elif self.dataPartitioning == '7:3':
            partition = 0.3
        elif self.dataPartitioning == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]

        # print(parameters_dict)
        # 使用FLDA回归模型进行拟合
        model1 = LinearDiscriminantAnalysis()
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        print(actualAndPredictResult)
        print('y_pred:')
        # print(y_pred)
        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        if ',' in self.evaluationIndicator:
            tempIndicator = self.evaluationIndicator.split(',')
        else:
            tempIndicator = [tempIndicator]
        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'MSE':
                precision['MSE'] = mean_squared_error(y_test, y_pred)
            # 计算R方
            elif temp == 'R方':
                precision['R方'] = r2_score(y_test, y_pred)
            # 计算OA
            elif temp == 'OA':
                precision['OA'] = accuracy_score(y_test, y_pred)
            # 计算Kappa
            elif temp == 'Kappa':
                precision['Kappa'] = cohen_kappa_score(y_test, y_pred)

        # =======================保存结果-模型结构+预测结果+评价指标结果=======================
        # 保存模型
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelsResults')
        joblib.dump(model1, os.path.join(
            rootPath, 'modelsStructure', 'FLDA_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath, 'predictAndTestLabel')
        savePath1 = os.path.join(savePathDir, 'FLDA_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'FLDA_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath, 'precision', 'FLDA_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult

    def onRF(self):
        # 训练模型
        # =======================获取数据集=======================
        df11 = self.dataFrame
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in self.featureVariable:
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # =======================划分训练集和测试集=======================
        partition = 0.2
        if self.dataPartitioning == '8:2':
            partition = 0.2
        elif self.dataPartitioning == '7:3':
            partition = 0.3
        elif self.dataPartitioning == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)
        # 使用RF回归模型进行拟合
        model1 = RandomForestClassifier(n_estimators=100, random_state=42)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        print('y_pred:')
        print(actualAndPredictResult)
        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        if ',' in self.evaluationIndicator:
            tempIndicator = self.evaluationIndicator.split(',')
        else:
            tempIndicator = [tempIndicator]
        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'MSE':
                precision['MSE'] = mean_squared_error(y_test, y_pred)
            # 计算R方
            elif temp == 'R方':
                precision['R方'] = r2_score(y_test, y_pred)
            # 计算OA
            elif temp == 'OA':
                precision['OA'] = accuracy_score(y_test, y_pred)
            # 计算Kappa
            elif temp == 'Kappa':
                precision['Kappa'] = cohen_kappa_score(y_test, y_pred)

        # =======================保存结果-模型结构+预测结果+评价指标结果=======================
        # 保存模型
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelsResults')
        joblib.dump(model1, os.path.join(
            rootPath, 'modelsStructure', 'RF_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath, 'predictAndTestLabel')
        savePath1 = os.path.join(savePathDir, 'RF_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'RF_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath, 'precision', 'RF_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult

    def onSEIR(self, ka, kb, kc, q, r, OPT_PRI, YZQ_num, YZQ_txt, YZQ_data, ZB_num, ZB_data, met_num, met_txt, met_data,
               Jizhi_num, Jizhi_data):
        [yzq_row, yzq_col] = YZQ_data.shape
        D = []
        # ==========================地点匹配==========================
        for i in range(0, yzq_row):
            ida = operator.eq(YZQ_data.values[i, 1], met_txt.values[:, 1])
            aimrow = np.where(ida[:] == 1)  # 找到移栽期表格第i行地点对应的气象数据
            # aimplace_met = []
            aimplace_met_num = []
            # gc.disable()
            for j in aimrow[0]:
                # aimplace_met.append(met_data.values[j, :])
                aimplace_met_num.append(met_num.values[j, :])
            # gc.enable()
            # del aimrow
            idb = operator.eq(YZQ_data.values[i, 1], ZB_data.values[:, 4])
            idb = np.array(idb)
            aimrow1 = np.where(idb[:] == 1)  # 找到移栽期表格第i行对应的植保数据

            aimplace_ZB = []
            aimplace_ZB_num = []
            for p in aimrow1[0]:
                aimplace_ZB.append(ZB_data.values[p, :])
                aimplace_ZB_num.append(ZB_num.values[p, :])
                # print(ZB_num)
            idc = operator.eq(YZQ_data.values[i, 1], Jizhi_data.values[:, 1])
            idc = np.array(idc)
            aimrowjizhi = np.where(idc[:] == 1)  # 找到移栽期第i行对应的地点所有年份的极值
            Jizhi4 = []
            for p in aimrowjizhi[0]:
                Jizhi4.append(Jizhi_num.values[p, :])
            Jizhi4 = np.array(Jizhi4)
            # ==========================时间匹配==========================
            for ii in range(2010, 2017):
                temp = np.array(aimplace_ZB_num)
                # print(aimplace_ZB_num)
                aimrow3 = np.where(temp[:, 0] == ii)
                if np.size(aimrow3) != 0:
                    temp1 = np.array(aimplace_met_num)
                    aimrow2 = np.where(temp1[:, 0] == ii)
                    aimplace_aimyear_met_num = []

                    aimplace_aimyear_ZB = []
                    aimplace_aimyear_ZB_num = []
                    for p in aimrow2[0]:
                        aimplace_aimyear_met_num.append(aimplace_met_num[p])
                    for p in aimrow3[0]:
                        aimplace_aimyear_ZB.append(aimplace_ZB[p])
                        aimplace_aimyear_ZB_num.append(aimplace_ZB_num[p])
                    aimpyzbnumrow = len(aimplace_aimyear_ZB_num)
                    startday = YZQ_num.values[i, 2]
                    endday = aimplace_aimyear_ZB_num[aimpyzbnumrow - 1][18]
                    tmp = np.array(aimplace_aimyear_met_num)
                    e1 = tmp[startday - 5:endday, :]  # 具体日期
                    e = e1[:, [2, 3]]
                    [erow, _] = e.shape
                    # ==========================SEIR模型预测==========================
                    # 潜伏期参数
                    W = 1 / 3
                    # 感染期参数
                    U = 1 / q
                    dt = 1  # 微分方程自变量梯度
                    n = erow - 4  # 模型预测区间长度
                    n1 = erow
                    t = np.zeros([1, n])
                    H = np.zeros([1, n])
                    L = np.zeros([1, n])
                    I = np.zeros([1, n])
                    R = np.zeros([1, n])
                    t[0, 0] = 0
                    H[0, 0] = 0.9997  # H初始值
                    L[0, 0] = 0.0001
                    I[0, 0] = 0.0001
                    R[0, 0] = 0.0001
                    B = []
                    # 若相对湿度>阈值，则赋值为1，否则赋值为0
                    for k in range(5, n1 + 1):
                        e1 = e[k - 5:k, 0]  # 前5天的降水
                        e2 = e[k - 3:k, 1]  # 前3天，潜伏期为3天
                        e_PRI = sum(e1)
                        e_TEM = np.mean(e2)
                        # logistic函数,取值在0.01-1
                        PRI = 1 + (0.001 - 1) / (1 + math.exp((e_PRI - OPT_PRI) / r))
                        # 基于正态分布函数确定温度的响应,各参数为函数横坐标取值范围
                        x = np.linspace(0, 43, 44)
                        # 生成均值为28,方差为kc的正态分布函数
                        y = norm.pdf(x, 28, kc)  # 使用了SciPy中的norm函数，pdf表示概率密度函数。
                        # 这一行代码计算了在均值为28，标准差为kc的正态分布下，
                        # 对x中每一个值的概率密度函数值。
                        # 这意味着y数组中的每个元素都代表了在给定正态分布下对应x值的概率密度
                        MAX = max(y)
                        MIN = min(y)
                        # 对温度的响应进行归一化处理
                        TEM = (y[math.floor(e_TEM)] - MIN) / (MAX - MIN)
                        AGE = k / n  # 年龄的响应
                        # 三个修正量将温度、湿度和作物生育期的影响纳入模型，分别为T、W和A
                        # 对于下面参数TEM/PRI/AGE，详见张雪雪论文-式（4.3）
                        B1 = ka * 0.46 * PRI * TEM * AGE + kb
                        B.append(B1)  # 将每个时相对应的参数取值放到一个矩阵中
                    # 模型的微分方程迭代计算
                    for g in range(0, n - 1):
                        # SEIR
                        t[0, g + 1] = t[0, g] + dt
                        H[0, g + 1] = H[0, g] + dt * (-B[g] * H[0, g] * I[0, g])
                        L[0, g + 1] = L[0, g] + dt * (B[g] * H[0, g] * I[0, g] - W * L[0, g])
                        I[0, g + 1] = I[0, g] + dt * (W * L[0, g] - U * I[0, g])
                        R[0, g + 1] = R[0, g] + dt * (U * I[0, g])
                    # 发病情况的组成
                    y2 = (R + I)
                    y1 = np.transpose(y2)  # 转置
                    # 在某地点某年份的预测结果中提取与实际植保数据对应的预测数据
                    aimplace_aimyear_row = len(aimplace_aimyear_ZB)
                    # C = []
                    for a in range(0, aimplace_aimyear_row):
                        # 计算实际植保数据时相相对于移栽期的相对位置
                        z = aimplace_aimyear_ZB_num[a][18] - YZQ_num.values[i, 2]
                        if z > erow:
                            z = erow - 1
                        else:
                            if z < 0 or z == 0:
                                z = 0  # z=1
                            else:
                                z = z
                        temp2 = np.array(Jizhi4)
                        # 找到对应年份的目标地区峰值
                        aimjzrow = np.where(temp2[:, 2] == ii)
                        aimJizhi = Jizhi4[aimjzrow, 0]
                        # 预测结果乘以权重（极值）
                        D.append(y1[z, 0] * aimJizhi)

        # 计算R方和RMSE
        ZB1 = ZB_num
        R2_List = []
        RMSE_List_Temp = []
        [RowZB, ColZB] = ZB1.shape
        for s in range(0, RowZB):
            # 残差平方和
            res_fenzi = np.power((ZB1.values[s, 14] - D[s]), 2)  # np.power((ZB1.values[s - 1, 14] - D[s]), 2)
            # 平方和
            average_Y = np.mean(ZB1.values[:, 14])  # 假设ZB1.values[:, 14]是你的观察值
            SS_tot = sum(np.power(ZB1.values[:, 14] - average_Y, 2))

            R2_List.append(1 - res_fenzi / SS_tot)
            RMSE_List_Temp.append(res_fenzi)
        RMSE_FENZI = sum(RMSE_List_Temp)
        RMSE = (RMSE_FENZI / RowZB) ** 0.5
        # R3 = np.corrcoef(ZB1.values[:, 14], D)
        # R2 = np.power(R3, 2)

        return R2_List, RMSE, D

    def onPLSR(self):
        # 训练模型
        # =======================获取数据集=======================
        df11 = self.dataFrame
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in self.featureVariable:
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # =======================划分训练集和测试集=======================
        partition = 0.2
        if self.dataPartitioning == '8:2':
            partition = 0.2
        elif self.dataPartitioning == '7:3':
            partition = 0.3
        elif self.dataPartitioning == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)
        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        # 合并参数名称和值
        params = self.modelParam
        # print(params['参数名'].keys())
        parameters_dict = {}
        for key in params['参数名']:
            # Get the parameter name and value using the key
            param_name = str(params['参数名'][key])
            param_value = str(params['参数值'][key])
            # Store them in the new dictionary
            parameters_dict[param_name] = param_value
        print(parameters_dict)
        # 使用PLSR回归模型进行拟合
        model1 = PLSRegression(n_components=2)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        if ',' in self.evaluationIndicator:
            tempIndicator = self.evaluationIndicator.split(',')
        else:
            tempIndicator = [tempIndicator]
        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'MSE':
                precision['MSE'] = mean_squared_error(y_test, y_pred)
            # 计算R方
            elif temp == 'R方':
                precision['R方'] = r2_score(y_test, y_pred)
            # 计算OA
            elif temp == 'OA':
                precision['OA'] = accuracy_score(y_test, y_pred)
            # 计算Kappa
            elif temp == 'Kappa':
                precision['Kappa'] = cohen_kappa_score(y_test, y_pred)

        # =======================保存结果-模型结构+预测结果+评价指标结果=======================
        # 保存模型
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelsResults')
        joblib.dump(model1, os.path.join(
            rootPath, 'modelsStructure', 'PLSR_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath, 'predictAndTestLabel')
        savePath1 = os.path.join(savePathDir, 'PLSR_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'PLSR_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath, 'precision', 'PLSR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult

    def onLR(self):
        # 训练模型
        # =======================获取数据集=======================
        df11 = self.dataFrame
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in self.featureVariable:
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # =======================划分训练集和测试集=======================
        partition = 0.2
        if self.dataPartitioning == '8:2':
            partition = 0.2
        elif self.dataPartitioning == '7:3':
            partition = 0.3
        elif self.dataPartitioning == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)
        # 使用LR回归模型进行拟合
        model1 = LinearRegression()
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        print('y_pred:')
        print(actualAndPredictResult)
        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        if ',' in self.evaluationIndicator:
            tempIndicator = self.evaluationIndicator.split(',')
        else:
            tempIndicator = [tempIndicator]
        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'MSE':
                precision['MSE'] = mean_squared_error(y_test, y_pred)
            # 计算R方
            elif temp == 'R方':
                precision['R方'] = r2_score(y_test, y_pred)
            # 计算OA
            elif temp == 'OA':
                precision['OA'] = accuracy_score(y_test, y_pred)
            # 计算Kappa
            elif temp == 'Kappa':
                precision['Kappa'] = cohen_kappa_score(y_test, y_pred)

        # =======================保存结果-模型结构+预测结果+评价指标结果=======================
        # 保存模型
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelsResults')
        joblib.dump(model1, os.path.join(
            rootPath, 'modelsStructure', 'LR_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath, 'predictAndTestLabel')
        savePath1 = os.path.join(savePathDir, 'LR_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'LR_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath, 'precision', 'LR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult

    def onSVR(self):
        # 训练模型
        # =======================获取数据集=======================
        df11 = self.dataFrame
        X = df11[self.featureVariable]
        Y = df11[self.targetVariable]
        # 对分类变量进行one-hot编码
        if '上级单位' and '测报站点' in self.featureVariable:
            X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # =======================划分训练集和测试集=======================
        partition = 0.2
        if self.dataPartitioning == '8:2':
            partition = 0.2
        elif self.dataPartitioning == '7:3':
            partition = 0.3
        elif self.dataPartitioning == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)
        # 使用SVM回归模型进行拟合
        model1 = SVR(kernel='linear')
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        print('y_pred:')
        print(actualAndPredictResult)
        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        if ',' in self.evaluationIndicator:
            tempIndicator = self.evaluationIndicator.split(',')
        else:
            tempIndicator = [tempIndicator]
        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'MSE':
                precision['MSE'] = mean_squared_error(y_test, y_pred)
            # 计算R方
            elif temp == 'R方':
                precision['R方'] = r2_score(y_test, y_pred)
            # 计算OA
            elif temp == 'OA':
                precision['OA'] = accuracy_score(y_test, y_pred)
            # 计算Kappa
            elif temp == 'Kappa':
                precision['Kappa'] = cohen_kappa_score(y_test, y_pred)

        # =======================保存结果-模型结构+预测结果+评价指标结果=======================
        # 保存模型
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelsResults')
        joblib.dump(model1, os.path.join(
            rootPath, 'modelsStructure', 'SVR_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath, 'predictAndTestLabel')
        savePath1 = os.path.join(savePathDir, 'SVR_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'SVR_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath, 'precision', 'SVR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult
