"""
@Author : SakuraFox
@Time: 2024-02-29 15:41
@File : FeatureOptimizationMethod.py
@Description : 特征优化方法
"""
import pandas as pd
from scipy.stats import stats, ttest_ind
import numpy as np
from sklearn.model_selection import train_test_split
from skrebate import ReliefF


class FeatureOptimizationMethod:
    def __init__(self, dataFrame):
        self.dataFrame = dataFrame.copy()
        # self.reservedField = reservedField

    # def getHandledFieldPoint(self, fieldName):
    #     # 若字段为原始数据
    #     if fieldName[-1].isdigit() and fieldName[-2] != '后':
    #         return fieldName[:-1] + str(int(fieldName[-1]) + 1)
    #     # 若字段已处理,则末尾数字+1
    #     else:
    #         return f"{fieldName}-优选特征0"

    # 检测连续数据判断是否回归模型
    @staticmethod
    def detectReliefFContinueColumn(dfT, columnT):
        # 根据唯一值数据占比判断
        unique_values = dfT[columnT].nunique()
        total_values = len(dfT[columnT])
        # 占比<0.005
        if unique_values / total_values < (5 * 0.001):
            return True
        else:
            return False

    # t检验
    def tTest(self, methodParam):
        # param:['年', 'DayOfYear 经度 纬度', '0.02']
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
        filtered_data = {key: value for key, value in tempResult.items() if value <= float(condition)}
        # 获取优选特征集
        optimalFeatureList = list(filtered_data.keys())
        # print(tempResult)
        # print(optimalFeatureList)
        # optimalFeatureList.remove(targetVariable)
        # newColumnsList = []
        # for feature in optimalFeatureList:
        #     new_column_name = self.getHandledFieldPoint(feature)
        #     # self.dataFrame[new_column_name] = self.dataFrame[feature]
        #     newColumnsList.append(new_column_name)

        return tempResult, optimalFeatureList

    # RF互相关分析
    def ReliefF(self, methodParam):
        # param:['病害峰值', ' 7-19_8-9_降雨日数 01-01_01-30_降水累量', '按百分比选取', '50']
        # param1:目标变量
        # param2:被比较变量
        # param3:提取方法
        # param4:提取方法参数
        target = methodParam[0]
        # print(target)
        comparedVariableList = methodParam[1].split(' ')
        name = methodParam[2]
        proportion = methodParam[3]
        # print(methodParam)
        # =========================提取有效值=========================
        # 使用groupby分组并提取每个分组的第一个非空值
        # ultimateFeatures = self.dataFrame.groupby(['经度', '纬度', '年']).first().reset_index()
        # # ******删除包含缺失值的行******
        # # 若DayOfYear列都为空表明已经以年为单位
        # if ultimateFeatures['DayOfYear'].isna().all():
        #     df_cleaned = ultimateFeatures
        # else:
        #     df_cleaned = ultimateFeatures.dropna()
        df_cleaned = self.dataFrame
        # 准备数据
        X = df_cleaned[comparedVariableList + [target]].drop(columns=[target])  # 假设我们已经从df中删除了目标列和不需要的列
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
        # print(X.columns)
        # print(f'特征重要性:{feature_scores}')
        # 从 X 获取特征名称
        feature_names = X.columns.tolist()

        # 检查特征名称和特征得分的长度
        if len(feature_names) != len(feature_scores):
            raise ValueError("特征名称和特征得分的长度不一致")

        # 将特征名称和得分组合成字典
        feature_importance_dict = dict(zip(feature_names, feature_scores))

        # 将特征名称和得分排序
        sorted_feature_importance_dict = dict(
            sorted(feature_importance_dict.items(), key=lambda item: item[1], reverse=True))

        # print(feature_importance_dict)
        # print('从大到小排序')
        # print(sorted_feature_importance_dict)
        selected_features_indices = None
        # 按照Top百分比选取特征
        if name == '按百分比选取':
            # 按值排序
            sorted_scores = np.sort(feature_scores)[::-1]
            # 计算前40%元素的数量，向上取整
            num_elements = len(sorted_scores)
            num_top_40_percent = int(np.ceil(num_elements * float(methodParam[3]) * 0.01))
            # print(f'TOP:{methodParam[3]}')
            # print(np.ceil(num_elements * float(methodParam[3]) * 0.01))
            # print(num_top_40_percent)
            # 提取前40%的元素值
            top_40_percent_values = sorted_scores[:num_top_40_percent]

            # 获取前40%元素的最大值（阈值）
            threshold_value = top_40_percent_values[-1]

            # 选取得分高于或等于阈值的特征
            selected_features_indices = np.where(feature_scores >= threshold_value)[0]

        elif name == '按权重值计算':
            # 按照权重阈值选取特征
            # 设置得分阈值
            score_threshold = proportion
            # 选取得分高于阈值的特征
            selected_features_indices = np.where(feature_scores > score_threshold)[0]
            # 使用选定的特征来转换数据集
        # print(selected_features_indices)
        selected_features = X.columns[selected_features_indices]
        selected_features = selected_features.tolist()
        print(selected_features)
        # selected_features.remove(target)
        # newColumnsList = []
        # for feature in selected_features:
        #     new_column_name = self.getHandledFieldPoint(feature)
        #     self.dataFrame[new_column_name] = self.dataFrame[feature]
        #     newColumnsList.append(new_column_name)
        return sorted_feature_importance_dict, selected_features

    # Pearson相关分析
    def Pearson(self, methodParam):
        # param:['年 DayOfYear 经度 纬度', '0.9']
        # param1:所有变量
        # param2:提取条件
        # print('============测试============')
        # print(methodParam)
        labelField = methodParam[0]
        fieldList = methodParam[1].split(' ') + [labelField]
        condition = methodParam[2]
        # print(pValue)
        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # 遍历输入变量进行pearson分析
        tempResultP = {}
        # 选择需要计算相关性的列
        # result = newDataFrame.groupby(['经度', '纬度', '年']).first().reset_index()
        # ******删除包含缺失值的行******
        # df_cleaned = result.dropna()
        df_cleaned = newDataFrame
        data = df_cleaned[fieldList]
        # print(data)
        # result = data.groupby(['经度', '纬度', '年']).first().reset_index()
        # # ******删除包含缺失值的行******
        # df_cleaned = result.dropna()
        # 计算相关性矩阵
        correlation_matrix = data.corr()
        # print(df_cleaned)
        # print(correlation_matrix)

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
        # print(tempResultP)
        for (feature1, feature2), correlation in tempResultP.items():
            # print(feature1, feature2)
            if abs(correlation) > float(condition):
                # 默认移除后一个特征
                if feature2 in selected_features and feature2 != labelField:
                    selected_features.discard(feature2)
                elif feature1 in selected_features and feature1 != labelField:
                    selected_features.discard(feature1)
        # 获取优选特征集
        selected_features_list = list(selected_features)

        # 确保标签字段存在并移除标签字段
        if labelField in selected_features_list:
            selected_features_list.remove(labelField)
        # for feature in selected_features_list:
        #     if feature == labelField:
        #         continue
        #     new_column_name = self.getHandledFieldPoint(feature)
        #     self.dataFrame[new_column_name] = self.dataFrame[feature]
        #     newColumnsList.append(new_column_name)
        return correlation_matrix, selected_features_list

    # t检验与pearson相关性分析
    def tTestAndPearson(self, methodParam):
        # param:['年 DayOfYear 经度 纬度', '0.9']
        # param1:所有变量
        # param2:提取条件
        # print('============测试============')
        # print(methodParam)
        # 1.T检验 - p < 0.05, p < 0.01, p < 0.001
        # 2.三档（取都敏感特征）+Pearson - R2 > 0.8（优先取敏感性高的特征）
        labelField = methodParam[0]
        fieldList = methodParam[1].split(' ')
        tCondition = methodParam[2].split('<')[1]
        pCondition = methodParam[3]

        # 确保 tCondition 是 numpy.float64 类型
        tCondition = np.float64(tCondition)
        pCondition = np.float64(pCondition)

        # 复制新的变量
        newDataFrame = self.dataFrame.copy()
        # ==================计算t检验==================
        # 提取病害发生程度和气象字段
        disease_levels = newDataFrame[labelField].unique()
        meteorological_fields = fieldList + [labelField]
        # print(f"比较数组{meteorological_fields}")
        left_field = []

        t_test_results = {}  # 用于存储每个特征的 t 检验结果
        # 进行 t 检验，筛选显著性高的特征
        for field in meteorological_fields:
            if field == labelField:
                continue
            p_values = []
            for i in range(len(disease_levels)):
                for j in range(i + 1, len(disease_levels)):
                    group_i = newDataFrame[newDataFrame[labelField] == disease_levels[i]][field]
                    group_j = newDataFrame[newDataFrame[labelField] == disease_levels[j]][field]
                    _, p_value = ttest_ind(group_i, group_j, equal_var=False)  # 独立样本 t 检验
                    p_values.append(p_value)

            # print(f"字段 {field} 与病害发生程度类别的 p 值: {p_values}")
            # 若所有 p 值都 < 0.05，则保留该字段
            if all(p < tCondition for p in p_values):
                left_field.append(field)
                t_test_results[field] = p_values  # 保存 t 检验结果
                # print(f"字段 {field} 被保留，因为所有 t 检验的 p 值都 < {tCondition}")
            else:
                pass
                # print(f"字段 {field} 可能影响病害发生，被考虑去除")
        # 筛选 t 检验后符合条件的特征
        optimalFeatureList = left_field
        print('=========t检验后优选特征集=========')
        print(optimalFeatureList)

        # 使用 t 检验后的特征进行 Pearson 相关性分析
        if not optimalFeatureList:
            print("没有特征通过 t 检验，无法进行 Pearson 相关性分析。")
            return '', []
        # 计算特征之间的 Pearson 相关性系数
        correlation_matrix = newDataFrame[optimalFeatureList].corr(method='pearson')
        selected_features = set(optimalFeatureList)
        print(correlation_matrix)
        # 遍历特征对，根据相关性系数和显著性水平筛选特征
        for i in range(len(optimalFeatureList)):
            for j in range(i + 1, len(optimalFeatureList)):
                feature1 = optimalFeatureList[i]
                feature2 = optimalFeatureList[j]
                correlation = correlation_matrix.loc[feature1, feature2]
                if abs(correlation) > pCondition:
                    p1 = min(t_test_results[feature1])
                    p2 = min(t_test_results[feature2])
                    # 比较 p 值，剔除显著性较低的特征
                    if p1 < p2:
                        selected_features.discard(feature2)
                    else:
                        selected_features.discard(feature1)

        print('=========Pearson相关性分析后的最优特征集=========')
        print(selected_features)
        return '', list(selected_features)
