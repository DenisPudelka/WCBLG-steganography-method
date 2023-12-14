from random import *
import random
from random import seed
import numpy as np
import math
import cv2
from Utils import *
from Embedding import embedding
from GeneticAlgorithm import GeneticAlgorithm
import tifffile


class WCBLGAlgorithm:
    def __init__(self, cover_path, data, key, BS, mul, n_pop, pc, pm, epoch, eng, use_iwt):
        self.cover_image = cover_path
        self.stego_image = None
        self.data = data
        self.key = key
        self.BS = BS
        self.mul = mul
        self.n_pop = n_pop
        self.pc = pc
        self.pm = pm
        self.epoch = epoch
        self.len_data = None
        self.can_loc = None
        self.LL = None
        self.LH = None
        self.HL = None
        self.HH = None
        self.subband_prim = None
        self.cover_k = None
        self.data_k = None
        self.subband_keys = {}
        self.eng = eng
        self.use_iwt = use_iwt
        self.data_bin_by_subband = []


    def number_of_quarters(self, L):
        m, n = self.cover_image.shape
        if L < m * n / (4 * self.mul):
            return 1
        if L < 2 * m * n / (4 * self.mul):
            return 2
        if L < 3 * m * n / (4 * self.mul):
            return 3
        return -1


    def get_subband_s(self, BestSeeds, subband):
        # for HH
        # selekcija lokacije za embedovanje
        self.SelEmbLocForSubband(subband)

        # GA
        genericAlgorithm = GeneticAlgorithm(self.n_pop, self.pc, self.pm, self.epoch, self.can_loc,
                                            self.cover_k, self.LL, self.LH, self.HL, self.HH, self.subband_prim,
                                            self.data_k, self.mul, self.key, self.subband_keys, self.eng, self.use_iwt)
        bestseedk = genericAlgorithm.findBestKey()  # treba da se popravi
        BestSeeds.append(bestseedk)

        # Embedovanje data
        subband_s = embedding(subband, self.subband_prim, self.can_loc, bestseedk, self.data_k, self.mul, self.subband_keys,
                        self.use_iwt)
        return subband_s


    def extract_data_by_subbands(self, number_of_quarters):
        data_bin = string_to_bin(self.data)
        L = len(data_bin)
        subband_part = L / number_of_quarters
        for i in range(number_of_quarters):
            self.data_bin_by_subband.append(data_bin[i * subband_part : (i+1) * subband_part])


    def wcblg(self):
        data_bin = string_to_bin(self.data)
        l = len(data_bin)
        number_of_quarters = self.number_of_quarters(l)
        self.extract_data_by_subbands(number_of_quarters)

        if number_of_quarters > 0:
            self.wcblg_for_subband(self.HH, self.data_bin_by_subband[0])
        elif number_of_quarters > 1:
            self.wcblg_for_subband()
        elif number_of_quarters > 2:
            self.wcblg_for_subband()
        else:
            return  None

    def wcblg_for_subband(self, number_of_quarters):
        m, n = self.cover_image.shape
        data_bin  = []

        data_bin = string_to_bin()

        NumRows = m // self.BS
        NumCols = n // self.BS

        block_number = NumRows * NumCols

        L = len(data_bin)
        self.len_data = L // (block_number)  # if numbers are not divisible , reminder will be lost which means part of message is not embeded, or we fill message with spaces

        k = 1
        self.stego_image = np.zeros_like(self.cover_image, dtype=self.cover_image.dtype) # tu mozno dam dtype=image.dtype
        BestSeeds = []


        for i in range(NumRows):
            for j in range(NumCols):
                # Extrakcia blokova
                self.GetSubBlCoverK( i, j)

                # DWT or IWT transformacija
                if self.use_iwt:
                    self.LL, self.LH, self.HL, self.HH = IWT_version_2(self.cover_k, self.eng)
                else:
                    self.LL, self.LH, self.HL, self.HH = DWT_version_2(self.cover_k, self.eng)

                HHS = self.HH
                HLS = self.HL
                LHS = self.LH
                if number_of_quarters > 0:
                    self.GetSubBlDataK(self.data_bin_by_subband[0], k)
                    HHS = self.get_subband_s(BestSeeds, self.HH)
                elif number_of_quarters > 1:
                    self.GetSubBlDataK(self.data_bin_by_subband[1], k)
                    HLS = self.get_subband_s(BestSeeds, self.HL)
                elif number_of_quarters > 2:
                    self.GetSubBlDataK(self.data_bin_by_subband[2], k)
                    LHS = self.get_subband_s(BestSeeds, self.LH)


                subband_s = self.get_subband_s(BestSeeds, subband=0)


                # IDWT or IIWT transformacija
                if self.use_iwt:
                    stego_k = IIWT_version_2(self.LL, LHS, HLS, HHS, self.eng)
                else:
                    stego_k = IDWT_version_2(self.LL, LHS, HLS, HHS, self.eng)

                # Spajanje blokova
                self.SetSubBl(stego_k, i, j)
                print('Iteracija: ', k)
                k += 1

        return BestSeeds, self.stego_image


    def SelEmbLocForSubband(self, subband):
        seed(self.key)
        n, m = subband.shape
        self.subband_keys = {}
        self.subband_prim = np.zeros((n, m))
        for i, item in enumerate(subband):
            for j, num in enumerate(item):
                r = random.random()
                self.subband_keys[str(i) + "," + str(j)] = r
                num_int = int(round(num))
                if num_int % 2 == 0:
                    self.subband_prim[i, j] = num_int     # previously here was num instead of num_int
                else:
                    if r <= 0.5:
                        self.subband_prim[i, j] = num_int + 1     # previously here was num instead of num_int
                    else:
                        self.subband_prim[i, j] = num_int - 1     # previously here was num instead of num_int
        edges = np.zeros((n, m))
        for i in range(n):
            for j in range(m):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if i + x < 0 or i + x >= n or j + y < 0 or j + y >= m:
                            continue
                        edges[i, j] += abs(self.subband_prim[i + x + 1, j + y + 1])
        edges_array = edges.flatten()
        # edges_array[::-1].sort() ovo moze da radi problem jer nikde necuvamo sortirani array
        edges_array.sort()
        edges_array = edges_array[::-1]

        element_number = math.ceil(self.mul * self.len_data)
        if len(edges_array) < element_number:
            print("No place for embedding.")
            return None, None
        treshold = edges_array[element_number - 1]

        self.can_loc = []
        elements_found = 0
        break_loop = False
        for i in range(n):
            for j in range(m):
                if edges[i, j] >= treshold:
                    self.can_loc.append((i, j))
                    elements_found += 1
                if elements_found == element_number:
                    break_loop = True
                    break
            if break_loop:
                break

        return self.can_loc, self.subband_prim  # returns locations in HH with hihgest edge and HHPrim(like HH but all even)


    def GetSubBlCoverK(self, i, j):
        Starti = i * self.BS
        Startj = j * self.BS
        Endi = (i + 1) * self.BS
        Endj = (j + 1) * self.BS
        self.cover_k = self.cover_image[Starti: Endi, Startj: Endj]

    def GetSubBlDataK(self, data_bin, k):
        self.data_k = data_bin[(k - 1) * self.len_data: k * self.len_data]

    def GetSubBl(self, data_bin, i, j, k):
        Starti = i * self.BS
        Startj = j * self.BS
        Endi = (i + 1) * self.BS
        Endj = (j + 1) * self.BS
        self.cover_k = self.cover_image[Starti: Endi, Startj: Endj]
        self.data_k = data_bin[(k - 1) * self.len_data: k * self.len_data]

    def SetSubBl(self, stego_k, i, j):
        Starti = i * self.BS
        Startj = j * self.BS
        Endi = (i + 1) * self.BS
        Endj = (j + 1) * self.BS
        self.stego_image[Starti:Endi, Startj:Endj] = stego_k
