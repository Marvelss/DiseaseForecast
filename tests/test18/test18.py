"""
@Author : SakuraFox
@Time: 2024-05-05 14:49
@File : test18.py
@Description : 测试-天气情景生成器-替换模拟数据
"""
import os

import joblib
import pandas as pd
from scipy.stats import stats
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
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


# 获取模型
def getModel(modelName):
    modelPathRoot = os.path.join(r'E:\a_python\program\diseaseForecastStreamlit',
                                 'resource',
                                 'modelsResults',
                                 'modelsStructure')
    modelPath = os.path.join(modelPathRoot, modelName + '_structure.pkl')
    print(modelPath)
    if os.path.exists(modelPath):
        # 加载已经训练好的模型
        return joblib.load(modelPath)
    else:
        return None


# 定义函数替换数据
def replace_data(df1, df2):
    # 根据条件筛选并替换原始数据表格中的值
    for index, row in df2.iterrows():
        condition = (df1['上级单位'] == row['上级单位']) & (df1['测报站点'] == row['测报站点']) & \
                    (df1['年'] == row['年']) & (df1['DayOfYear'] == row['DayOfYear'])
        df1.loc[condition, '降水'] = row['降水']
        df1.loc[condition, '温度'] = row['温度']
    return df1


# =========================原始数据集=========================
df1T = pd.read_excel('气象数据-六省.xlsx')
df2T = pd.read_excel('病害峰值.xlsx')

# =========================替换模拟气象数据=========================
# 用户输入:上级单位、测报站点、年份范围
province = '湖南省'
station = '湘阴县'
# sd, ed = '2010', '2010'

# 调用天气情景生成器,获取数据

# # 根据上级单位、测报站点、年份范围替换原始数据
# path1 = '第1年.xlsx'
# df3T = pd.read_excel(path1)
# df1 = replace_data(df1T, df3T)
# print('=========================替换后数据=========================')
# df1.to_excel('replaced.xlsx', index=False)
# # =========================特征计算及读取执行方法=========================
# # 读取记录
# featureCalculateDF = pd.read_excel('特征计算记录.xlsx')
# inputFeature1 = featureCalculateDF["输入特征"].tolist()
# # outputFeature1 = featureCalculateDF["备选特征"].tolist()
# featureCalculateList = featureCalculateDF["特征计算方法"].tolist()
# modelParam1 = featureCalculateDF["方法参数"].tolist()
# print(modelParam1)
#
# for indexT, tempMethod in enumerate(featureCalculateList):
#     # 使用处理后最新的字段内容
#     reservedField = df1.columns.tolist()
#     print(f'=============测试保留字段-{reservedField}=============')
#     tool1 = FeatureCalculationMethod(df1, reservedField)
#     if tempMethod == '降雨日数计算':
#         result1 = tool1.rainfallDaysAccumulation(
#             inputFeature1[indexT], modelParam1[indexT])
#     elif tempMethod == '降水累积量计算':
#         result2 = tool1.precipitationAccumulation(
#             inputFeature1[indexT], modelParam1[indexT])
#         # result2.to_excel('handled' + str(indexT) + '.xlsx')
#
# # 获得特征计算后结果
# # print(result1)
# # =========================合并数据集=========================
# resul3 = pd.merge(result2, df2T, on=['测报站点', '年'], how='left')
# print(f'=========================合并数据集=========================')
# resul3.to_excel('merged.xlsx', index=False)
#
# # =========================特征优选及读取执行方法=========================
# featureOptimalDF = pd.read_excel('特征优选记录.xlsx')
#
# inputFeature2 = featureOptimalDF["输入特征"].tolist()
# outputFeature2 = featureOptimalDF["优选特征"].tolist()
# featureOptimalList = featureOptimalDF["特征优选方法"].tolist()
# modelParam2 = featureOptimalDF["方法参数"].tolist()
# print(modelParam2)
#
# tool2 = FeatureOptimizationMethod(resul3, resul3.columns)
# # 初始化特征优选方法
# for indexT, tempMethod in enumerate(featureOptimalList):
#     reservedField = resul3.columns.tolist()
#     afterHandleData = None
#     # print(tempMethod)
#     if tempMethod == 'Pearson相关性分析':
#         afterHandleData = tool2.Pearson(
#             modelParam2[indexT])
#         # 获得特征计算后结果
#         print(afterHandleData)
#         afterHandleData.to_excel('handled2.xlsx')
#     elif tempMethod == 'Relief-F互相关分析':
#         afterHandleData = tool2.ReliefF(
#             inputFeature2[0], modelParam2)
#
# # =========================提取有效值(可输出)=========================
# print('=========================提取有效值(可输出)=========================')
# # 使用groupby分组并提取每个分组的第一个非空值
# ultimateFeatures = afterHandleData.groupby(['上级单位', '测报站点', '年']).first().reset_index()
# # ******删除包含缺失值的行******
# df_cleaned = ultimateFeatures.dropna()
# df_cleaned.to_excel('ultimateFeatures.xlsx')

