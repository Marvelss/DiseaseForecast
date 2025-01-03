from seir_parameter_search.cal_objvalue import cal_objvalue_run
from seir_parameter_search.crossover import crossover
from seir_parameter_search.initpop import initpop
from seir_parameter_search.binary2decimal import binary2decimal

from seir_parameter_search.mutation import mutation
from seir_parameter_search.selection import selection

"""
这段代码是遗传算法的优化过程，用于寻找最优解。
代码中设定了种群大小为20，编码长度为10，交叉概率为0.6，变异概率为0.001。
初始种群为随机生成的二进制编码，分别进行了选择、交叉、变异操作，并更新了种群，从而不断优化。
通过计算得到每个个体的适应度值，并保存最好的个体和适应度值。
在代码的最后，将最好的个体转换为十进制值，并输出结果。

"""


def start():
    popsize = 20
    # 二进制编码长度
    v = 10
    chromlength = 10
    # 交叉概率
    pc = 0.6
    # pc = 0.8
    # 变异概率
    pm = 0.001
    # 初始种群
    pop_ka = initpop(popsize, chromlength)
    pop_kb = initpop(popsize, chromlength)
    pop_kc = initpop(popsize, chromlength)
    pop_q = initpop(popsize, chromlength)
    pop_r = initpop(popsize, chromlength)
    pop_OPT_PRI = initpop(popsize, chromlength)
    min_coefficient_ka = 1
    max_coefficient_ka = 4
    min_coefficient_kb = 0
    max_coefficient_kb = 0.3
    min_coefficient_kc = 30
    max_coefficient_kc = 60
    min_coefficient_q = 50
    # 感染期
    max_coefficient_q = 90
    min_coefficient_r = 10
    max_coefficient_r = 20
    min_coefficient_OPT_PRI = 10
    max_coefficient_OPT_PRI = 30

    pop2_ka_decimal2 = binary2decimal(pop_ka, min_coefficient_ka, max_coefficient_ka)  # 2进制转换为10进制
    pop2_kb_decimal2 = binary2decimal(pop_kb, min_coefficient_kb, max_coefficient_kb)
    pop2_kc_decimal2 = binary2decimal(pop_kc, min_coefficient_kc, max_coefficient_kc)
    pop2_q_decimal2 = binary2decimal(pop_q, min_coefficient_q, max_coefficient_q)
    pop2_r_decimal2 = binary2decimal(pop_r, min_coefficient_r, max_coefficient_r)
    pop2_OPT_PRI_decimal2 = binary2decimal(pop_OPT_PRI, min_coefficient_OPT_PRI, max_coefficient_OPT_PRI)

    objvalue2 = cal_objvalue_run(pop2_ka_decimal2, pop2_kb_decimal2, pop2_kc_decimal2, pop2_q_decimal2, pop2_r_decimal2,
                                 pop2_OPT_PRI_decimal2)
    fitvalue2 = objvalue2
    [px, py] = pop_ka.shape
    bestindividual_ka = pop_ka[0, :]
    bestindividual_kb = pop_kb[0, :]
    bestindividual_kc = pop_kc[0, :]
    bestindividual_q = pop_q[0, :]
    bestindividual_r = pop_r[0, :]
    bestindividual_OPT_PRI = pop_OPT_PRI[0, :]
    bestfit = fitvalue2[0]

    for i in range(0, 50):  # 50
        print(i)
        pop2_ka_decimal = binary2decimal(pop_ka, min_coefficient_ka, max_coefficient_ka)
        pop2_kb_decimal = binary2decimal(pop_kb, min_coefficient_kb, max_coefficient_kb)
        pop2_kc_decimal = binary2decimal(pop_kc, min_coefficient_kc, max_coefficient_kc)
        pop2_q_decimal = binary2decimal(pop_q, min_coefficient_q, max_coefficient_q)
        pop2_r_decimal = binary2decimal(pop_r, min_coefficient_r, max_coefficient_r)
        pop2_OPT_PRI_decimal = binary2decimal(pop_OPT_PRI, min_coefficient_OPT_PRI, max_coefficient_OPT_PRI)
        objvalue1 = cal_objvalue_run(pop2_ka_decimal, pop2_kb_decimal, pop2_kc_decimal, pop2_q_decimal, pop2_r_decimal,
                                     pop2_OPT_PRI_decimal)
        fitvalue1 = objvalue1

        for j in range(0, px):
            if fitvalue1[j] < bestfit:
                bestindividual_ka = pop_ka[j, :]
                bestindividual_kb = pop_kb[j, :]
                bestindividual_kc = pop_kc[j, :]
                bestindividual_q = pop_q[j, :]
                bestindividual_r = pop_r[j, :]
                bestindividual_OPT_PRI = pop_OPT_PRI[j, :]
                bestfit = fitvalue1[j]
        # 选择操作
        newpop_ka = selection(pop_ka, fitvalue1)
        newpop_kb = selection(pop_kb, fitvalue1)
        newpop_kc = selection(pop_kc, fitvalue1)
        newpop_q = selection(pop_q, fitvalue1)
        newpop_r = selection(pop_r, fitvalue1)
        newpop_OPT_PRI = selection(pop_OPT_PRI, fitvalue1)
        # 交叉操作
        newpop_ka = crossover(newpop_ka, pc)
        newpop_kb = crossover(newpop_kb, pc)
        newpop_kc = crossover(newpop_kc, pc)
        newpop_q = crossover(newpop_q, pc)
        newpop_r = crossover(newpop_r, pc)
        newpop_OPT_PRI = crossover(newpop_OPT_PRI, pc)
        # 变异操作
        newpop_ka = mutation(newpop_ka, pm)
        newpop_kb = mutation(newpop_kb, pm)
        newpop_kc = mutation(newpop_kc, pm)
        newpop_q = mutation(newpop_q, pm)
        newpop_r = mutation(newpop_r, pm)
        newpop_OPT_PRI = mutation(newpop_OPT_PRI, pm)
        # 更新种群
        pop_ka = newpop_ka
        pop_kb = newpop_kb
        pop_kc = newpop_kc
        pop_q = newpop_q
        pop_r = newpop_r
        pop_OPT_PRI = newpop_OPT_PRI
    best_ka = binary2decimal(bestindividual_ka, min_coefficient_ka, max_coefficient_ka)
    best_kb = binary2decimal(bestindividual_kb, min_coefficient_kb, max_coefficient_kb)
    best_kc = binary2decimal(bestindividual_kc, min_coefficient_kc, max_coefficient_kc)
    best_q = binary2decimal(bestindividual_q, min_coefficient_q, max_coefficient_q)
    best_r = binary2decimal(bestindividual_r, min_coefficient_r, max_coefficient_r)
    best_OPT_PRI = binary2decimal(bestindividual_OPT_PRI, min_coefficient_OPT_PRI, max_coefficient_OPT_PRI)
    print('The best X is --->>%5.2f\n', best_ka, best_kb, best_kc, best_q, best_r, best_OPT_PRI, bestfit)


