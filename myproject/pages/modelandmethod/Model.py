"""
@Author : SakuraFox
@Time: 2024-02-29 15:41
@File : Model.py
@Description : 模型训练算法及相关设置参数
"""
import os

import joblib
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
from sklearn.svm import SVR

from lib.share import RESOURCE_MODELRESULT_PATH
from .seir_parameter_search.binary2decimal import binary2decimal
from .seir_parameter_search.cal_objvalue import cal_objvalue_run
from .seir_parameter_search.crossover import crossover
from .seir_parameter_search.mutation import mutation
from .seir_parameter_search.selection import selection
from .seir_parameter_search.initpop import initpop


class Model:
    def __init__(self, dataFrame, featureVariable, targetVariable,
                 dataPartitioning, modelParam, evaluationIndicator):
        self.dataFrame = dataFrame
        self.targetVariable = targetVariable
        self.featureVariable = featureVariable
        self.dataPartitioning = dataPartitioning
        self.evaluationIndicator = evaluationIndicator
        self.modelParam = modelParam
        # 模型结果保存路径:模型结构 + 预测结果 + 评价指标结果
        self.modelsStructurePath = os.path.join(RESOURCE_MODELRESULT_PATH, 'structure')
        self.modelsPredictPath = os.path.join(RESOURCE_MODELRESULT_PATH, 'predict')
        self.modelsPrecisionPath = os.path.join(RESOURCE_MODELRESULT_PATH, 'precision')

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
        # print('======================模型构建-开始训练======================')
        # print(self.modelParam)
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
        # print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        # print('y_pred:')
        # print(actualAndPredictResult)
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
        modelStruct = 'SVM_structure.pkl'
        joblib.dump(model1, os.path.join(
            self.modelsStructurePath, modelStruct))
        # 保存预测结果
        actualAndPredictResult = 'SVM_predictLabel.xlsx'
        savePath1 = os.path.join(self.modelsPredictPath, actualAndPredictResult)
        savePath2 = os.path.join(self.modelsPredictPath, 'SVM_testLabel.xlsx')
        pd.DataFrame(pd.concat([X_test, y_pred]),
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(self.modelsPrecisionPath, 'SVM_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult, modelStruct

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
        # print('======================模型构建-开始训练======================')
        # print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # # 转换参数格式
        if 'n_neighbors' in parameters_dict:
            parameters_dict['n_neighbors'] = int(parameters_dict['n_neighbors'])
        if 'leaf_size' in parameters_dict:
            parameters_dict['max_iter'] = int(parameters_dict['max_iter'])
        if 'n_jobs' in parameters_dict:
            parameters_dict['max_iter'] = int(parameters_dict['max_iter'])
        # 使用KNN回归模型进行拟合
        model1 = KNeighborsClassifier(**parameters_dict)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        # print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        # print('y_pred:')
        # print(actualAndPredictResult)
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
        modelStruct = 'KNN_structure.pkl'
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelresult')
        joblib.dump(model1, os.path.join(
            self.modelsStructurePath, modelStruct))
        # 保存预测结果
        actualAndPredictResult = 'KNN_predictLabel.xlsx'
        savePath1 = os.path.join(self.modelsPredictPath, actualAndPredictResult)
        savePath2 = os.path.join(self.modelsPredictPath, 'KNN_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(self.modelsPrecisionPath, 'KNN_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult, modelStruct

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
        # print('======================模型构建-开始训练======================')
        # print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # # 转换参数格式
        if 'store_covariance' in parameters_dict:
            parameters_dict['store_covariance'] = bool(parameters_dict['store_covariance'])
        # 使用KNN回归模型进行拟合
        # 使用FLDA回归模型进行拟合
        model1 = LinearDiscriminantAnalysis(**parameters_dict)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        # print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        # print(actualAndPredictResult)
        # print('y_pred:')
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
        modelStruct = 'FLDA_structure.pkl'
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelresult')
        joblib.dump(model1, os.path.join(
            self.modelsStructurePath, modelStruct))
        # 保存预测结果
        actualAndPredictResult = 'FLDA_predictLabel.xlsx'
        savePath1 = os.path.join(self.modelsPredictPath, )
        savePath2 = os.path.join(self.modelsPredictPath, 'FLDA_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(self.modelsPrecisionPath, 'FLDA_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult, modelStruct

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
        # print('======================模型构建-开始训练======================')
        # print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)
        # # 转换参数格式
        if 'n_estimators' in parameters_dict:
            parameters_dict['n_estimators'] = int(parameters_dict['n_estimators'])
        if 'min_samples_split' in parameters_dict:
            parameters_dict['min_samples_split'] = int(parameters_dict['min_samples_split'])
        # 使用RF回归模型进行拟合
        model1 = RandomForestClassifier(**parameters_dict)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        # print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        # print('y_pred:')
        # print(actualAndPredictResult)
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
        modelStruct = 'RF_structure.pkl'
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelresult')
        joblib.dump(model1, os.path.join(
            self.modelsStructurePath, modelStruct))
        # 保存预测结果
        actualAndPredictResult = 'RF_predictLabel.xlsx'
        savePath1 = os.path.join(self.modelsPredictPath, actualAndPredictResult)
        savePath2 = os.path.join(self.modelsPredictPath, 'RF_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(self.modelsPrecisionPath, 'RF_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult, modelStruct

    def onSEIR(self):

        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        precision = {}
        if ',' in self.evaluationIndicator:
            tempIndicator = self.evaluationIndicator.split(',')
        else:
            tempIndicator = [tempIndicator]

        array = self.modelParam
        param_values = array['参数值']
        paramT = param_values
        # print('------------测试参数------------')
        # print(self.modelParam)

        # "min_coefficient_ka": "1", "max_coefficient_ka": "4",
        # "min_coefficient_kb": "0", "max_coefficient_kb": "0.3", "min_coefficient_kc": "30",
        # "max_coefficient_kc": "60", "min_coefficient_OPT_PRI": "10", "max_coefficient_OPT_PRI": "30",
        # "min_coefficient_r": "10", "max_coefficient_r": "20",
        #      "min_coefficient_q": "50", "max_coefficient_q": "90", "ω": "3",
        #      "β0": "0.46", "optimumTEM": "28", "temStep": "3", "preStep": "5", "slideStep": "暂定",
        #      "loopNumbers": "1", "popSize": "20", "chromLength": "10", "pc": "0.6", "pm": "0.001"
        self.evaluationIndicator = 'evaluationIndicator'

        min_coefficient_ka = float(paramT[0])
        max_coefficient_ka = float(paramT[1])
        min_coefficient_kb = float(paramT[2])
        max_coefficient_kb = float(paramT[3])
        min_coefficient_kc = float(paramT[4])
        max_coefficient_kc = float(paramT[5])
        # 感染期
        min_coefficient_q = float(paramT[10])
        max_coefficient_q = float(paramT[11])
        min_coefficient_r = float(paramT[8])
        max_coefficient_r = float(paramT[9])
        min_coefficient_OPT_PRI = float(paramT[6])
        max_coefficient_OPT_PRI = float(paramT[7])

        w = float(paramT[12])
        beta0 = float(paramT[13])
        optimumTEM = float(paramT[14])
        # 内置模块
        temStep = float(paramT[15])
        preStep = float(paramT[16])

        slideStep = paramT[17]  # 后期若用添上float
        # 遗传算法参数
        loopNum = int(paramT[18])
        popSize = int(paramT[19])
        # 二进制编码长度(v=10)
        chromlength = int(paramT[20])
        # 交叉概率
        pc = float(paramT[21])
        # 变异概率
        pm = float(paramT[22])

        # 初始种群
        pop_ka = initpop(popSize, chromlength)
        pop_kb = initpop(popSize, chromlength)
        pop_kc = initpop(popSize, chromlength)
        pop_q = initpop(popSize, chromlength)
        pop_r = initpop(popSize, chromlength)
        pop_OPT_PRI = initpop(popSize, chromlength)

        # 编码
        pop2_ka_decimal2 = binary2decimal(pop_ka, min_coefficient_ka, max_coefficient_ka)  # 2进制转换为10进制
        pop2_kb_decimal2 = binary2decimal(pop_kb, min_coefficient_kb, max_coefficient_kb)
        pop2_kc_decimal2 = binary2decimal(pop_kc, min_coefficient_kc, max_coefficient_kc)
        pop2_q_decimal2 = binary2decimal(pop_q, min_coefficient_q, max_coefficient_q)
        pop2_r_decimal2 = binary2decimal(pop_r, min_coefficient_r, max_coefficient_r)
        pop2_OPT_PRI_decimal2 = binary2decimal(pop_OPT_PRI, min_coefficient_OPT_PRI, max_coefficient_OPT_PRI)

        objvalue2, objvalueR2First, allPredictList, allActualResultList = cal_objvalue_run(
            pop2_ka_decimal2, pop2_kb_decimal2,
            pop2_kc_decimal2, pop2_q_decimal2,
            pop2_r_decimal2, pop2_OPT_PRI_decimal2,
            w, beta0, optimumTEM, temStep, preStep,
            slideStep, self.dataFrame)
        fitvalue2 = objvalue2
        [px, py] = pop_ka.shape
        bestindividual_ka = pop_ka[0, :]
        bestindividual_kb = pop_kb[0, :]
        bestindividual_kc = pop_kc[0, :]
        bestindividual_q = pop_q[0, :]
        bestindividual_r = pop_r[0, :]
        bestindividual_OPT_PRI = pop_OPT_PRI[0, :]
        bestfit = fitvalue2[0]
        bestfitR2 = objvalueR2First[0]
        predictResult = allPredictList[0]
        # ActualResultList = allActualResultList

        for i in range(0, loopNum):  # 50
            print(f'--------------训练中:{str(i)}/{str(loopNum - 1)}--------------')
            pop2_ka_decimal = binary2decimal(pop_ka, min_coefficient_ka, max_coefficient_ka)
            pop2_kb_decimal = binary2decimal(pop_kb, min_coefficient_kb, max_coefficient_kb)
            pop2_kc_decimal = binary2decimal(pop_kc, min_coefficient_kc, max_coefficient_kc)
            pop2_q_decimal = binary2decimal(pop_q, min_coefficient_q, max_coefficient_q)
            pop2_r_decimal = binary2decimal(pop_r, min_coefficient_r, max_coefficient_r)
            pop2_OPT_PRI_decimal = binary2decimal(pop_OPT_PRI, min_coefficient_OPT_PRI, max_coefficient_OPT_PRI)
            objvalue1, objvalueR2, allPredictList2, _ = cal_objvalue_run(
                pop2_ka_decimal, pop2_kb_decimal,
                pop2_kc_decimal, pop2_q_decimal,
                pop2_r_decimal, pop2_OPT_PRI_decimal,
                w, beta0, optimumTEM, temStep, preStep,
                slideStep, self.dataFrame)
            fitvalue1 = objvalue1
            fitvalueR2 = objvalueR2
            for j in range(0, px):
                # if fitvalue1[j] < bestfit:
                # cal_objvalue_run中除了第一个元素,其他赋值都0
                if fitvalue1[j] < bestfit and fitvalue1[j] != 0:
                    bestindividual_ka = pop_ka[j, :]
                    bestindividual_kb = pop_kb[j, :]
                    bestindividual_kc = pop_kc[j, :]
                    bestindividual_q = pop_q[j, :]
                    bestindividual_r = pop_r[j, :]
                    bestindividual_OPT_PRI = pop_OPT_PRI[j, :]
                    bestfit = fitvalue1[j]
                    bestfitR2 = fitvalueR2[j]
                    predictResult = allPredictList2[j]
                    # ActualResultList = allActualResultList
            # print('-------------当前精度-------------')
            # print(f'RMSE:{fitvalue1}')
            # print(f'R方:{fitvalueR2}')
            # best_ka = binary2decimal(bestindividual_ka, min_coefficient_ka, max_coefficient_ka)
            # best_kb = binary2decimal(bestindividual_kb, min_coefficient_kb, max_coefficient_kb)
            # best_kc = binary2decimal(bestindividual_kc, min_coefficient_kc, max_coefficient_kc)
            # best_q = binary2decimal(bestindividual_q, min_coefficient_q, max_coefficient_q)
            # best_r = binary2decimal(bestindividual_r, min_coefficient_r, max_coefficient_r)
            # best_OPT_PRI = binary2decimal(bestindividual_OPT_PRI, min_coefficient_OPT_PRI, max_coefficient_OPT_PRI)
            # print('各项参数',
            #       f'best_ka:{best_ka}',
            #       f'best_kb:{best_kb}',
            #       f'best_kc:{best_kc}',
            #       f'best_q:{best_q}',
            #       f'best_r:{best_r}',
            #       f'best_OPT_PRI:{best_OPT_PRI}')
            print(f'优选精度RMSE:{bestfit}')
            print(f'优选精度R方:{bestfitR2}')

            # 选择操作
            newpop_ka = selection(pop_ka, fitvalue1)
            newpop_kb = selection(pop_kb, fitvalue1)
            newpop_kc = selection(pop_kc, fitvalue1)
            newpop_q = selection(pop_q, fitvalue1)
            newpop_r = selection(pop_r, fitvalue1)
            newpop_OPT_PRI = selection(pop_OPT_PRI, fitvalue1)
            # 交叉操作
            newpop_ka = crossover(newpop_ka, pc)
            newpop_kb = crossover(newpop_kb, pc)
            newpop_kc = crossover(newpop_kc, pc)
            newpop_q = crossover(newpop_q, pc)
            newpop_r = crossover(newpop_r, pc)
            newpop_OPT_PRI = crossover(newpop_OPT_PRI, pc)
            # 变异操作
            newpop_ka = mutation(newpop_ka, pm)
            newpop_kb = mutation(newpop_kb, pm)
            newpop_kc = mutation(newpop_kc, pm)
            newpop_q = mutation(newpop_q, pm)
            newpop_r = mutation(newpop_r, pm)
            newpop_OPT_PRI = mutation(newpop_OPT_PRI, pm)
            # 更新种群
            pop_ka = newpop_ka
            pop_kb = newpop_kb
            pop_kc = newpop_kc
            pop_q = newpop_q
            pop_r = newpop_r
            pop_OPT_PRI = newpop_OPT_PRI
        best_ka = binary2decimal(bestindividual_ka, min_coefficient_ka, max_coefficient_ka)
        best_kb = binary2decimal(bestindividual_kb, min_coefficient_kb, max_coefficient_kb)
        best_kc = binary2decimal(bestindividual_kc, min_coefficient_kc, max_coefficient_kc)
        best_q = binary2decimal(bestindividual_q, min_coefficient_q, max_coefficient_q)
        best_r = binary2decimal(bestindividual_r, min_coefficient_r, max_coefficient_r)
        best_OPT_PRI = binary2decimal(bestindividual_OPT_PRI, min_coefficient_OPT_PRI, max_coefficient_OPT_PRI)
        print('The best X is --->>%5.2f\n',
              f'best_ka:{best_ka}',
              f'best_kb:{best_kb}',
              f'best_kc:{best_kc}',
              f'best_q:{best_q}',
              f'best_r:{best_r}',
              f'best_OPT_PRI:{best_OPT_PRI}',
              f'bestfit:{bestfit}',
              f'bestfitR2:{bestfitR2}')
        temp = [best_ka, best_kb, best_kc, best_q, best_r, best_OPT_PRI, bestfitR2]
        RMSE, R2, modelStruct = bestfit, bestfitR2, temp

        for temp in tempIndicator:
            # 计算均方误差
            if temp == 'RMSE':
                precision['RMSE'] = RMSE[0]
            # 计算R方
            elif temp == 'R方':
                precision['R方'] = R2[0]

        # 保存模型结果
        modelStructPath = 'SEIR_structure.xlsx'
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelresult')
        modelStructPathT = os.path.join(self.modelsStructurePath, modelStructPath)
        # 对应的标签
        labels = ['ka', 'kb', 'kc', 'q', 'r', 'OPT_PRI', 'RMSE', 'R方']
        data = {label: result[0] for label, result in zip(labels, modelStruct)}
        # 创建 DataFrame
        df = pd.DataFrame([data])
        df.to_excel(modelStructPathT, index=False)

        # 保存预测结果
        actualAndPredictResult = 'SEIR机理模型_predictLabel.xlsx'
        savePath1 = os.path.join(self.modelsPredictPath, actualAndPredictResult)
        savePath2 = os.path.join(self.modelsPredictPath, 'SEIR机理模型_testLabel.xlsx')
        pd.DataFrame(predictResult,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        pd.DataFrame(allActualResultList,
                     columns=['实际病株率']).to_excel(
            savePath2, index=False)

        return precision, actualAndPredictResult, modelStructPath

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
        # print('======================模型构建-开始训练======================')
        # 合并参数名称和值
        params = self.modelParam
        param_names = params['参数名']
        param_values = params['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # # 转换参数格式
        if 'n_components' in parameters_dict:
            parameters_dict['n_components'] = int(parameters_dict['n_components'])
        if 'max_iter' in parameters_dict:
            parameters_dict['max_iter'] = int(parameters_dict['max_iter'])
        if 'scale' in parameters_dict:
            parameters_dict['scale'] = bool(parameters_dict['scale'])
        # print(parameters_dict)
        # 使用PLSR回归模型进行拟合
        model1 = PLSRegression(**parameters_dict)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        # print('======================模型构建-精度指标======================')
        precision = {}
        # actualAndPredictResult = y_pred.tolist()
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
        modelStruct = 'PLSR_structure.pkl'
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelresult')
        joblib.dump(model1, os.path.join(
            self.modelsStructurePath, modelStruct))
        # 保存预测结果
        actualAndPredictResult = 'PLSR_predictLabel.xlsx'
        savePath1 = os.path.join(self.modelsPredictPath, actualAndPredictResult)
        savePath2 = os.path.join(self.modelsPredictPath, 'PLSR_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(self.modelsPrecisionPath, 'PLSR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult, modelStruct

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
        # print('======================模型构建-开始训练======================')
        # print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)
        if 'fit_intercept' in parameters_dict:
            parameters_dict['fit_intercept'] = bool(parameters_dict['fit_intercept'])
        if 'alpha' in parameters_dict:
            parameters_dict['alpha'] = float(parameters_dict['alpha'])
        # 使用LR回归模型进行拟合
        model1 = LinearRegression(**parameters_dict)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        # print('======================模型构建-精度指标======================')
        precision = {}
        # actualAndPredictResult = y_pred.tolist()
        # print('y_pred:')
        # print(actualAndPredictResult)
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
        modelStruct = 'LR_structure.pkl'
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelresult')
        joblib.dump(model1, os.path.join(
            self.modelsStructurePath, modelStruct))
        # 保存预测结果
        actualAndPredictResult = 'LR_predictLabel.xlsx'
        savePath1 = os.path.join(self.modelsPredictPath, actualAndPredictResult)
        savePath2 = os.path.join(self.modelsPredictPath, 'LR_testLabel.xlsx')
        # 将 y_pred 转换为一个 Series 并命名为 'predictLabel'
        # y_pred = pd.Series(y_pred.flatten(), name='predictLabel', index=X_test.index)
        # 合并 X_test 和 y_pred
        # result = pd.concat([X_test, y_pred], axis=1)
        # 将合并后的 DataFrame 保存为 Excel 文件
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(self.modelsPrecisionPath, 'LR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult, modelStruct

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
        # print('======================模型构建-开始训练======================')
        # print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array['参数名']
        param_values = array['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)

        if 'epsilon' in parameters_dict:
            parameters_dict['epsilon'] = float(parameters_dict['epsilon'])
        if 'C' in parameters_dict:
            parameters_dict['C'] = float(parameters_dict['C'])
        # 使用SVM回归模型进行拟合
        model1 = SVR(**parameters_dict)
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        # print('======================模型构建-精度指标======================')
        precision = {}
        actualAndPredictResult = y_pred.tolist()
        # print('y_pred:')
        # print(actualAndPredictResult)
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
        modelStruct = 'SVR_structure.pkl'
        rootPath = os.path.join(os.getcwd(), 'resource', 'modelresult')
        joblib.dump(model1, os.path.join(
            self.modelsStructurePath, modelStruct))
        # 保存预测结果
        actualAndPredictResult = 'SVR_predictLabel.xlsx'
        savePath1 = os.path.join(self.modelsPredictPath, actualAndPredictResult)
        savePath2 = os.path.join(self.modelsPredictPath, 'SVR_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(self.modelsPrecisionPath, 'SVR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult, modelStruct
