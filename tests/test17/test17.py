"""
@Author : SakuraFox
@Time: 2024-04-29 8:50
@File : test17.py
@Description : 测试-模型应用
"""
import pandas as pd
from sklearn.cross_decomposition import PLSRegression

import os

import joblib

from sklearn.metrics import r2_score, mean_squared_error, accuracy_score, cohen_kappa_score
from scipy.stats import stats
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from skrebate import ReliefF


class FeatureOptimizationMethod:
    def __init__(self, dataFrame, reservedField):
        self.dataFrame = dataFrame
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
        temp1 = methodParam.split(',')
        objectField = temp1[0]
        selectedFeature = temp1[1].split(' ')
        coefficientStandard = temp1[2].split('>')[1]
        # print(pValue)
        # 复制新的变量
        newDataFrame = self.dataFrame
        print(newDataFrame)
        # 遍历输入变量进行pearson分析
        for temp in selectedFeature:
            df_cleaned = newDataFrame[['上级单位', '测报站点', '年', temp, objectField]].dropna()
            # print(df_cleaned)
            print(temp)
            print(objectField)
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
        return newDataFrame[self.reservedField.tolist() + newColumns]


class Model:
    def __init__(self, dataFrame, featureVariable, targetVariable,
                 dataPartitioning, modelParam, evaluationIndicator):
        self.dataFrame = dataFrame
        self.targetVariable = targetVariable
        self.featureVariable = featureVariable
        self.dataPartitioning = dataPartitioning
        self.evaluationIndicator = evaluationIndicator
        self.modelParam = modelParam

    def onPLSR(self):
        print('=============方法接收=============')
        # print(self.evaluationIndicator)
        # print(self.dataPartitioning)
        # print(self.featureVariable)
        # print(self.targetVariable)
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
            rootPath, 'PLSR_structure.pkl'))
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
        precisionResultDir = os.path.join(rootPath, 'PLSR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult

    def onSVR(self):
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
            rootPath, 'SVR_structure.pkl'))
        # 保存预测结果
        savePathDir = os.path.join(rootPath)
        savePath1 = os.path.join(savePathDir, 'SVR_predictLabel.xlsx')
        savePath2 = os.path.join(savePathDir, 'SVR_testLabel.xlsx')
        pd.DataFrame(y_pred,
                     columns=['predictLabel']).to_excel(
            savePath1, index=False)
        y_test.to_excel(
            savePath2, index=False)
        # 保存评价指标
        precisionResultDir = os.path.join(rootPath, 'SVR_precision.xlsx')
        pd.DataFrame(precision.items(),
                     columns=['evaluationIndex', 'value']).to_excel(
            precisionResultDir, index=False)
        return precision, actualAndPredictResult


class FeatureCalculationMethod:
    def __init__(self, dataFrame, reservedField):
        self.dataFrame = dataFrame
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

    # 降水累积量计算
    def precipitationAccumulation(self, inputFields, param):
        temp = None
        startDate = None
        endDate = None
        timeRation = param.split(',')
        inputField = inputFields[0]
        flag = timeRation[0]
        # print(flag)
        if timeRation[1]:
            startDate = timeRation[1]
            endDate = timeRation[2]
        if flag == '月累积降水量':
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

            # 提取月份
            self.dataFrame['月'] = self.dataFrame['日期'].dt.month

            # 计算每月降水量总和
            monthly_precipitation_sum = self.dataFrame.groupby(['年', '月'])[inputField].sum().reset_index(
                name='降水累积量')

            # 将月降水量总和合并回原始DataFrame
            # 使用左连接保证所有原始记录都被保留
            temp = pd.merge(self.dataFrame, monthly_precipitation_sum, on=['年', '月'], how='left')
            # 删除'月','旬' '日期'字段
            temp = temp.drop(['月', '日期'], axis=1)
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
            temp = temp.drop(['旬', '日期'], axis=1)
        elif flag == '指定日期':
            # 指定日期范围（每年相同的日期）
            start_day = startDate
            end_day = endDate
            # print(self.dataFrame)
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
            print(temp)

        return temp


# =========================原始数据集=========================
df1 = pd.read_excel('气象数据-六省.xlsx')
df2 = pd.read_excel('病害峰值.xlsx')