"""
遗传算法寻优结果对应含义
best_ka：缓冲系数
best_kb：降水 P 的调节参数
best_kc：温度 T 的函数方差
best_q：平均感染期
best_r：缓冲系数
best_OPT_PRI：降水 P 的最适降水量
"""

# pd.xlswrite('F:/数字农业/原始代码/训练记录1125.xlsx', best_ka, 'HN最优参数2', 'A1')
# xlswrite('E:\研究生\研究生课题\!!论文\!!20200924-论文修改\6省datav2\训练记录1125.xlsx',best_kb,'HN最优参数2','B1')
# xlswrite('E:\研究生\研究生课题\!!论文\!!20200924-论文修改\6省datav2\训练记录1125.xlsx',best_kc,'HN最优参数2','C1')
# xlswrite('E:\研究生\研究生课题\!!论文\!!20200924-论文修改\6省datav2\训练记录1125.xlsx',best_q,'HN最优参数2','D1')
# xlswrite('E:\研究生\研究生课题\!!论文\!!20200924-论文修改\6省datav2\训练记录1125.xlsx',best_r,'HN最优参数2','E1')
# xlswrite('E:\研究生\研究生课题\!!论文\!!20200924-论文修改\6省datav2\训练记录1125.xlsx',best_OPT_PRI,'HN最优参数2','F1')
# xlswrite('E:\研究生\研究生课题\!!论文\!!20200924-论文修改\6省datav2\训练记录1125.xlsx',bestfit,'HN最优参数2','G1')


# xlswrite('E:\研究生\研究生课题\!!论文\!!20200924-论文修改\6省datav2\训练记录1125.xlsx',mtime,'HN最优参数2','I1')
