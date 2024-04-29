"""
@Author : SakuraFox
@Time: 2024-04-28 15:50
@File : test16.py
@Description : 测试-模型构建
原始数据字段:上级单位、测报站点、年、DayOfYear降水、温度、历史病害峰值
数据预处理:异常值剔除(暂无)
特征计算:01-01_01-20_降水累积量、01-21_01-31_降水累积量
特征优选:Pearson相关性分析
模型:PLSR
"""
from datetime import datetime

import pandas as pd
from scipy.stats import stats, pearsonr
import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from skrebate import ReliefF
import pandas as pd
from scipy.stats import stats, pearsonr
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from skrebate import ReliefF


# ==========================预处理==========================
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
        print('==========接收self.fieldName==========')
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 复制原处理字段,并在名称后添加_预处理后
        # newDataColumn = f"{self.fieldName}_预处理后"
        newDataColumn = self.getHandledField(self.fieldName)
        newDataFrame[newDataColumn] = newDataFrame[self.fieldName]
        missingValueBefore = newDataFrame[newDataColumn].isnull().sum()
        newDataFrame[newDataColumn] = newDataFrame[newDataColumn].interpolate()
        missingValueAfter = newDataFrame[newDataColumn].isnull().sum()
        # 检查是否还有缺失值
        print(F'=========检查数组并情况=========')
        # print(self.reservedField)
        print(self.fieldName)
        # print(self.reservedField + [self.fieldName])
        tempData = newDataFrame
        # tempData = newDataFrame[self.reservedField + [self.fieldName + '_预处理后']]
        return tempData, missingValueBefore, missingValueAfter, newDataColumn

    # 剔除异常值
    def outlierEliminator(self, methodParam):
        # 处理单个字段
        self.fieldName = self.fieldName[0]
        print(methodParam)
        minNum, maxNum = float(methodParam[1]), float(methodParam[0])
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        print(newDataFrame)

        newDataColumn = self.getHandledField(self.fieldName)
        newDataFrame[newDataColumn] = newDataFrame[self.fieldName]

        # 获取原始记录数
        lengthBefore = len(newDataFrame)
        # newDataFrame[self.fieldName] = newDataFrame[self.fieldName].clip(minNum, maxNum)
        newDataFrame = newDataFrame[
            (newDataFrame[self.fieldName] >= minNum) &
            (newDataFrame[self.fieldName] <= maxNum)]
        lengthAfter = len(newDataFrame)
        # 检查是否还有缺失值
        print('======到处理完数据集')
        print(newDataFrame)
        tempData = newDataFrame
        return tempData, str(lengthBefore - lengthAfter), lengthAfter, newDataColumn


