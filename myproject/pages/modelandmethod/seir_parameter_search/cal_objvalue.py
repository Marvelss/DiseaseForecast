import numpy as np

from .fitness2_modify2 import fitness2_modify2


def cal_objvalue_run(pop2_ka, pop2_kb, pop2_kc, pop2_q, pop2_r, pop2_OPT_PRI,
                     w, beta0, optimumTEM, temStep, preStep, slideStep, mergedDataSet):
    px = len(pop2_ka)
    cg = np.zeros((px, 1))
    r = np.zeros((px, 1))
    allPredictResultList = []
    # allActualResultList = []
    allDataList = []
    for k in range(0, px):  # px
        # k = 0  # 改版增加上
        #     print('cal', k)
        cg[k, :], r[k, :], allPredictList, allActualResultList, dataF = fitness2_modify2(
            pop2_ka[k], pop2_kb[k], pop2_kc[k],
            pop2_q[k],
            pop2_r[k],
            pop2_OPT_PRI[k],
            w, beta0, optimumTEM, temStep, preStep,
            slideStep,
            mergedDataSet)
        allPredictResultList.append(allPredictList)
        # allActualResultList.append(allActualList)
        allDataList.append(dataF)
    return cg, r, allPredictResultList, allActualResultList, allDataList
