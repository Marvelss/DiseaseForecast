"""
@Author : SakuraFox
@Time: 2024-05-10 20:06
@File : test22.py
@Description : 补充模拟气象数据,并替换原始气象数据
补充上级单位、测报站点、年信息
"""
import os

import pandas as pd


# 获取模拟气象数据(待修正)
def getSimulateWeather(weatherSituation, province, station, startYear):
    modelPathRoot = os.path.join(
        r'E:\a_python\program\diseaseForecastStreamlit',
        'resource',
        'weatherGeneratorOutput')
    fileDirPath = os.path.join(modelPathRoot, weatherSituation)
    merged_data = None
    for fileTemp in os.listdir(fileDirPath):
        # Get the file name
        file_name = os.path.join(fileDirPath, fileTemp)
        yearNum = fileTemp.split('年')[0].split('第')[1]
        data = pd.read_excel(file_name)
        print(yearNum)
        data['年'] = int(yearNum) + int(startYear)
        if merged_data is None:
            merged_data = data.copy()  # Initialize merged_data with the first file's data
        # Read the Excel file
        else:
            print(merged_data)
            # Merge the data using the 'left' method
            merged_data = pd.merge(merged_data, data, how='outer')
        # Add additional columns
        merged_data['上级单位'] = province
        merged_data['测报站点'] = station
        # Calculate average temperature
        merged_data['温度'] = (merged_data['最高温度'] + merged_data['最低温度']) / 2
    merged_data.to_excel('merged.xlsx')
    print(merged_data)
    return merged_data


# 函数替换数据
def replace_data(df1, df2):
    # 根据条件筛选并替换原始数据表格中的值
    for index, row in df2.iterrows():
        condition = (df1['上级单位'] == row['上级单位']) & (df1['测报站点'] == row['测报站点']) & \
                    (df1['年'] == row['年']) & (df1['DayOfYear'] == row['DayOfYear'])
        df1.loc[condition, '降水'] = round(row['降水'], 2)
        df1.loc[condition, '温度'] = round(row['温度'], 2)
    return df1


df3T = getSimulateWeather(
    '低温少雨',
    '湖南省',
    '湘阴县', '2010')
# print(df3T)
rawData = replace_data(pd.read_excel('气象数据.xlsx'), df3T)
rawData.to_excel('replaced.xlsx')
