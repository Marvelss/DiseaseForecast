import numpy


def initpop(popsize, chromlength):
    pop = numpy.random.randint(0, 2, (popsize, chromlength))
    return pop
