from random import *
import random
from random import seed
import math
import struct
from Utils import *


def embedding(HH, HHprim, can_loc, best_seed, data_k, mul, HH_keys, use_iwt):
    seed(int(best_seed))
    lenData = len(data_k)
    element_number = math.ceil(mul * lenData)
    seq = random.sample(range(0, element_number), lenData)
    # best_loc = can_loc[seq]  # ovo je matrica parova indexa sekvence [(1,2),(2,2)]
    best_loc = [can_loc[i] for i in seq]
    d = 0
    HHS = HH
    if use_iwt:
        for i, j in best_loc:
            data_part = int(data_k[d])
            num = int(round(HHprim[i, j]))
            if num % 2 != data_part:

                r = HH_keys[str(i) + "," + str(j)]
                if r <= 0.5:
                    HHS[i, j] = HHprim[i, j] - 1
                else:
                    HHS[i, j] = HHprim[i, j] + 1
            else:
                HHS[i, j] = HHprim[i, j]
            d += 1
    else:
        for i, j in best_loc:
            data_part = int(data_k[d])
            num = int(round(HHprim[i, j]))
            if num % 2 != data_part:

                r = HH_keys[str(i) + "," + str(j)]
                if r <= 0.5:
                    decimal_places = str(HHprim[i, j])[::-1].find('.')
                    decrement = 10 ** (-decimal_places)
                    HHS[i, j] = round(HHprim[i, j] - decrement, decimal_places)
                else:
                    decimal_places = str(HHprim[i, j])[::-1].find('.')
                    increment = 10 ** (-decimal_places)
                    HHS[i, j] = round(HHprim[i, j] + increment, decimal_places)
            else:
                HHS[i, j] = HHprim[i, j]
            d += 1
    return HHS
