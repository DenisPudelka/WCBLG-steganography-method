from random import *
import random
from random import seed
import math
import struct
from Utils import *


def embedding(subband, subband_prim, can_loc, best_seed, data_k, mul, subband_keys, use_iwt):
    seed(int(best_seed))
    lenData = len(data_k)
    element_number = math.ceil(mul * lenData)
    seq = random.sample(range(0, element_number), lenData)
    # best_loc = can_loc[seq]  # ovo je matrica parova indexa sekvence [(1,2),(2,2)]
    best_loc = [can_loc[i] for i in seq]
    d = 0
    subband_S = subband
    if use_iwt:
        for i, j in best_loc:
            data_part = int(data_k[d])
            num = int(round(subband_prim[i, j]))
            if num % 2 != data_part:

                r = subband_keys[str(i) + "," + str(j)]
                if r <= 0.5:
                    subband_S[i, j] = subband_prim[i, j] - 1
                else:
                    subband_S[i, j] = subband_prim[i, j] + 1
            else:
                subband_S[i, j] = subband_prim[i, j]
            d += 1
    else:
        for i, j in best_loc:
            data_part = int(data_k[d])
            num = int(round(subband_prim[i, j]))
            if num % 2 != data_part:

                r = subband_keys[str(i) + "," + str(j)]
                if r <= 0.5:
                    subband_S[i, j] = subband_prim[i, j] - 1
                else:
                    subband_S[i, j] = subband_prim[i, j] + 1
            else:
                subband_S[i, j] = subband_prim[i, j]
            d += 1
    return subband_S
