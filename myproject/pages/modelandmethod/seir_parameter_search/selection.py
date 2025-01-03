import numpy as np

"""
遗传算法内置-选择操作
"""
def selection(pop, fitvalue):
    [px, py] = pop.shape
    totalfit = np.sum(fitvalue)
    p_fitvalue = fitvalue / totalfit
    p_fitvalue = np.cumsum(p_fitvalue, axis=0)
    ms = np.sort(np.random.rand(px, 1),axis=0)
    fitin = 0
    newin = 0
    newpop = np.zeros((px, py))
    while newin <= px - 1:
        if (ms[newin]) <= p_fitvalue[fitin]:
            newpop[newin, :] = pop[fitin, :]
            newin = newin + 1
        else:
            fitin = fitin + 1
    return newpop
