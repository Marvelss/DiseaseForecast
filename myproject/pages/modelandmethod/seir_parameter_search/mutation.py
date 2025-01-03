import numpy as np
import random

"""
遗传算法内置-变异操作
"""
def mutation(pop, pm):
    [px, py] = pop.shape
    newpop = np.ones((px, py))
    for i in range(0, px ):

        if random.random() < pm:
            mpoint = round(random.random() * py)-1#-0？
            if mpoint <= 0:
                mpoint = 0
            newpop[i, :] = pop[i, :]
            if newpop[i, mpoint] == 0:
                newpop[i, mpoint] = 1
            elif newpop[i, mpoint] == 1:
                newpop[i, mpoint] = 0
        else:
            newpop[i, :] = pop[i, :]
    return newpop
