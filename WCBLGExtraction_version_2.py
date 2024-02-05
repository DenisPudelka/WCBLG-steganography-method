from random import *
import random
from random import seed
import math
from Utils import *

class WCBLGExtraction:
    def __init__(self, stego_image, key, bs, mul, best_seed, data_len, eng, use_iwt):
        self.stego_image = stego_image
        self.key = key
        self.bs = bs
        self.mul = mul
        self.best_seed = best_seed
        self.data_len = data_len
        self.len_data = None
        # self.stego_k = None
        # self.LL = None
        # self.LH = None
        # self.HL = None
        # self.HHS = None
        # self.HHSprim = None
        # self.can_loc = None
       # self.data_k = None
        self.data = np.zeros(data_len)
        self.message = None
        self.eng = eng
        self.use_iwt = use_iwt
        self.m, self.n = self.stego_image.shape
        self.max_capacity_per_subband = int(self.m * self.n / (4 * self.mul))
        self.data_bin_HH = None  # binary data for HH subband
        self.data_bin_HL = None
        self.data_bin_LH = None
        self.len_data_HH = 0  # len of binary data
        self.len_data_HL = 0
        self.len_data_LH = 0
        self.len_data_HH_block = 0  # len of binary data per block
        self.len_data_HL_block = 0
        self.len_data_LH_block = 0
        self.NumRows = self.m // self.bs
        self.NumCols = self.n // self.bs

    def adjust_max_capacity_per_subband(self):
        block_number = self.NumRows * self.NumCols
        remainder = self.max_capacity_per_subband % block_number
        self.max_capacity_per_subband -= remainder

    def prepare_algorith(self):
        data_bin = string_to_bin(self.data)
        data_len = len(data_bin)

        block_number = self.NumRows * self.NumCols
        self.adjust_max_capacity_per_subband()

        self.stego_image = np.zeros_like(self.cover_image, dtype=self.cover_image.dtype)  # tu mozno dam dtype=image.dtype

        if data_len <= self.max_capacity_per_subband:
            # if not dividible
            self.data_bin_HH = ''
            self.len_data_HH = self.data_len
            self.len_data_HH_block = self.len_data_HH // block_number
            return True
        if self.data_len <= 2 * self.max_capacity_per_subband:
            self.data_bin_HH = ''
            self.len_data_HH = self.max_capacity_per_subband
            self.len_data_HH_block = self.len_data_HH // block_number
            self.data_bin_HL = ''
            self.data_bin_HL = self.data_len - self.max_capacity_per_subband
            # if image size and block size are nicely choosen this is not necessary
            self.data_bin_HL, self.len_data_HL = self.fill_data_for_block_number(self.data_bin_HL, self.len_data_HL)
            self.len_data_HL_block = self.len_data_HL // block_number
            return True
        if data_len <= 3 * self.max_capacity_per_subband:
            self.data_bin_HH = ''
            self.len_data_HH = self.max_capacity_per_subband
            self.len_data_HH_block = self.len_data_HH // block_number

            self.data_bin_HL = ''
            #self.len_data_HL = self.max_capacity_per_subband
            self.len_data_HL_block = self.len_data_HL // block_number

            self.data_bin_LH = ''
            self.len_data_LH = self.data_len - 2 * self.max_capacity_per_subband
            #self.data_bin_LH, self.len_data_LH = self.fill_data_for_block_number(self.data_bin_LH, self.len_data_LH)
            self.len_data_LH_block = self.len_data_LH // block_number
            return True
        if self.data_len > 3 * self.max_capacity_per_subband:
            print("Not enough space")
            return False
        return True

    def extract_data(self):

        k = 1
        for i in range(self.NumRows):
            for j in range(self.NumCols):
                # Get sub block
                stego_k = self.getSubBl(i, j)

                # Wavelet transformation
                if self.use_iwt:
                    LLS, LHS, HLS, HHS = IWT_version_2(stego_k, self.eng)
                else:
                    LLS, LHS, HLS, HHS = DWT_version_2(stego_k, self.eng)

                # Selection of Embeding Location
                can_loc_HH = self.selEmbLoc(HHS)
                data_k_HH = self.extraction(k, HHS, can_loc_HH)

                if self.data_bin_HL is not None:
                    can_loc_HL = self.selEmbLoc(HLS)
                    data_k_HL = self.extraction(k, HHS, can_loc_HL)

                if self.data_bin_LH is not None:
                    can_loc_LH = self.selEmbLoc(LHS)
                    data_k_LH = self.extraction(k, HHS, can_loc_LH)


                # Set sub block
                self.setSubBl(k, data_k)

                k += 1

        self.message = bin_to_string(self.data)
        for i in self.message:
            print(i + '\n')

        return self.message

    def setSubBl(self, k, data_k, len_data_subband, data_subband):
        start_index = (k - 1) * len_data_subband
        end_index = k * len_data_subband
        data_subband[start_index: end_index] = data_k

    def getSubBl(self, i, j):
        start_i = i * self.bs
        start_j = j * self.bs
        end_i = (i + 1) * self.bs
        end_j = (j + 1) * self.bs
        return self.stego_image[start_i: end_i, start_j: end_j]

    def selEmbLoc(self, subband_s):
        seed(self.key)

        n, m = subband_s.shape

        subband_s_prim = np.zeros((n, m))
        for i, item in enumerate(subband_s):
            for j, num in enumerate(item):
                r = random.random()
                num_int = int(round(num))
                if num_int % 2 == 0:
                    subband_s_prim[i, j] = num_int    # previously here was num instead of num_int
                else:
                    if r <= 0.5:
                        subband_s_prim[i, j] = num_int + 1    # previously here was num instead of num_int
                    else:
                        subband_s_prim[i, j] = num_int - 1    # previously here was num instead of num_int
        edges = np.zeros((n, m))
        for i in range(n):
            for j in range(m):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if i + x < 0 or i + x >= n or j + y < 0 or j + y >= m:
                            continue
                        edges[i, j] += abs(subband_s_prim[i + x, j + y])
        edges_array = edges.flatten()
        edges_array[::-1].sort()

        element_number = math.ceil(self.mul * self.len_data)

        treshold = edges_array[element_number - 1]

        can_loc = []
        elements_found = 0
        break_loop = False
        for i in range(n):
            for j in range(m):
                if edges[i, j] >= treshold:  # mozda udje vise indexa u can_loc jer moze par njih biti == T
                    can_loc.append((i, j))
                    elements_found += 1
                if elements_found == element_number:
                    break_loop = True
                    break
            if break_loop:
                break

        return can_loc,  # returns locations in HH with hihgest edge and HHPrim(like HH but all even)

    def extraction(self, k, subband_s, can_loc, len_data_subband):
        data_k = np.zeros(self.len_data)

        #best_seed_k = self.best_seed[k * 32: (k + 1) * 32]      #treba srediti keys da bi znali kako da ih saljemo(kao lsitu ili str)
        best_seed_k = self.best_seed[k - 1]
        #np.random.seed(best_seed_k)
        seed(int(best_seed_k))
        element_number = math.ceil(self.mul * self.len_data)
        #seq = np.random.choice(range(int(self.mul * self.len_data)), size=self.len_data, replace=False) #dodati ovo u embedding
        seq = random.sample(range(0, element_number), self.len_data)
        best_loc = [can_loc[i] for i in seq]

        d = 0
        for i, j in best_loc:
            num = int(round(subband_s[i, j]))
            data_k[d] = int(num % 2)
            d += 1
        return data_k