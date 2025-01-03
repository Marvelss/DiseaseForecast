import os
import numpy as np
from natsort import natsorted
import pandas as pd
from scipy.stats import norm
import math

namelist_tem = []
filelocation = os.path.normpath('E:/智慧农业/DItxt')
for root, dirs, files in os.walk(filelocation):
    for i in files:
        if os.path.splitext(i)[1] == '.txt':
            namelist_tem.append(i)
ka = 1.34
kb = 0.19
kc = 56.25
q = 67.57
r = 19.29
OPT_PRI = 15.08
temA = np.zeros(72, 128, 365)
temB = np.zeros(72, 128, 365)
preA = np.zeros(72, 128, 365)
preB = np.zeros(72, 128, 365)
BZLfinal = np.zeros(72, 128, 365)
for i in range(0, 365):
    for m in range(0, 72):
        for n in range(0, 128):
            BZLfinal[m, n, i] = -99
temlen = len(namelist_tem)
Tfilename_name1 = natsorted(namelist_tem)
for i in range(0, temlen):
    Tnames = pd.read_table('E:/智慧农业/DItxt/' + Tfilename_name1[i], header='None', usecols=[0], nrows=6)
    Tvalues = pd.read_table('E:/智慧农业/DItxt/' + Tfilename_name1[i], header='None', usecols=[1], nrows=6)
    Tnx = Tvalues[0]
    Tny = Tvalues[1]
    TData = pd.read_table('E:/智慧农业/DItxt/' + Tfilename_name1[i], header='None', skiprows=6)
    TData.reshape(Tnx, Tny)
    TData = TData.T
    temA[:, :, i] = TData
# 降水代码，待补充
#
#
#
#
#
#
YZQnames = pd.read_table('F:/matlab/模型原始代码/GA/移栽期.txt', header='None', usecols=[0], nrows=6)
YZQvalues = pd.read_table('F:/matlab/模型原始代码/GA/移栽期.txt', header='None', usecols=[1], nrows=6)
YZQnx = YZQvalues[0]
YZQny = YZQvalues[1]
tpday = pd.read_table('F:/matlab/模型原始代码/GA/移栽期.txt', header='None', skiprows=6)
tpday.reshape(YZQnx, YZQny)
tpday = tpday.T
FZnames = pd.read_table('F:/matlab/模型原始代码/GA/fengzhi.txt', header='None', usecols=[0], nrows=6)
FZvalues = pd.read_table('F:/matlab/模型原始代码/GA/fengzhi.txt', header='None', usecols=[1], nrows=6)
FZnx = FZvalues[0]
FZny = FZvalues[1]
FZdata = pd.read_table('F:/matlab/模型原始代码/GA/fengzhi.txt', header='None', skiprows=6)
FZdata.reshape(FZnx, FZny)
FZdata = FZdata.T
W = 1 / 4
U = 1 / q
dt = 1
n = 70
t = np.zeros(1, n)
H = np.zeros(1, n)
L = np.zeros(1, n)
I = np.zeros(1, n)
R = np.zeros(1, n)
t[0, 0] = 0
H[0, 0] = 0.9997
L[0, 0] = 0.0001
I[0, 0] = 0.0001
R[0, 0] = 0.0001
x = np.linspace(0, 1, 43)
y = norm.pdf(x, 28, kc)
MAX = max(y)
MIN = min(y)
for a in range(39, 60):
    for b in range(72, 102):
        if tpday != -99:
            startday = tpday[a, b]
            endday = startday + 140
            for u in range(startday - 1, endday):
                k = u - startday + 1
                AGE = k / n
                temsum = temA[a, b, u] + temA[a, b, u - 1] + temA[a, b, u - 2]
                tem = temsum / 3
                pre = preA(a, b, u) + preA[a, b, u - 1] + preA[a, b, u - 2] + preA[a, b, u - 3] + preA[a, b, u - 4]
                if tem != -99:
                    if pre != -9999:
                        if math.floor(tem) < 0:
                            tem = 0
                        TEM = (y[1, (math.floor(tem)) + 1] - MIN) / (MAX - MIN)
                        PRI = 1 + (0.001 - 1) / (1 + math.exp((pre - OPT_PRI) / r))
                        B1 = ka * 0.46 * PRI * TEM * AGE + kb
                        t[0, k + 1] = t[0, k] + dt
                        H[0, k + 1] = H[0, k] + dt * (-B1 * H[0, k] * I[0, k])
                        L[0, k + 1] = L[0, k] + dt * (B1 * H[0, k] * I[0, k] - W * L[0, k])
                        I[0, k + 1] = I[0, k] + dt * (W * L[0, k] - U * I[0, k])
                        R[0, k + 1] = R[0, k] + dt * (U * I[0, k])
                        y2 = R[1, k] + I[1, k]
                        if y2 > 1:
                            y2 = 1
                            BZLfinal[a, b, u] = y2 * FZdata(a, b)
                        else:
                            BZLfinal[a, b, u] = y2 * FZdata(a, b)
for i in range(149, 300):
    fp = open('2DI' + str(i) + Tfilename_name1[i], 'w')
    for c in range(1, Tnames.shape):
        print(c, file=fp)
    m = 72
    n = 128
    for j in range(0, m):
        for k in range(0, n):
            if k == n - 1:
                print('%06.6\n', BZLfinal[j, k, i], file=fp)
            else:
                print('%06.6', BZLfinal[j, k, i], file=fp)

    fp.close()
