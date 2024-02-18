from random import *
import random
from random import seed
import math
from stego.Utils import *
from stego.Embedding_version_2 import embedding
from stego.GeneticAlgorithm_version_2 import GeneticAlgorithm


class WCBLGAlgorithm:
    def __init__(self, cover_path, data, key, BS, mul, n_pop, pc, pm, epoch, eng, use_iwt, progress_callback=None):
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
        self.LL = None
        self.LH = None
        self.HL = None
        self.HH = None
        self.cover_k = None
        self.eng = eng
        self.use_iwt = use_iwt
        self.m, self.n = self.cover_image.shape
        self.max_capacity_per_subband = int(self.m * self.n / (4 * self.mul))
        self.data_bin_HH = None  # binary data for HH subband
        self.data_bin_HL = None
        self.data_bin_LH = None
        self.len_data_HH = 0    # len of binary data
        self.len_data_HL = 0
        self.len_data_LH = 0
        self.len_data_HH_block = 0  # len of binary data per block
        self.len_data_HL_block = 0
        self.len_data_LH_block = 0
        self.NumRows = self.m // self.BS
        self.NumCols = self.n // self.BS
        self.progress_callback = progress_callback


    def adjust_max_capacity_per_subband(self):
        block_number = self.NumRows * self.NumCols
        remainder = self.max_capacity_per_subband % block_number
        self.max_capacity_per_subband -= remainder

    def fill_data_for_block_number(self, data_bin, data_len): # in extraction erase last fill_data_len
        block_number = self.NumRows * self.NumCols
        remainder = data_len % block_number
        if remainder ==0:
            return data_bin, data_len
        fill_data_len = block_number - remainder
        data_len += fill_data_len
        data_bin += "0" * fill_data_len
        return data_bin, data_len

    def prepare_algorithm(self):
        data_bin = string_to_bin(self.data)
        data_len = len(data_bin)
        self.adjust_max_capacity_per_subband()
        if data_len > 3 * self.max_capacity_per_subband:
            print("not enough space in picture")
            return False

        self.stego_image = np.zeros_like(self.cover_image, dtype=self.cover_image.dtype)
        block_number = self.NumRows * self.NumCols

        # if numbers are not divisible , reminder will be lost which means part of message
        # is not embeded, or we fill message with spaces
        # if data_len % block_number != 0:
        # return False

        # self.len_data = data_len // block_number

        if data_len <= self.max_capacity_per_subband:
            # if not dividible
            self.data_bin_HH = data_bin
            self.len_data_HH = data_len
            self.len_data_HH_block = self.len_data_HH // block_number
            return True
        if data_len <= 2 * self.max_capacity_per_subband:
            self.data_bin_HH = data_bin[0: self.max_capacity_per_subband]
            self.len_data_HH = self.max_capacity_per_subband
            self.len_data_HH_block = self.len_data_HH // block_number
            if self.len_data_HH % block_number != 0:
                print("max len data per block not dividible by block number")
                return False
            self.data_bin_HL = data_bin[self.max_capacity_per_subband:]
            self.len_data_HL = data_len - self.max_capacity_per_subband
            #if image size and block size are nicely choosen this is not neccesery
            self.data_bin_HL, self.len_data_HL = self.fill_data_for_block_number(self.data_bin_HL, self.len_data_HL)
            self.len_data_HL_block = self.len_data_HL // block_number
            if self.len_data_HL % block_number != 0:
                print("max len data per block not dividible by block number")
                return False
            return True
        self.data_bin_HH = data_bin[0: self.max_capacity_per_subband]
        self.len_data_HH = self.max_capacity_per_subband
        self.len_data_HH_block = self.len_data_HH // block_number
        if self.len_data_HH % block_number != 0:
            print("max len data per block not dividible by block number")
            return False
        self.data_bin_HL = data_bin[self.max_capacity_per_subband: 2 * self.max_capacity_per_subband]
        self.len_data_HL = self.max_capacity_per_subband
        self.len_data_HL_block = self.len_data_HL // block_number
        if self.len_data_HL % block_number != 0:
            print("max len data per block not dividible by block number")
            return False
        self.data_bin_LH = data_bin[2 * self.max_capacity_per_subband:]
        self.len_data_LH = data_len - 2 * self.max_capacity_per_subband
        self.data_bin_LH, self.len_data_LH = self.fill_data_for_block_number(self.data_bin_LH, self.len_data_LH)
        self.len_data_LH_block = self.len_data_LH // block_number
        if self.len_data_LH % block_number != 0:
            print("max len data per block not dividible by block number")
            return False
        return True

    def wcblg(self):

        k = 1
        BestSeeds = []

        for i in range(self.NumRows):
            for j in range(self.NumCols):
                # Extraction of blocks
                # prepares covek_k
                self.GetSubBlCoverK(i, j)

                # DWT or IWT transformation
                if self.use_iwt:
                    self.LL, self.LH, self.HL, self.HH = IWT_version_2(self.cover_k, self.eng)
                else:
                    self.LL, self.LH, self.HL, self.HH = DWT_version_2(self.cover_k, self.eng)

                HLS = self.HL
                LHS = self.LH
                data_k_HL = None
                can_loc_HL = None
                HL_prim = None
                HL_keys = None

                data_k_LH = None
                can_loc_LH = None
                LH_prim = None
                LH_keys = None

                data_k_HH = self.GetSubBlDataK(self.data_bin_HH, self.len_data_HH_block, k)
                can_loc_HH, HH_prim, HH_keys = self.SelEmbLocForSubband(self.HH, self.len_data_HH_block)

                if self.data_bin_HL is not None:
                    data_k_HL = self.GetSubBlDataK(self.data_bin_HL, self.len_data_HL_block, k)
                    can_loc_HL, HL_prim, HL_keys = self.SelEmbLocForSubband(self.HL, self.len_data_HL_block)

                if self.data_bin_LH is not None:
                    data_k_LH = self.GetSubBlDataK(self.data_bin_LH, self.len_data_LH_block, k)
                    can_loc_LH, LH_prim, LH_keys = self.SelEmbLocForSubband(self.LH, self.len_data_LH_block)

                genericAlgorithm = GeneticAlgorithm(self.n_pop, self.pc, self.pm, self.epoch, can_loc_HH, can_loc_HL,
                                                    can_loc_LH, self.cover_k, self.LL, self.LH, self.HL, self.HH,
                                                    HH_prim, HL_prim, LH_prim, data_k_HH, data_k_HL, data_k_LH,
                                                    self.mul, self.key, HH_keys, HL_keys, LH_keys, self.eng,
                                                    self.use_iwt)
                bestseedk = genericAlgorithm.findBestKey()
                BestSeeds.append(bestseedk)

                # Data embeding
                HHS = embedding(self.HH, HH_prim, can_loc_HH, bestseedk, data_k_HH, self.mul, HH_keys, self.use_iwt)
                if data_k_HL is not None:
                    HLS = embedding(self.HL, HL_prim, can_loc_HL, bestseedk, data_k_HL, self.mul, HL_keys, self.use_iwt)
                if data_k_LH is not None:
                    LHS = embedding(self.LH, LH_prim, can_loc_LH, bestseedk, data_k_LH, self.mul, LH_keys, self.use_iwt)

                # IDWT or IIWT transformation
                if self.use_iwt:
                    stego_k = IIWT_version_2(self.LL, LHS, HLS, HHS, self.eng)
                else:
                    stego_k = IDWT_version_2(self.LL, LHS, HLS, HHS, self.eng)

                # Putting blocks together
                self.SetSubBl(stego_k, i, j)

                if self.progress_callback:
                    self.progress_callback(k)

                print('Iteracija: ', k)
                k += 1


        return BestSeeds, self.stego_image

    # Update progress bar method
    def update_progress_bar(self, increment):
        self.progress["value"] += increment
        self.window.update_idletasks()

    def SelEmbLocForSubband(self, subband, len_data_block):
        seed(self.key)
        n, m = subband.shape
        subband_keys = {}
        subband_prim = np.zeros((n, m), dtype=int)
        for i, item in enumerate(subband):
            for j, num in enumerate(item):
                r = random.random()
                subband_keys[str(i) + "," + str(j)] = r
                num_int = int(round(num))
                if num_int % 2 == 0:
                    subband_prim[i, j] = num_int     # previously here was num instead of num_int
                else:
                    if r <= 0.5:
                        subband_prim[i, j] = num_int + 1     # previously here was num instead of num_int
                    else:
                        subband_prim[i, j] = num_int - 1     # previously here was num instead of num_int
        edges = np.zeros((n, m), dtype=int)
        for i in range(n):
            for j in range(m):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if i + x < 0 or i + x >= n or j + y < 0 or j + y >= m:
                            continue
                        edges[i, j] += abs(subband_prim[i + x, j + y]) # edges[i, j] += abs(subband_prim[i + x + 1, j + y + 1])
        edges_array = edges.flatten()
        # edges_array[::-1].sort() this could cause a problem becaue we do not hold values of sorted array
        edges_array.sort()
        edges_array = edges_array[::-1]

        element_number = math.ceil(self.mul * len_data_block)
        if len(edges_array) < element_number:
            print("No place for embedding.")
            return None, None
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

        return can_loc, subband_prim, subband_keys  # returns locations in HH with hihgest edge and HHPrim(like HH but all even)


    def GetSubBlCoverK(self, i, j):
        Starti = i * self.BS
        Startj = j * self.BS
        Endi = (i + 1) * self.BS
        Endj = (j + 1) * self.BS
        self.cover_k = self.cover_image[Starti: Endi, Startj: Endj]

    def GetSubBlDataK(self, data_bin, len_data_block,  k):
        return data_bin[(k - 1) * len_data_block: k * len_data_block]

    def SetSubBl(self, stego_k, i, j):
        Starti = i * self.BS
        Startj = j * self.BS
        Endi = (i + 1) * self.BS
        Endj = (j + 1) * self.BS
        self.stego_image[Starti:Endi, Startj:Endj] = stego_k