# ==========================特征计算==========================
class FeatureCalculationMethod:
    def __init__(self, dataFrame, reservedField):
        self.dataFrame = dataFrame.copy()
        self.reservedField = reservedField

    # 旬值获取
    @staticmethod
    def get_decade(day):
        if day <= 10:
            return 1
        elif day <= 20:
            return 2
        else:
            return 3

    def precipitationAccumulation(self, inputFields, timeRation):
        temp = None
        startDate = None
        endDate = None
        inputField = inputFields[0]
        flag = timeRation[0]
        if timeRation[1]:
            startDate = timeRation[1]
            endDate = timeRation[2]
        # print(self.dataFrame)
        if flag == '月累积降水量':

            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 提取月份
            self.dataFrame['月'] = self.dataFrame['日期'].dt.month
            # 计算降水累积量
            self.dataFrame['降水累积量'] = self.dataFrame.groupby([
                '上级单位', '测报站点', '年', '月'])['降水'].transform('sum')
            temp = self.dataFrame
            # 使用左连接保证所有原始记录都被保留
            # temp = pd.merge(self.dataFrame, monthly_precipitation_sum, on=['年', '月'], how='left')
            # 删除'月','旬' '日期'字段
            # temp = temp.drop(['月', '日期'], axis=1)
        elif flag == '旬累积降水量':
            # 转换DayOfYear为日期，以便提取月份
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 提取月份
            self.dataFrame['月'] = self.dataFrame['日期'].dt.month

            # 计算每天所在的旬，假设1-10日为第一旬，11-20日为第二旬，21日至月末为第三旬

            self.dataFrame['旬'] = self.dataFrame['日期'].dt.day.apply(FeatureCalculationMethod.get_decade)

            # 计算每旬的累积降水量
            decade_precipitation_sum = self.dataFrame.groupby(['年', '月', '旬'])[inputField].sum().reset_index(
                name='降水累积量')

            # 将旬累积降水量合并回原始DataFrame
            temp = pd.merge(self.dataFrame, decade_precipitation_sum, on=['年', '月', '旬'], how='left')
            # 删除'月','旬' '日期'字段
            # temp = temp.drop(['旬', '日期'], axis=1)
        elif flag == '指定日期':
            # 指定日期范围（每年相同的日期）
            start_day = startDate
            end_day = endDate
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 转换日期到年内的日期格式，忽略年份
            self.dataFrame['年内日期'] = self.dataFrame['日期'].dt.strftime('%m-%d')

            # 过滤数据，只保留在指定日期范围内的记录
            date_filter = (self.dataFrame['年内日期'] >= start_day) & (self.dataFrame['年内日期'] <= end_day)
            filtered_df = self.dataFrame.loc[date_filter]

            # 计算每个分组在指定日期范围内的降水累积量
            sums = filtered_df.groupby(['上级单位', '测报站点', '年'])['降水'].sum()

            # 在原 DataFrame 上创建一个新列 '降水累积量'，初始值设置为 NaN
            newColumn = startDate + '_' + endDate + '_' + '降水累积量'
            self.dataFrame[newColumn] = pd.NA

            # 只为符合指定日期条件的行赋值累积降水量
            for index, total_precip in sums.items():
                match_condition = (self.dataFrame['上级单位'] == index[0]) & (
                        self.dataFrame['测报站点'] == index[1]) & (
                                          self.dataFrame['年'] == index[2]) & date_filter
                self.dataFrame.loc[match_condition, newColumn] = total_precip
            temp = self.dataFrame
        return temp

    # 计算降雨日数
    def rainfallDaysAccumulation(self, inputFields, param):
        # 复制新的变量
        print('===========接收参数===========')
        print(param)
        print(inputFields)
        startMD = param[0]
        tempS = startMD.split('-')
        startM, startD = int(tempS[1]), int(tempS[2])
        endMD = param[1]
        tempE = endMD.split('-')
        endM, endD = int(tempE[1]), int(tempE[2])
        rule = param[2]
        minNum = param[3]
        # duration = param[0][4]  # 暂未使用,默认1天
        # print(self.fieldName)
        if rule == '单日降水量':
            # 转换DayOfYear为日期
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) +
                self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
            # 根据上级单位、测报站点、年分类
            grouped = self.dataFrame.groupby(['上级单位', '测报站点', '年'])
            for (key, group) in grouped:
                start_date_range = datetime(key[2], startM, startD)
                end_date_range = datetime(key[2], endM, endD)
                rainy_days_count = len(
                    group[
                        (group['日期'] >= start_date_range) &
                        (group['日期'] <= end_date_range) &
                        (group[inputFields[0]] >= float(minNum))]
                )
                # print('==========具体明细==========')
                # print(group[
                #         (group['日期'] >= start_date_range) &
                #         (group['日期'] <= end_date_range) &
                #         (group[inputFields[0]] >= float(minNum))])
                # print(f'长度{rainy_days_count}')
                # Assign the calculated rainy days count to the '降雨日数' column within the specified date range
                mask = (self.dataFrame['上级单位'] == key[0]) & (self.dataFrame['测报站点'] == key[1]) & (
                        self.dataFrame['日期'] >= start_date_range) & (
                               self.dataFrame['日期'] <= end_date_range)
                self.dataFrame.loc[mask, '降雨日数'] = rainy_days_count

            # # 删除还没生成的字段
            # tempReservedField = [field for field in self.reservedField if field in self.dataFrame.columns]
            # print(f'==============降雨日数-筛选特征{tempReservedField}================')
            # tempData = self.dataFrame[list(set(tempReservedField + ['降雨日数']))]
            # 删除'月','旬' '日期'字段
            self.dataFrame = self.dataFrame.drop(['日期'], axis=1)
            return self.dataFrame


