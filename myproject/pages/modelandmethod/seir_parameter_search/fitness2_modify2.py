"""
@Author : SakuraFox
@Time: 2024-06-13 16:54
@File : fitness2_modify2.py
@Description : file description
"""
import math
import numpy as np
from scipy.stats import norm


def getCellDate(doyList):
    for i in range(1, len(doyList)):
        if doyList[i] < doyList[i - 1]:
            return doyList[i - 1]


def fitness2_modify2(ka, kb, kc, q, r, OPT_PRI, w, beta0,
                     optimumTEM, temStep, preStep, slideStep, mergedDataSet):
    df = mergedDataSet
    grouped = df.groupby(['测报站点', '年'])
    precisionDiseaseResultList = []
    # 全部预测值和实际值
    allPredictList, allActualList = [], []
    for (key, group) in grouped:
        # 打印分组键（'测报站点' 和 '年'）
        # print(f"Group key: {key}")
        # 获取降水和温度字段的数据
        precipitation_data = group['降水'].values
        temperature_data = group['温度'].values
        transplanting_data = group['移栽期'].values
        dayOfYear_data = group['DayOfYear'].values

        # 移栽期取最小值
        transplanting_data_duplicates = np.unique(transplanting_data)[0]
        # DayOfYear取无缺失值的最大值(前提:重要提供的原始数据集缺失值后置**)
        first_negative_diff_value = getCellDate(dayOfYear_data)
        startDay = transplanting_data_duplicates
        endDay = first_negative_diff_value

        # 获取 startDay 和 endDay 范围内的所有字段数据
        mask = (group['DayOfYear'] >= startDay - 5) & (group['DayOfYear'] <= endDay)
        # 获取窗口内所有有效数据
        effectiveIntervalData = group.loc[mask]
        # print(effectiveIntervalData)
        # 接下处理
        # 按 DayOfYear排序保存文件
        effectiveIntervalDataT = effectiveIntervalData.sort_values(by='DayOfYear').reset_index(drop=True)
        # tempSaveFile.to_excel(f'每个地区每年有效时间范围内数据/result{key[0]}{key[1]}.xlsx', index=False)
        # time.sleep(3)

        # print(f'时间范围下限:{transplanting_data_duplicates}')
        # print(f'时间范围上限:{first_negative_diff_value}')
        if not first_negative_diff_value:
            continue

        # 打印降水和温度数据
        # print(f"Precipitation data: {precipitation_data}")
        # print(f"Temperature data: {temperature_data}")
        # print(f"Transplanting data: {transplanting_data}")
        # print(f"DayOfYear data: {dayOfYear_data}")
        # print('----------------------------')

        e = effectiveIntervalDataT
        # print(e)
        erow = len(e)
        tempActualDiseaseData = e['实际病株率'].values
        tempPData = e['降水'].values
        tempTData = e['温度'].values
        # print(f'降水:{tempPData}')
        # print(f'温度:{tempTData}')
        # 使用布尔索引去除 NaN 值
        # actualDiseaseData = tempActualDiseaseData[~np.isnan(tempActualDiseaseData)]
        # print(f'实际病株率:{tempActualDiseaseData}')
        # print(actualDiseaseData)
        # print('总数据:')
        # print(e)
        # 平均潜伏期
        W = 1 / w
        # 平均感染期
        U = 1 / q
        # 感染率
        Beta = []
        dt = 1

        n = erow - 4
        n1 = erow

        t = np.zeros([1, n])  # n+1? n?
        H = np.zeros([1, n])
        L = np.zeros([1, n])
        I = np.zeros([1, n])
        R = np.zeros([1, n])
        t[0, 0] = 0
        H[0, 0] = 0.9997
        L[0, 0] = 0.0001
        I[0, 0] = 0.0001
        R[0, 0] = 0.0001

        # # 不带峰值的病害预测结果
        # predictDiseaseResultList = []
        # 带有峰值的病害预测结果
        predictDiseaseResultPeakList = []
        # 温度窗口步长
        # temStep = 3
        # # 降水窗口步长
        # preStep = 5
        # 最适降水量
        # OPT_PRI = 10.83
        # 调节参数
        # r = 15
        # 缓冲系统ka,kb,温度函数方差
        # ka, kb, kc = 4.05, 0.04, 30
        # 获取传染率
        for k in range(5, n1 + 1):
            # **这里温度和降水都-1(和源代码不符)**
            e1 = e.loc[k - preStep:k, '降水']
            e2 = e.loc[k - temStep:k, '温度']
            # print(f'第{str(k)}批温度和降水:')
            # print(e1)
            # print(e2)
            # print('********************')
            # print(e1)
            # print(e2)
            # time.sleep(10)
            e_PRI = sum(e1)
            e_TEM = np.mean(e2)
            PRI = 1 + (0.001 - 1) / (1 + math.exp((e_PRI - OPT_PRI) / r))
            x = np.linspace(0, 43, 44)
            y = norm.pdf(x, optimumTEM, kc)
            MAX = max(y)
            MIN = min(y)
            TEM = (y[math.floor(e_TEM)] - MIN) / (MAX - MIN)
            AGE = k / n
            B1 = ka * beta0 * PRI * TEM * AGE + kb
            Beta.append(B1)
        # SEIR框架
        for g in range(0, n - 1):
            t[0, g + 1] = t[0, g] + dt
            H[0, g + 1] = H[0, g] + dt * (-Beta[g] * H[0, g] * I[0, g])
            L[0, g + 1] = L[0, g] + dt * (Beta[g] * H[0, g] * I[0, g] - W * L[0, g])
            I[0, g + 1] = I[0, g] + dt * (W * L[0, g] - U * I[0, g])
            R[0, g + 1] = R[0, g] + dt * (U * I[0, g])
        tempPredictDiseaseResult = (R + I)
        # 模型预测结果
        predictDiseaseResultT = np.transpose(tempPredictDiseaseResult)

        # 峰值模块
        DOYData = e['DayOfYear'].values
        transplantingData = e['移栽期'].values
        peakData = e['病害峰值'].values
        predictDiseaseResult = []
        for doy, transplanting, peak in zip(DOYData, transplantingData, peakData):
            z = doy - transplanting
            if z > erow:
                z = erow - 1
            else:
                if z < 0 or z == 0:
                    z = 0  # z=1
                else:
                    z = z
            result = predictDiseaseResultT[z] * peak
            predictDiseaseResult.append(result)

        # print(predictDiseaseResult)
        # 设置 NumPy 的打印选项，以科学计数法显示，并控制小数点后的位数
        # np.set_printoptions(suppress=False, formatter={'float_kind': '{:e}'.format})
        # 打印结果
        # print(predictDiseaseResultList)
        predictLabel = np.array(predictDiseaseResult)
        actualLabel = tempActualDiseaseData
        # tempPredictLabel = predictLabel
        tempPredictLabel = predictLabel.flatten()
        # tempPredictLabel = predictLabel
        # print(tempPredictLabel)
        # 预测结果使用非空值填充使其与实际病害数据大小同意长度
        # (重要:预测结果长度比原始截取的植保数据区间少4**)
        # 计算长度差
        length_difference = len(actualLabel) - len(tempPredictLabel)

        # 创建一个包含 NaN 的数组，长度为 length_difference
        nan_array = np.full(length_difference, np.nan)

        # 将 NaN 数组与 predictLabel 数组合并
        predictLabel_padded = np.concatenate((nan_array, tempPredictLabel))

        # 提取非空值
        # 找到 actualLabel 中非空值的下标
        non_nan_indices = ~np.isnan(actualLabel)

        # 提取 actualLabel 中的非空值
        actualLabel_non_nan = actualLabel[non_nan_indices]

        # 提取 predictLabel_padded 中对应下标的值
        predictLabel_corresponding = predictLabel_padded[non_nan_indices]

        # # 创建一个 DataFrame 来保存这些值
        # data = {
        #     'ActualLabel': actualLabel_non_nan,
        #     'PredictLabel': predictLabel_corresponding
        # }
        #
        # df1 = pd.DataFrame(data)
        # df1.to_excel('提取后.xlsx')

        tempMoleculeList = []
        for s in range(0, len(predictLabel_corresponding)):
            tempMolecule = np.power((actualLabel_non_nan[s] - predictLabel_corresponding[s]),
                                    2)  # np.power((ZB1.values[s - 1, 14] - D[s]), 2)
            tempMoleculeList.append(tempMolecule)

            # 全部预测和实际值放在一个矩阵
            allPredictList.append(predictLabel_corresponding[s])
            allActualList.append(actualLabel_non_nan[s])
        molecule = sum(tempMoleculeList)
        rootMeanSquareError = (molecule / len(actualLabel)) ** 0.5
        precisionDiseaseResultList.append(rootMeanSquareError)

    # 取所有组精度的平均值
    meanRMSE = sum(precisionDiseaseResultList) / len(precisionDiseaseResultList)
    # print(f'RMSE:{meanRMSE}')

    # 计算相关系数矩阵
    R3 = np.corrcoef(allActualList, allPredictList)
    R2 = np.power(R3, 2)[0, 1]
    # print(f'R方:{R2}')
    # print('------------a-----------------')
    allPredictList = np.array(allPredictList).flatten()
    allActualList = np.array(allActualList).flatten()
    return meanRMSE, R2, allPredictList, allActualList
