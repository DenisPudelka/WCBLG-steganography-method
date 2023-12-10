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
        if L < m * n / 4:
            return 1
        if L < 2 * m * n / 4:
            return 2
        if L < 3 * m * n / 4:
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
        pass

    def wcblg_for_subband(self, subband, data_for_subband):
        m, n = self.cover_image.shape
        data_bin = string_to_bin(data_for_subband)

        NumRows = m // self.BS
        NumCols = n // self.BS

        block_number = NumRows * NumCols

        L = len(data_bin)
        self.len_data = L // (block_number)  # if numbers are not divisible , reminder will be lost which means part of message is not embeded, or we fill message with spaces

        k = 1
        self.stego_image = np.zeros_like(self.cover_image, dtype=self.cover_image.dtype) # tu mozno dam dtype=image.dtype
        BestSeeds = []

        number_of_quarters = self.number_of_quarters(L)
        if number_of_quarters == -1:
            return  None, None
        for i in range(NumRows):
            for j in range(NumCols):
                # Extrakcia blokova
                self.GetSubBl(data_bin, i, j, k)

                # DWT or IWT transformacija
                if self.use_iwt:
                    self.LL, self.LH, self.HL, self.HH = IWT_version_2(self.cover_k, self.eng)
                else:
                    self.LL, self.LH, self.HL, self.HH = DWT_version_2(self.cover_k, self.eng)


                if number_of_quarters > 0:
                    # for HH
                    HHS = self.get_subband_s(BestSeeds, self.HH)
                if number_of_quarters > 1:
                    #for HL
                    HLS = self.get_subband_s(BestSeeds, self.HL)


                # for HL
                # selekcija lokacije za embedovanje
                self.SelEmbLocForSubband(self.HL)

                # GA
                genericAlgorithm = GeneticAlgorithm(self.n_pop, self.pc, self.pm, self.epoch, self.can_loc,
                                                    self.cover_k, self.LL, self.LH, self.HL, self.HH, self.subband_prim,
                                                    self.data_k, self.mul, self.key, self.subband_keys, self.eng,
                                                    self.use_iwt)
                bestseedk = genericAlgorithm.findBestKey()  # treba da se popravi
                BestSeeds.append(bestseedk)

                # Embedovanje data
                HHS = embedding(self.HH, self.subband_prim, self.can_loc, bestseedk, self.data_k, self.mul,
                                self.subband_keys, self.use_iwt)

                # IDWT or IIWT transformacija
                if self.use_iwt:
                    stego_k = IIWT_version_2(self.LL, self.LH, self.HL, HHS, self.eng)
                else:
                    stego_k = IDWT_version_2(self.LL, self.LH, self.HL, HHS, self.eng)

                # Spajanje blokova
                self.SetSubBl(stego_k, i, j)
                print('Iteracija: ', k)
                k += 1

        return BestSeeds, self.stego_image


    def wcblg2(self):
        m, n = self.cover_image.shape
        data_bin = string_to_bin(self.data)
        NumRows = m // self.BS
        NumCols = n // self.BS
        totalCapacity = m * n
        HH_Capacity = totalCapacity / 4
        block_number = NumRows * NumCols
        L = len(data_bin)
        self.len_data = L // (block_number)

        if self.len_data <= HH_Capacity:
            # Embed in HH subband
            self.EmbedInHH()
        else:
            # first embed in HH subband
            # get data to embed in HH subband
            self.EmbedInHH()

            # calculate remaining data to embed
            remainingData = 0
            remainingDataLength = 0

            # decide how to spread the rest of data to HL and LH subbands
            HL_capacity = 0
            LH_capacity = 0

            if remainingDataLength <= HL_capacity:
                # embed in HL subband
                self.EmbedInHL()
            elif remainingDataLength <= (HL_capacity + LH_capacity):
                HL_data = 0
                LH_data = 0
                self.EmbedInHL()
                self.EmbedInLH()
            else:
                raise Exception("Data length exceeds the embedding capacity.")



    def embed_data_in_subband(self):
        pass


    def EmbedInHH(self):
        pass

    def EmbedInHL(self):
        pass

    def EmbedInLH(self):
        pass

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
        edges = np.zeros((n - 2, m - 2))
        for i in range(n - 2):
            for j in range(m - 2):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        edges[i, j] += abs(self.subband_prim[i + x + 1, j + y + 1])
        edges_array = edges.flatten()
        # edges_array[::-1].sort() ovo moze da radi problem jer nikde necuvamo sortirani array
        edges_array.sort()
        edges_array = edges_array[::-1]

        element_number = math.ceil(self.mul * self.len_data)
        if len(edges_array) < element_number:
            return None, None
        treshold = edges_array[element_number - 1]

        self.can_loc = []
        elements_found = 0
        break_loop = False
        for i in range(n - 2):
            for j in range(m - 2):
                if edges[i, j] >= treshold:
                    self.can_loc.append((i + 1, j + 1))
                    elements_found += 1
                if elements_found == element_number:
                    break_loop = True
                    break
            if break_loop:
                break

        return self.can_loc, self.subband_prim  # returns locations in HH with hihgest edge and HHPrim(like HH but all even)

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
