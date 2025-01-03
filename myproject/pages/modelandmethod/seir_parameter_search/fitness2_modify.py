import math
import operator
import gc
import numpy as np
from scipy.stats import norm

"""
这段代码是用matlab实现的，看起来是一个运用SEIR模型进行疫情预测的程序。
程序中使用了xlsx格式的表格存储数据，包括气象数据、移栽期、植保数据等。
其中还用到了正态分布函数和logistic函数对温度和降水量进行响应处理，
并且使用了极值权重来修正预测结果，最后计算预测结果与实际植保数据的RMSE和R方。

"""



def fitness2(ka, kb, kc, q, r, OPT_PRI, YZQ_num, YZQ_txt, YZQ_data, ZB_num, ZB_data, met_num, met_txt, met_data,
             Jizhi_num, Jizhi_data):
    [yzq_row, yzq_col] = YZQ_data.shape
    D = []
    for i in range(0, yzq_row):
        ida = operator.eq(YZQ_data.values[i, 1], met_txt.values[:, 1])
        ida = np.array(ida)
        aimrow = np.where(ida[:] == 1)
        # aimplace_met = []
        aimplace_met_num = []
        gc.disable()
        for j in aimrow[0]:
            # aimplace_met.append(met_data.values[j, :])
            aimplace_met_num.append(met_num.values[j, :])
        gc.enable()
        del aimrow
        idb = operator.eq(YZQ_data.values[i, 1], ZB_data.values[:, 4])
        idb = np.array(idb)
        aimrow1 = np.where(idb[:] == 1)
        aimplace_ZB = []
        aimplace_ZB_num = []
        for p in aimrow1[0]:
            aimplace_ZB.append(ZB_data.values[p, :])
            aimplace_ZB_num.append(ZB_num.values[p, :])
        idc = operator.eq(YZQ_data.values[i, 1], Jizhi_data.values[:, 1])
        idc = np.array(idc)
        aimrowjizhi = np.where(idc[:] == 1)
        Jizhi4 = []
        for p in aimrowjizhi[0]:
            Jizhi4.append(Jizhi_num.values[p, :])
        Jizhi4 = np.array(Jizhi4)
        for ii in range(2010, 2017):
            temp = np.array(aimplace_ZB_num)
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
                W = 1 / 3
                U = 1 / q
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
                B = []
                for k in range(5, n1 + 1):
                    e1 = e[k - 5:k , 0]
                    e2 = e[k - 3:k , 1]
                    e_PRI = sum(e1)
                    e_TEM = np.mean(e2)
                    PRI = 1 + (0.001 - 1) / (1 + math.exp((e_PRI - OPT_PRI) / r))
                    x = np.linspace(0, 43, 44)
                    y = norm.pdf(x, 28, kc)
                    MAX = max(y)
                    MIN = min(y)
                    TEM = (y[math.floor(e_TEM)] - MIN) / (MAX - MIN)
                    AGE = k / n
                    # 三个修正量将温度、湿度和作物生育期的影响纳入模型，分别为T、W和A
                    # 对于下面参数TEM/PRI/AGE，详见张雪雪论文-式（4.3）
                    B1 = ka * 0.46 * PRI * TEM * AGE + kb
                    B.append(B1)
                for g in range(0, n - 1):
                    t[0, g + 1] = t[0, g] + dt
                    H[0, g + 1] = H[0, g] + dt * (-B[g] * H[0, g] * I[0, g])
                    L[0, g + 1] = L[0, g] + dt * (B[g] * H[0, g] * I[0, g] - W * L[0, g])
                    I[0, g + 1] = I[0, g] + dt * (W * L[0, g] - U * I[0, g])
                    R[0, g + 1] = R[0, g] + dt * (U * I[0, g])
                y2 = (R + I)
                y1 = np.transpose(y2)
                aimplace_aimyear_row = len(aimplace_aimyear_ZB)
                # C = []
                for a in range(0, aimplace_aimyear_row):
                    z = aimplace_aimyear_ZB_num[a][18] - YZQ_num.values[i, 2]  # +1 ?
                    if z > erow:
                        z = erow-1
                    else:
                        if z < 0 or z == 0:
                            z = 0 #z=1
                        else:
                            z = z
                    temp2 = np.array(Jizhi4)
                    aimjzrow = np.where(temp2[:, 2] == ii)
                    aimJizhi = Jizhi4[aimjzrow, 0]
                    D.append(y1[z, 0] * aimJizhi)

    ZB1 = ZB_num
    R2_FENZI1 = []
    [RowZB, ColZB] = ZB1.shape
    for s in range(0, RowZB):
        R2_fenzi = np.power((ZB1.values[s , 14] - D[s]), 2)#np.power((ZB1.values[s - 1, 14] - D[s]), 2)
        R2_FENZI1.append(R2_fenzi)
    R2_FENZI = sum(R2_FENZI1)
    RMSE = (R2_FENZI / RowZB) ** 0.5
    # R3 = np.corrcoef(ZB1.values[:, 14], D)
    # R2 = np.power(R3, 2)

    return RMSE
# fitness2(1, 1, 1, 1, 1, 1)
