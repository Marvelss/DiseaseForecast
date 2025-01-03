import numpy as np
import random
#
# pop = np.random.randint(0, 2, (3, 9))
# print(pop)
"""
遗传算法内置-交叉操作
"""

def crossover(pop, pc):
    [px, py] = pop.shape
    newpop = np.ones((px, py))
    # print(newpop)
    for i in range(0, px-1, 2):

        if random.random() < pc:
            cpoint = round(random.random() * (py-1))
            newpop[i, :] = np.append(pop[i, 0:cpoint+1], pop[i + 1, cpoint+1:py], axis=0)
            newpop[i + 1, :] = np.append(pop[i + 1, 0:cpoint + 1], pop[i, cpoint +1:py], axis=0)
        else:
            newpop[i, :] = pop[i, :]
            newpop[i + 1, :] = pop[i + 1, :]
    return newpop
#     print(newpop)
#
#
# crossover(pop, 0.6)