# ==========================特征优选==========================
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

        objectField = methodParam[0][0]
        selectedFeature = methodParam[0][1]
        coefficientStandard = methodParam[0][2].split('>')[1]
        # print(pValue)
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # print('============测试============')

        # 遍历输入变量进行pearson分析
        # print(inputFields)

        for temp in selectedFeature:
            pearson_corr_value, a = stats.pearsonr(
                newDataFrame[temp], newDataFrame[objectField])
            # print(pearson_corr_value)
            # print(coefficientStandard)
            tempDict[temp] = pearson_corr_value
            # 判断是否符合筛选条件
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
        return newDataFrame[self.reservedField + newColumns]


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
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score, cohen_kappa_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import math
import operator
from scipy.stats import norm


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
        print('=============方法接收=============')
        print(self.evaluationIndicator)
        print(self.dataPartitioning)
        print(self.featureVariable)
        print(self.targetVariable)
        print(self.dataFrame)
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
        if self.dataPartitioning[0] == '8:2':
            partition = 0.2
        elif self.dataPartitioning[0] == '7:3':
            partition = 0.3
        elif self.dataPartitioning[0] == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array[0]['参数名']
        param_values = array[0]['参数值']
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
        if ',' in self.evaluationIndicator[0]:
            tempIndicator = self.evaluationIndicator[0].split(',')
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
        print('=============方法接收=============')
        print(self.evaluationIndicator)
        print(self.dataPartitioning)
        print(self.featureVariable)
        print(self.targetVariable)
        print(self.dataFrame)
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
        if self.dataPartitioning[0] == '8:2':
            partition = 0.2
        elif self.dataPartitioning[0] == '7:3':
            partition = 0.3
        elif self.dataPartitioning[0] == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array[0]['参数名']
        param_values = array[0]['参数值']
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
        if ',' in self.evaluationIndicator[0]:
            tempIndicator = self.evaluationIndicator[0].split(',')
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
        print('=============方法接收=============')
        print(self.evaluationIndicator)
        print(self.dataPartitioning)
        print(self.featureVariable)
        print(self.targetVariable)
        print(self.dataFrame)
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
        if self.dataPartitioning[0] == '8:2':
            partition = 0.2
        elif self.dataPartitioning[0] == '7:3':
            partition = 0.3
        elif self.dataPartitioning[0] == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array[0]['参数名']
        param_values = array[0]['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]

        # print(parameters_dict)
        # 使用SVM回归模型进行拟合
        model1 = LinearDiscriminantAnalysis()
        model1.fit(X_train, y_train)
        # 进行预测
        y_pred = model1.predict(X_test)
        print('======================模型构建-精度指标======================')
        precision = {}
        # actualAndPredictResult = [savePath1, savePath2]
        actualAndPredictResult = y_pred.tolist()
        # 'predictLabel': ,
        # 'actualLabel': }
        print(actualAndPredictResult)
        # print('X_test:')
        # print(X_test)
        print('y_pred:')
        # print(y_pred)
        tempIndicator = self.evaluationIndicator
        # print(tempIndicator)
        if ',' in self.evaluationIndicator[0]:
            tempIndicator = self.evaluationIndicator[0].split(',')
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
        print('=============方法接收=============')
        print(self.evaluationIndicator)
        print(self.dataPartitioning)
        print(self.featureVariable)
        print(self.targetVariable)
        print(self.dataFrame)
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
        if self.dataPartitioning[0] == '8:2':
            partition = 0.2
        elif self.dataPartitioning[0] == '7:3':
            partition = 0.3
        elif self.dataPartitioning[0] == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)

        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array[0]['参数名']
        param_values = array[0]['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)
        # 使用SVM回归模型进行拟合
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
        if ',' in self.evaluationIndicator[0]:
            tempIndicator = self.evaluationIndicator[0].split(',')
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

    def onPLSR(self):
        # print('=============方法接收=============')
        # print(self.evaluationIndicator)
        # print(self.dataPartitioning)
        # print(self.featureVariable)
        # print(self.targetVariable)
        # print(self.dataFrame)
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
        if self.dataPartitioning[0] == '8:2':
            partition = 0.2
        elif self.dataPartitioning[0] == '7:3':
            partition = 0.3
        elif self.dataPartitioning[0] == '6:4':
            partition = 0.4
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, Y, test_size=partition, random_state=42)
        # =======================创建模型并开始训练=======================
        print('======================模型构建-开始训练======================')
        # print(self.modelParam)
        # 合并参数名称和值
        array = self.modelParam
        param_names = array[0]['参数名']
        param_values = array[0]['参数值']
        parameters_dict = {}
        for i in range(len(param_names)):
            parameters_dict[param_names[i]] = param_values[i]
        # print(parameters_dict)
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
        if ',' in self.evaluationIndicator[0]:
            tempIndicator = self.evaluationIndicator[0].split(',')
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
        rootPath = os.path.join(os.getcwd())
        joblib.dump(model1, os.path.join(
            rootPath,  'PLSR_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath)
        savePath1 = os.path.join(savePathDir, 'PLSR_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'PLSR_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath,  'PLSR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult


# ==================模型构建==================

# 原始数据
# df1 = pd.read_excel('气象数据-六省.xlsx')
# df2 = pd.read_excel('病害峰值.xlsx')

# 特征计算
# afterHandleData = FeatureCalculationMethod(
#     df1, df1.columns).precipitationAccumulation(
#     ['降水'], ['指定日期', '01-01', '01-20'])
# # afterHandleData.to_excel('result.xlsx', index=False)
# afterHandleData1 = FeatureCalculationMethod(
#     afterHandleData, afterHandleData.columns).precipitationAccumulation(
#     ['降水'], ['指定日期', '01-21', '01-31'])
# afterHandleData1.to_excel('result.xlsx', index=False)
# temp = pd.merge(afterHandleData1, df2, on=['测报站点', '年'], how='left')
# temp.to_excel('merged.xlsx', index=False)

# 特征优选-数据参考test15
# df = pd.read_excel('merged.xlsx')

# afterHandleData = FeatureOptimizationMethod(
#     df, df.columns).Pearson(
#     [['病害峰值'],
#      ['01-01_01-20_降水累积量', '01-21_01-31_降水累积量'],
#      '相关系数的绝对值>0.8'])
# afterHandleData.to_excel('optimalResult.xlsx')

# # ******读取优选后数据******
# df = pd.read_excel('optimalResult.xlsx')
# # 使用groupby分组并提取每个分组的第一个非空值
# result = df.groupby(['上级单位', '测报站点', '年']).first().reset_index()
# result.to_excel('dropped.xlsx')


# ******删除包含缺失值的行******
# df = pd.read_excel('dropped.xlsx')
# df_cleaned = df.dropna()
# df_cleaned.to_excel('result.xlsx')

# 根据上级单位、测报站点、年份和降水累积量优选特征进行分组，并提取唯一值
# 创建一个空列表，用于存储提取的数据
extracted_data = []

# # 遍历数据集
# for index, row in df.iterrows():
#     # 提取所需的列
#     upper_unit = row['上级单位']
#     station = row['测报站点']
#     year = row['年']
#     feature_01_01_to_01_20 = row['01-01_01-20_降水累积量_优选特征']
#     feature_01_21_to_01_31 = row['01-21_01-31_降水累积量_优选特征']
#     peak_value = row['病害峰值']
#
#     # 将提取的数据存储到列表中
#     extracted_data.append([upper_unit, station, year, feature_01_01_to_01_20, feature_01_21_to_01_31, peak_value])
#
# # 将提取的数据转换为DataFrame
# extracted_df = pd.DataFrame(extracted_data, columns=['上级单位', '测报站点', '年', '01-01_01-20_降水累积量_优选特征',
#                                                      '01-21_01-31_降水累积量_优选特征', '病害峰值'])
# extracted_df.to_excel('extracted_df.xlsx')
#


# from sklearn.preprocessing import StandardScaler
#
# # 加载数据
df = pd.read_excel('result-去温度.xlsx')
#
# # 分离自变量和响应变量
# X = data[['上级单位', '测报站点', '年', '01-21_01-31_降水累积量', '01-01_01-20_降水累积量', '温度']]
# y = data[['病害峰值']]
#
# if '上级单位' and '测报站点' in data.columns:
#     X = pd.get_dummies(X, columns=['上级单位', '测报站点'])  # 数据标准化
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)
# # 构建 PLSR 模型
# # pls = LinearRegression()
# pls = SVR(kernel='linear')
# pls.fit(X_scaled, y)
#
# # 预测响应变量
# y_pred = pls.predict(X_scaled)
# print(y_pred.flatten().tolist())

modelParam = [{'参数名': {0: 'n_estimators', 1: 'criterion', 2: 'gini'},
               '参数值': {0: '100', 1: 'gini', 2: '3'}}]
evaluationIndicator = ['MSE', 'R方']
evaluationResult, actualAndPredictResult = Model(
    df, ['上级单位', '测报站点', '年', '01-21_01-31_降水累积量', '01-01_01-20_降水累积量'],
    ['病害峰值'], '2:8',
    modelParam,
    evaluationIndicator).onPLSR()
print(evaluationResult, actualAndPredictResult)
