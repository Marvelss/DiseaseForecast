"""
@Author : SakuraFox
@Time: 2024-04-08 9:41
@File : test8.py
@Description : 测试Relief-F特征选择算法
注意问题:
1.数据中不能含缺失值
2.y = df['发生程度']和y = df['发生程度']使用set(y)会失去多分类
3.X = df.drop(columns=['发生程度'])和y = df['发生程度']需要重置索引
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from skrebate import ReliefF

df = pd.read_excel('2024-04-08T01-42_export.xlsx')
# 准备数据
X = df.drop(columns=['发生程度'])  # 假设我们已经从df中删除了目标列和不需要的列
y = df['发生程度']
# 检查和处理缺失值
print('设置检查和处理缺失值')
# print(X.index)
# X = X.dropna()
# print(X.index)
# y = y.loc[X.index]  # 保持 y 和 X 的索引一致

# 确保所有列的数据类型一致
# X = X.astype(float)
# 找到包含缺失值的行
# missing_rows = X.isnull().any(axis=1)
# 数据标准化,下方X_train无需重置索引
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)
# print(X_scaled)
# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 重置索引并转换为NumPy数组
X_train = X_train.reset_index(drop=True).to_numpy()
y_train = y_train.reset_index(drop=True).to_numpy()
fs = ReliefF(n_features_to_select=2)

# 训练ReliefF模型以找到最重要的特征
fs.fit(X_train, y_train)

# 假设 fs.feature_importances_ 包含了特征的重要性得分
feature_scores = fs.feature_importances_
print(feature_scores)
print(len(feature_scores))
