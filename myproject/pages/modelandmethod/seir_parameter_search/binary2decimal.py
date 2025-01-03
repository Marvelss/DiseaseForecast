import numpy as np


def binary2decimal(pop, min_coefficient, max_coefficient):
    if pop.ndim > 1:
        [px, py] = pop.shape
        pop1 = np.zeros((px, py))
        for i in range(0, py):
            pop1[:, i] = 2 ** (py - 1 - i) * pop[:, i]
        temp = pop1.sum(axis=1)
        pop2 = min_coefficient + temp * (max_coefficient - min_coefficient) / (2 ** py - 1)
    # print(px, py)
    else:
        px = 1
        py = pop.shape[0]
        pop1 = np.zeros((px, py))
        for i in range(0, py):
            pop1[0][i] = 2 ** (py - 1 - i) * pop[i]
        temp = pop1.sum(axis=1)
        pop2 = min_coefficient + temp * (max_coefficient - min_coefficient) / (2 ** py - 1)
    return pop2