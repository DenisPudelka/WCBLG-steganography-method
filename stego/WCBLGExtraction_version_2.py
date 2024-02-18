from random import *
import random
from random import seed
import math
from stego.Utils import *

class WCBLGExtraction:
    def __init__(self, stego_image, key, bs, mul, best_seed, data_len, eng, use_iwt, progress_callback=None):
        self.stego_image = stego_image
        self.key = key
        self.bs = bs
        self.mul = mul
        self.best_seed = best_seed
        self.data_len = data_len
        self.eng = eng
        self.use_iwt = use_iwt
        self.m, self.n = self.stego_image.shape
        self.max_capacity_per_subband = int(self.m * self.n / (4 * self.mul))
        self.data_bin_HH = None
        self.data_bin_HL = None
        self.data_bin_LH = None
        self.len_data_HH = 0
        self.len_data_HL = 0
        self.len_data_LH = 0
        self.len_data_HH_block = 0
        self.len_data_HL_block = 0
        self.len_data_LH_block = 0
        self.NumRows = self.m // self.bs
        self.NumCols = self.n // self.bs
        self.progress_callback = progress_callback

    def adjust_max_capacity_per_subband(self):
        block_number = self.NumRows * self.NumCols
        remainder = self.max_capacity_per_subband % block_number
        self.max_capacity_per_subband -= remainder

    def prepare_algorithm(self):
        self.adjust_max_capacity_per_subband()
        if self.data_len > 3 * self.max_capacity_per_subband:
            print("not enough space in picture")
            return False

        block_number = self.NumRows * self.NumCols

        if self.data_len <= self.max_capacity_per_subband:
            self.data_bin_HH = np.zeros(self.data_len, dtype=int)
            self.len_data_HH = self.data_len
            self.len_data_HH_block = self.len_data_HH // block_number
            return True
        if self.data_len <= 2 * self.max_capacity_per_subband:
            self.len_data_HH = self.max_capacity_per_subband
            self.data_bin_HH = np.zeros(self.len_data_HH, dtype=int)
            self.len_data_HH_block = self.len_data_HH // block_number

            self.len_data_HL = self.data_len - self.max_capacity_per_subband
            self.data_bin_HL = np.zeros(self.len_data_HL, dtype=int)
            self.len_data_HL_block = self.len_data_HL // block_number

            return True
        self.len_data_HH = self.max_capacity_per_subband
        self.data_bin_HH = np.zeros(self.len_data_HH, dtype=int)
        self.len_data_HH_block = self.len_data_HH // block_number

        self.len_data_HL = self.max_capacity_per_subband
        self.data_bin_HL = np.zeros(self.len_data_HL, dtype=int)
        self.len_data_HL_block = self.len_data_HL // block_number

        self.len_data_LH = self.data_len - 2 * self.max_capacity_per_subband
        self.data_bin_LH = np.zeros(self.len_data_LH, dtype=int)
        self.len_data_LH_block = self.len_data_LH // block_number
        return True

    def extract_data(self):

        k = 1
        for i in range(self.NumRows):
            for j in range(self.NumCols):
                # Get sub block
                stego_k = self.getSubBl(i, j)

                # Wavelet transformation
                if self.use_iwt:
                    LL, LHS, HLS, HHS = IWT_version_2(stego_k, self.eng)
                else:
                    LL, LHS, HLS, HHS = DWT_version_2(stego_k, self.eng)

                # Selection of Embeding Location
                can_loc_HH = self.selEmbLoc(HHS, self.len_data_HH_block)
                data_k_HH = self.extraction(k, HHS, can_loc_HH, self.len_data_HH_block)
                self.setSubBl(k, data_k_HH, self.len_data_HH_block, self.data_bin_HH)

                if self.data_bin_HL is not None:
                    can_loc_HL = self.selEmbLoc(HLS, self.len_data_HL_block)
                    data_k_HL = self.extraction(k, HLS, can_loc_HL, self.len_data_HL_block)
                    self.setSubBl(k, data_k_HL, self.len_data_HL_block, self.data_bin_HL)

                if self.data_bin_LH is not None:
                    can_loc_LH = self.selEmbLoc(LHS, self.len_data_LH_block)
                    data_k_LH = self.extraction(k, LHS, can_loc_LH, self.len_data_LH_block)
                    self.setSubBl(k, data_k_LH, self.len_data_LH_block, self.data_bin_LH)

                if self.progress_callback:
                    self.progress_callback(k)
                k += 1

        data = self.data_bin_HH
        if self.data_bin_HL is not None:
            data = np.append(data, self.data_bin_HL)

        if self.data_bin_LH is not None:
            data = np.append(data, self.data_bin_LH)

        message = bin_to_string(data)

        return message

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

    def selEmbLoc(self, subband_s, len_data_subband):
        seed(self.key)

        n, m = subband_s.shape

        subband_s_prim = np.zeros((n, m), dtype=int)
        for i, item in enumerate(subband_s):
            for j, num in enumerate(item):
                r = random.random()
                num_int = int(round(num))
                if num_int % 2 == 0:
                    subband_s_prim[i, j] = num_int
                else:
                    if r <= 0.5:
                        subband_s_prim[i, j] = num_int + 1
                    else:
                        subband_s_prim[i, j] = num_int - 1
        edges = np.zeros((n, m), dtype=int)
        for i in range(n):
            for j in range(m):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if i + x < 0 or i + x >= n or j + y < 0 or j + y >= m:
                            continue
                        edges[i, j] += abs(subband_s_prim[i + x, j + y])
        edges_array = edges.flatten()
        edges_array[::-1].sort()

        element_number = math.ceil(self.mul * len_data_subband)

        treshold = edges_array[element_number - 1]

        can_loc = []
        elements_found = 0
        break_loop = False
        for i in range(n):
            for j in range(m):
                if edges[i, j] >= treshold:
                    can_loc.append((i, j))
                    elements_found += 1
                if elements_found == element_number:
                    break_loop = True
                    break
            if break_loop:
                break

        return can_loc

    def extraction(self, k, subband_s, can_loc, len_data_subband):
        data_k = np.zeros(len_data_subband, dtype=int)
        best_seed_k = self.best_seed[k - 1]

        seed(int(best_seed_k))
        element_number = math.ceil(self.mul * len_data_subband)

        seq = random.sample(range(0, element_number), len_data_subband)
        best_loc = [can_loc[i] for i in seq]

        d = 0
        for i, j in best_loc:
            num = int(round(subband_s[i, j]))
            data_k[d] = int(num % 2)
            d += 1
        return data_k