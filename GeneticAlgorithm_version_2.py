import cProfile
from random import *
import random
import numpy as np
import math
from Embedding_version_2 import embedding
from Utils import *


class GeneticAlgorithm:
    def __init__(self, n_pop, pc, pm, epoch, can_loc_HH, can_loc_HL, can_loc_LH, cover_k, LL, LH, HL, HH,  HHprim, HLprim, LHprim, data_k_HH, data_k_HL, data_k_LH, mul, key, HH_keys, HL_keys, LH_keys, eng, use_iwt):
        self.n_pop = n_pop
        self.pc = pc
        self.pm = pm
        self.epoch = epoch
        self.can_loc_HH = can_loc_HH
        self.can_loc_HL = can_loc_HL
        self.can_loc_LH = can_loc_LH
        self.cover_k = cover_k
        self.LL = LL
        self.LH = LH
        self.HL = HL
        self.HH = HH
        self.HHprim = HHprim
        self.HLprim = HLprim
        self.LHprim = LHprim
        self.data_k_HH = data_k_HH
        self.data_k_HL = data_k_HL
        self.data_k_LH = data_k_LH
        self.pop = np.random.randint(1, high=(2 ** 31) - 1, size=self.n_pop)
        self.mul = mul
        self.key = key
        self.HH_keys = HH_keys
        self.HL_keys = HL_keys
        self.LH_keys = LH_keys
        self.eng = eng
        self.use_iwt = use_iwt

    def findBestKey(self):

        for i in range(0, self.epoch):
            print("Epocha:" , i)
            pop_cross_over = self.cross_over()
            pop_mut = self.mutation()
            self.pop = np.append(self.pop, pop_cross_over)
            self.pop = np.append(self.pop, pop_mut)
            pop_dict = {key: 0 for key in self.pop}
            self.fitness_population(pop_dict)
            self.pop = self.selection(pop_dict)
            #cProfile.runctx('self.fitness_population(pop_dict)', globals(), locals())

        return self.pop[0]

    def selection(self, pop_dict):
        sorted_pop = sorted(pop_dict, key=pop_dict.get, reverse=True)
        sorted_pop = sorted_pop[:self.n_pop]
        pop_array = np.array(sorted_pop)
        return pop_array

    def mutation(self):
        num_mut = int(self.pm * self.n_pop)
        pop_size = self.pop.size
        num_list = random.sample(range(0, pop_size), num_mut)
        pop_mut = np.zeros(0, dtype=np.int32)
        for i in num_list:
            mutated_chro = self.mutate_chromosome(self.pop[i])
            pop_mut = np.append(pop_mut, mutated_chro)
        return pop_mut

    def mutate_chromosome(self, chromosome):
        k = random.randint(0, 31)
        new_chromosome = chromosome ^ (1 << k)
        return new_chromosome

    def cross_over(self):
        num_cross = int(self.pc * self.n_pop)
        pop_size = self.pop.size
        pop_cross_over = np.zeros(0, dtype=np.int32)
        for i in range(num_cross):
            rand_2_chromo = random.sample(range(0, pop_size), 2)
            child1, child2 = self.cross_over_chromosomes(self.pop[rand_2_chromo[0]], self.pop[rand_2_chromo[1]])
            pop_cross_over = np.append(pop_cross_over, child1)
            pop_cross_over = np.append(pop_cross_over, child2)
        return pop_cross_over

    def cross_over_chromosomes(self, crom1, crom2):
        lower_mask = int('1111111111111111', 2)
        upper_mask = int('11111111111111110000000000000000', 2)

        lower_crom1 = crom1 & lower_mask
        lower_crom2 = crom2 & lower_mask

        upper_crom1 = crom1 & upper_mask
        upper_crom2 = crom2 & upper_mask

        child1 = lower_crom1 | upper_crom2
        child2 = lower_crom2 | upper_crom1
        return child1, child2

    def fitness_population(self, pop_dict):
        for chromo in pop_dict:
            pop_dict[chromo] = self.fitness(chromo)

    def fitness(self, chromo):
        HHS = embedding(self.HH, self.HHprim, self.can_loc_HH, chromo, self.data_k_HH, self.mul, self.HH_keys, self.use_iwt)
        HLS = self.HL
        LHS = self.LH
        if self.HLprim is not None:
            HLS = embedding(self.HL, self.HLprim, self.can_loc_HL, chromo, self.data_k_HL, self.mul, self.HL_keys, self.use_iwt)
        if self.LHprim is not None:
            LHS = embedding(self.LH, self.LHprim, self.can_loc_LH, chromo, self.data_k_LH, self.mul, self.LH_keys, self.use_iwt)
        if self.use_iwt:
            stego_k = IIWT_version_2(self.LL, LHS, HLS, HHS, self.eng)
        else:
            stego_k = IDWT_version_2(self.LL, LHS, HLS, HHS, self.eng)
        return self.picture_fitness(self.cover_k, stego_k)

    def picture_fitness(self, cover, stego_image):
        m, n = cover.shape
        suma = 0

        for i in range(m):
            for j in range(n):
                suma += pow(cover[i, j] - stego_image[i, j], 2)
        MSE = suma / (m * n)

        fitness = 20 * math.log10(255 / math.sqrt(MSE))

        return fitness
