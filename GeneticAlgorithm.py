import cProfile
from random import *
import random
import numpy as np
import math
from Embedding import embedding
from Utils import *


class GeneticAlgorithm:
    def __init__(self, n_pop, pc, pm, epoch, can_loc, cover_k, LL, LH, HL, HH, HHprim, data_k, mul, key, HH_keys, eng):
        self.n_pop = n_pop
        self.pc = pc
        self.pm = pm
        self.epoch = epoch
        self.can_loc = can_loc
        self.cover_k = cover_k
        self.LL = LL
        self.LH = LH
        self.HL = HL
        self.HH = HH
        self.HHprim = HHprim
        self.data_k = data_k
        self.pop = np.random.randint(1, high=(2 ** 31) - 1, size=self.n_pop)
        self.mul = mul
        self.key = key
        self.HH_keys = HH_keys
        self.eng = eng

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
        HHS = embedding(self.HH, self.HHprim, self.can_loc, chromo, self.data_k, self.mul, self.HH_keys)
        stego_k = IDWT_version_2(self.LL, self.LH, self.HL, HHS, self.eng)
        #stego_k = IIWT_version_2(self.LL, self.LH, self.HL, HHS, self.eng)
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
