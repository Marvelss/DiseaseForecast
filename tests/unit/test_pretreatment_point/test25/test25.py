"""
@Author : SakuraFox
@Time: 2024-05-22 16:45
@File : test25.py
@Description : 缺失值插补
"""
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

# 湖南省xxx县部分温度数据插补前后对比图
#
# 第一个缺失值前后3个数值(共6个)
#
# x:doy
# y:wendu
# 读取数据集
# 生成模拟数据
np.random.seed(0)
days = np.arange(1, 31)  # 一个月的数据，1到30天
precipitation = np.random.rand(30)  # 随机生成0到1之间的降水量

# 引入一些缺失值
precipitation[[2, 5, 15, 18, 25]] = np.nan

# 创建DataFrame
data = pd.DataFrame({
    'dayofyear': days,
    'precipitation': precipitation
})

# 创建插补前的数据副本
data_before = data.copy()

# 查找缺失值的索引
missing_indices = data[data['precipitation'].isna()].index

# 找到第一个缺失值的位置
first_missing_index = missing_indices[0]

# 获取前3天和后3天的数据，注意处理边界情况
start_index = max(first_missing_index - 3, 0)
end_index = min(first_missing_index + 3, len(data) - 1)

# 获取前3天和后3天的数据，并打印出来
x_axis_data = data.loc[start_index:end_index]


# 定义一个函数，用于插补缺失值
def interpolate_precipitation(series, index):
    start = max(index - 3, 0)
    end = min(index + 4, len(series))
    valid_values = series[start:end].dropna()
    if len(valid_values) > 0:
        return valid_values.mean()
    else:
        return None


# 对每个缺失值进行插补
for index in missing_indices:
    data.loc[index, 'precipitation'] = interpolate_precipitation(data['precipitation'], index)
plt.rcParams['font.sans-serif'] = 'SimHei'

# 绘制对比折线图
plt.figure(figsize=(12, 6))

# 绘制插补前的折线图
plt.plot(data_before['dayofyear'], data_before['precipitation'], label='原始数据', color='black', linestyle='-',
         marker='o')

# 绘制插补后的折线图
plt.plot(data['dayofyear'], data['precipitation'], label='插补后数据', color='blue', linestyle='--', marker='o',
         alpha=0.3)

# 标注插补点
# for index in missing_indices:
#     plt.axvline(x=data.loc[index, 'dayofyear'], color='green', marker='x', alpha=0.6)

plt.xlabel('Day of Year')
plt.ylabel('降水')
plt.title('湖南省湘阴县部分降水数据插补前后对比图')
plt.legend()
# plt.grid(True)
# plt.show()

data_before = pd.read_excel('a气象数据 - 测试.xlsx')
# data_before =
# data_after = st.session_state["DPVisualInformation"][o]['after']
# 查找缺失值的索引
missing_indices = data_before[data_before['降水'].isna()].index
# 获取第一个缺失值的索引
first_missing_index = missing_indices[0]
print(missing_indices)
missing_rows = data_before.loc[missing_indices, ['上级单位', '测报站点', '年', 'DayOfYear']].to_dict('records')[0]

# 打印结果
print(missing_rows['上级单位'])

# 计算前15行和后15行的起始和结束索引
start_index = max(first_missing_index - 15, 0)
end_index = min(first_missing_index + 15 + 1, len(data_before))

# 获取前15行和后15行数据
surrounding_data = data_before.iloc[start_index:end_index]
# 打印结果
print(type(surrounding_data))