# =========================特征计算及读取执行方法=========================
# 读取记录
featureCalculateDF = pd.read_excel('特征计算记录.xlsx')
inputFeature1 = featureCalculateDF["输入特征"].tolist()
# outputFeature1 = featureCalculateDF["备选特征"].tolist()
featureCalculateList = featureCalculateDF["特征计算方法"].tolist()
modelParam1 = featureCalculateDF["方法参数"].tolist()
print(modelParam1)

for indexT, tempMethod in enumerate(featureCalculateList):
    # 使用处理后最新的字段内容
    reservedField = df1.columns.tolist()
    print(f'=============测试保留字段-{reservedField}=============')
    tool1 = FeatureCalculationMethod(df1, reservedField)
    if tempMethod == '降雨日数计算':
        result1 = tool1.rainfallDaysAccumulation(
            inputFeature1[indexT], modelParam1[indexT])
    elif tempMethod == '降水累积量计算':
        result2 = tool1.precipitationAccumulation(
            inputFeature1[indexT], modelParam1[indexT])
        # result2.to_excel('handled' + str(indexT) + '.xlsx')

# 获得特征计算后结果
# print(result1)
# =========================合并数据集=========================
resul3 = pd.merge(result2, df2, on=['测报站点', '年'], how='left')
# temp.to_excel('merged.xlsx', index=False)

# =========================特征优选及读取执行方法=========================
featureOptimalDF = pd.read_excel('特征优选记录.xlsx')

inputFeature2 = featureOptimalDF["输入特征"].tolist()
outputFeature2 = featureOptimalDF["优选特征"].tolist()
featureOptimalList = featureOptimalDF["特征优选方法"].tolist()
modelParam2 = featureOptimalDF["方法参数"].tolist()
print(modelParam2)

tool2 = FeatureOptimizationMethod(resul3, resul3.columns)
# 初始化特征优选方法
for indexT, tempMethod in enumerate(featureOptimalList):
    reservedField = resul3.columns.tolist()
    afterHandleData = None
    # print(tempMethod)
    if tempMethod == 'Pearson相关性分析':
        afterHandleData = tool2.Pearson(
            modelParam2[indexT])
        # 获得特征计算后结果
        print(afterHandleData)
        afterHandleData.to_excel('handled2.xlsx')
    elif tempMethod == 'Relief-F互相关分析':
        afterHandleData = tool2.ReliefF(
            inputFeature2[0], modelParam2)

# =========================提取有效值=========================
# 使用groupby分组并提取每个分组的第一个非空值
ultimateFeatures = afterHandleData.groupby(['上级单位', '测报站点', '年']).first().reset_index()
# ******删除包含缺失值的行******
df_cleaned = ultimateFeatures.dropna()
# df_cleaned.to_excel('ultimateFeatures.xlsx')

# =========================模型构建及读取执行方法=========================
modelDF = pd.read_excel('模型记录.xlsx')

models = modelDF["模型"].tolist()
modelsParam = modelDF["模型参数"].tolist()
feature = modelDF["特征"].tolist()
label = modelDF["标签"].tolist()
precision = modelDF["评价指标"].tolist()
ratio = modelDF["数据集划分比例"].tolist()

# print(models)
# print(modelsParam)
# print(feature)
# print(label)
# print(precision)
# print(ratio)

for indexT, (tempModel, tempModelsParam
             , tempFeature,
             tempLabel, tempPrecision, tempRatio) in enumerate(zip(
    models, modelsParam, feature, label, precision, ratio)):
    evaluationIndicator = list(eval(tempPrecision).keys())
    tempFeature = eval(tempFeature)
    tempLabel = eval(tempLabel)
    tempModelsParam = [eval(tempModelsParam)]
    if tempModel == 'PLSR':
        evaluationResult, actualAndPredictResult = Model(
            df_cleaned, tempFeature,
            tempLabel, tempRatio,
            tempModelsParam,
            evaluationIndicator).onPLSR()
        print('PLSR:')
        print(evaluationResult)
    elif tempModel == 'LR':
        evaluationResult, actualAndPredictResult = Model(
            df_cleaned, tempFeature,
            tempLabel, tempRatio,
            tempModelsParam,
            evaluationIndicator).onLR()
        print(evaluationResult)
        # 显示模型训练结果信息
    elif tempModel == 'SVR':
        evaluationResult, actualAndPredictResult = Model(
            df_cleaned, tempFeature,
            tempLabel, tempRatio,
            tempModelsParam,
            evaluationIndicator).onSVR()
        print('======测试返回模型评价结果======')
        print('SVR:')
        print(evaluationResult)
