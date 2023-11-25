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
    def __init__(self, cover_path, data, key, BS, mul, n_pop, pc, pm, epoch):
        #self.cover_image = tifffile.imread(cover_path)
        self.cover_image = cv2.imread(cover_path,0)
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
        self.HHprim = None
        self.cover_k = None
        self.data_k = None
        self.HH_keys = {}
        self.tags = {
            'dtype': 'float64',
            'shape': self.cover_image.shape,
            'compression': None,
            'photometric': 'minisblack',
            'planarconfig': 'contig',
            'resolution': (1,1),
            'description': 'This is a float64 TIF image'
        }

    # jedno resenje
    # def fillDataWithEmpty(self, data, block_number):
    #     remainder = len(data) % block_number
    #     if remainder != 0:
    #         padding_needed = block_number - remainder
    #         data += '0' * padding_needed  # appending the necessary number of '0's
    #     return data

    def fillDataWithEmpty(self, data, block_number):
        pass

    def wcblg(self):
        m, n = self.cover_image.shape
        data_bin = string_to_bin(self.data)

        NumRows = m // self.BS
        NumCols = n // self.BS

        block_number = NumRows * NumCols
        data_padding = self.fillDataWithEmpty(data_bin, block_number)

        #  jedno moguce resenje
        # L = len(data_padding)
        # self.len_data = L // block_number

        # default resenje
        L = len(data_bin)
        self.len_data = L // (
                NumRows * NumCols)  # if numbers are not divisible , reminder will be lost which means part of message is not embeded, or we fill message with spaces

        k = 1
        self.stego_image = np.zeros_like(self.cover_image, dtype = 'float64')
        BestSeeds = []
        for i in range(NumRows):
            for j in range(NumCols):
                # Extrakcia blokova
                self.GetSubBl(data_bin, i, j, k)

                # DWT transformacija
                self.LL, self.LH, self.HL, self.HH = DWT(self.cover_k)

                # selekcija lokacije za embedovanje
                self.SelEmbLoc()

                # GA
                genericAlgorithm = GeneticAlgorithm(self.n_pop, self.pc, self.pm, self.epoch, self.can_loc,
                                                    self.cover_k, self.LL, self.LH, self.HL, self.HH, self.HHprim,
                                                    self.data_k, self.mul, self.key, self.HH_keys)
                bestseedk = genericAlgorithm.findBestKey()
                BestSeeds.append(bestseedk)

                # Embedovanje data
                HHS = embedding(self.HH, self.HHprim, self.can_loc, bestseedk, self.data_k, self.mul, self.HH_keys)

                # IDWT transformacija
                stego_k = IDWT(self.LL, self.LH, self.HL, HHS)

                # Spajanje blokova
                self.SetSubBl(stego_k, i, j)
                print('jedna iteracija')
                k += 1

        # cv2.imwrite("stego_image.png", Stego)
        # self.stego_image = Stego

        # self.stego_image = self.stego_image.astype(np.float32)

        return BestSeeds, self.stego_image, self.tags

    # self.HH, datak, self.key, self.mul, self.len_data
    def SelEmbLoc(self):
        seed(self.key)

        n, m = self.HH.shape
        self.HH_keys = {}
        self.HHprim = np.zeros((n, m))
        for i, item in enumerate(self.HH):
            for j, num in enumerate(item):
                r = random.random()
                self.HH_keys[str(i) + "," + str(j)] = r
                num_int = int(round(num))
                if num_int % 2 == 0:
                    self.HHprim[i, j] = num
                else:
                    if r <= 0.5:
                        self.HHprim[i, j] = num + 1
                    else:
                        self.HHprim[i, j] = num - 1
        edges = np.zeros((n - 2, m - 2))
        for i in range(n - 2):
            for j in range(m - 2):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        edges[i, j] += abs(self.HHprim[i + x + 1, j + y + 1])
        edges_array = edges.flatten()
        # edges_array[::-1].sort() ovo moze da radi problem jer nikde necuvamo sortirani array
        edges_array.sort()
        edges_array = edges_array[::-1]

        element_number = math.ceil(self.mul * self.len_data)

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

        return self.can_loc, self.HHprim  # returns locations in HH with hihgest edge and HHPrim(like HH but all even)

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