# ***********************数据准备完成,准备预测***********************
# df_cleaned = pd.read_excel('ultimateFeatures.xlsx')
# # 根据上级单位、测报站点、年份范围获取数据集执行模型预测结果
# # =========================模型读取及读取执行方法(读入)=========================
# modelDF = pd.read_excel('模型记录.xlsx')
# models = modelDF["模型"].tolist()
# feature = modelDF["特征"].tolist()
# label = modelDF["标签"].tolist()
#
# print('=========================模型读取及预测=========================')
# for indexT, (tempModel, tempFeature,
#              tempLabel) in enumerate(zip(models, feature, label)):
#     tempFeature = eval(tempFeature)
#     # 模型读取
#     model = getModel(tempModel)
#     inputDF = df_cleaned[tempFeature]
#     # 筛选出省份为'湖南省'和测报站点为'湘阴县'的所有行(不能删除,否则少特征)
#     # filtered_df = df_cleaned[(df_cleaned['上级单位'] == province) & (df_cleaned['测报站点'] == station)]
#     # 选取包含在 tempFeature 中的列
#     # inputDF = filtered_df[tempFeature]
#     print(model)
#     if '上级单位' and '测报站点' in tempFeature:
#         X = pd.get_dummies(inputDF, columns=['上级单位', '测报站点'])
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)
#     # 接下来您可以使用 X_scaled 进行进一步的模型训练和预测
#     # model.predict() 方法需要接受和训练时相同的特征列
#     predictions = model.predict(X_scaled)
#     # 创建一个 DataFrame 包含预测值
#     predictions_df = pd.DataFrame(predictions, columns=['Predicted_value'])
#
#     # 合并特征数值和预测值到一个新的 DataFrame
#     result_df = pd.concat([df_cleaned, predictions_df], axis=1)
#     # 打印包含预测值和特征值的 DataFrame
#     result_df.to_excel('predicts' + str(tempModel) + '.xlsx')

# =========================计算静态偏差指标=========================
# 输入真实植保数据(测试是否缺失)(输入原始特征中有),并结合上述模型输出预测数据

# (单一气象场景)结果可视化(暂不处理)
# 计算指标
data = pd.read_excel('predictsSVR.xlsx')
data_B = data['病害峰值']  # 实际
data_A = data['Predicted_value']  # 预测
# 计算两组数据相减的均值之和除以长度
mean_diff = ((data_A - data_B).sum()) / len(data_A)

# 计算数据 A 的标准差之和除以长度
std_dev_B = data_B.std() / len(data_B)

print(f"预测值与实际发生程度之差的均值: {mean_diff}")
print(f"实际发生程度的标准差: {std_dev_B}")
print(f'Dev_s:{mean_diff / std_dev_B}')
