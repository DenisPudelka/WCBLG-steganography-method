from random import *
import random
from random import seed
import math
from stego.Utils import *
from stego.Embedding_version_2 import embedding
from stego.GeneticAlgorithm_version_2 import GeneticAlgorithm


class WCBLGAlgorithm:
    def __init__(self, cover_path, data, key, BS, mul, n_pop, pc, pm, epoch, eng, progress_callback=None):
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
        self.m, self.n = self.cover_image.shape
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
        self.NumRows = self.m // self.BS
        self.NumCols = self.n // self.BS
        self.progress_callback = progress_callback


    def adjust_max_capacity_per_subband(self):
        """
        Adjusts the maximum capacity per subband by reducing it to the nearest multiple of the number of blocks.
        This ensures that the capacity is a perfect fit for the number of blocks available in the image.
        """
        block_number = self.NumRows * self.NumCols
        remainder = self.max_capacity_per_subband % block_number
        self.max_capacity_per_subband -= remainder

    def fill_data_for_block_number(self, data_bin, data_len):
        """Adjusts the length of binary data to ensure it perfectly fits into the blocks available."""
        block_number = self.NumRows * self.NumCols
        remainder = data_len % block_number
        if remainder == 0:
            return data_bin, data_len
        fill_data_len = block_number - remainder
        data_len += fill_data_len
        data_bin += "0" * fill_data_len
        return data_bin, data_len

    def prepare_algorithm(self):
        """
        Prepares the steganography algorithm for execution. This includes converting the data to binary,
        adjusting for maximum capacity, and splitting the data among the different subbands.
        """
        data_bin = string_to_bin(self.data)
        data_len = len(data_bin)
        self.adjust_max_capacity_per_subband()
        if data_len > 3 * self.max_capacity_per_subband:
            print("Max capacity: ", self.max_capacity_per_subband)
            print("not enough space in picture")
            return False

        self.stego_image = np.zeros_like(self.cover_image, dtype=self.cover_image.dtype)
        block_number = self.NumRows * self.NumCols

        if data_len <= self.max_capacity_per_subband:
            self.data_bin_HH = data_bin
            self.len_data_HH = data_len
            self.data_bin_HH, self.len_data_HH = self.fill_data_for_block_number(self.data_bin_HH, self.len_data_HH)
            self.len_data_HH_block = self.len_data_HH // block_number
            if self.len_data_HH > self.max_capacity_per_subband:
                print("filling data HH overfilled")
                return False
            return True
        if data_len <= 2 * self.max_capacity_per_subband:
            self.data_bin_HH = data_bin[0: self.max_capacity_per_subband]
            self.len_data_HH = self.max_capacity_per_subband
            self.len_data_HH_block = self.len_data_HH // block_number

            self.data_bin_HL = data_bin[self.max_capacity_per_subband:]
            self.len_data_HL = data_len - self.max_capacity_per_subband
            self.data_bin_HL, self.len_data_HL = self.fill_data_for_block_number(self.data_bin_HL, self.len_data_HL)
            self.len_data_HL_block = self.len_data_HL // block_number
            if self.len_data_HL > self.max_capacity_per_subband:
                print("filling data HL overfilled")
                return False
            return True
        self.data_bin_HH = data_bin[0: self.max_capacity_per_subband]
        self.len_data_HH = self.max_capacity_per_subband
        self.len_data_HH_block = self.len_data_HH // block_number

        self.data_bin_HL = data_bin[self.max_capacity_per_subband: 2 * self.max_capacity_per_subband]
        self.len_data_HL = self.max_capacity_per_subband
        self.len_data_HL_block = self.len_data_HL // block_number

        self.data_bin_LH = data_bin[2 * self.max_capacity_per_subband:]
        self.len_data_LH = data_len - 2 * self.max_capacity_per_subband
        self.data_bin_LH, self.len_data_LH = self.fill_data_for_block_number(self.data_bin_LH, self.len_data_LH)
        self.len_data_LH_block = self.len_data_LH // block_number
        if self.len_data_LH > self.max_capacity_per_subband:
            print("filling data LH overfilled")
            return False
        return True

    def wcblg(self):
        """
        This method performs embedding process by blocks of the image, embedding data using genetic algorithm
        and finally reconstructing the stego image.
        """
        k = 1
        BestSeeds = []

        for i in range(self.NumRows):
            for j in range(self.NumCols):
                # Extraction of current block
                self.GetSubBlCoverK(i, j)

                # Performing IWT transformation
                self.LL, self.LH, self.HL, self.HH = IWT_version_2(self.cover_k, self.eng)
                self.HH = self.HH.astype(int)
                self.HL = self.HL.astype(int)
                self.LH = self.LH.astype(int)
                self.LL = self.LL.astype(int)

                # Initializing variables for potential secondary subbands
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

                # Embedding data to the HH subband
                data_k_HH = self.GetSubBlDataK(self.data_bin_HH, self.len_data_HH_block, k)
                can_loc_HH, HH_prim, HH_keys = self.SelEmbLocForSubband(self.HH, self.len_data_HH_block)

                # Embedding data to the HL and LH if they were used
                if self.data_bin_HL is not None:
                    data_k_HL = self.GetSubBlDataK(self.data_bin_HL, self.len_data_HL_block, k)
                    can_loc_HL, HL_prim, HL_keys = self.SelEmbLocForSubband(self.HL, self.len_data_HL_block)

                if self.data_bin_LH is not None:
                    data_k_LH = self.GetSubBlDataK(self.data_bin_LH, self.len_data_LH_block, k)
                    can_loc_LH, LH_prim, LH_keys = self.SelEmbLocForSubband(self.LH, self.len_data_LH_block)

                # Initializing the genetic algorithm with all parameters
                genericAlgorithm = GeneticAlgorithm(self.n_pop, self.pc, self.pm, self.epoch, can_loc_HH, can_loc_HL,
                                                    can_loc_LH, self.cover_k, self.LL, self.LH, self.HL, self.HH,
                                                    HH_prim, HL_prim, LH_prim, data_k_HH, data_k_HL, data_k_LH,
                                                    self.mul, self.key, HH_keys, HL_keys, LH_keys, self.eng)
                # Finding the best seed for the current block
                bestseedk = genericAlgorithm.findBestKey()
                BestSeeds.append(bestseedk)

                # Embedding data into the subbands using the best seed found
                HHS = embedding(self.HH, HH_prim, can_loc_HH, bestseedk, data_k_HH, self.mul, HH_keys)
                if data_k_HL is not None:
                    HLS = embedding(self.HL, HL_prim, can_loc_HL, bestseedk, data_k_HL, self.mul, HL_keys)
                if data_k_LH is not None:
                    LHS = embedding(self.LH, LH_prim, can_loc_LH, bestseedk, data_k_LH, self.mul, LH_keys)

                # Performing IIWT transformation
                stego_k = IIWT_version_2(self.LL, LHS, HLS, HHS, self.eng)

                # Putting blocks together
                self.SetSubBl(stego_k, i, j)

                # Optionally, update progress to UI or console
                if self.progress_callback is not None:
                    self.progress_callback(k)

                print('Iteracija: ', k)
                k += 1

        # Return all best seeds and the final stego image
        return BestSeeds, self.stego_image


    def SelEmbLocForSubband(self, subband, len_data_block):
        """
        Selects the best candidate locations for embedding data within a subband based on edge values.
        """
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
                    subband_prim[i, j] = num_int
                else:
                    if r <= 0.5:
                        subband_prim[i, j] = num_int + 1
                    else:
                        subband_prim[i, j] = num_int - 1
        edges = np.zeros((n, m), dtype=int)
        for i in range(n):
            for j in range(m):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if i + x < 0 or i + x >= n or j + y < 0 or j + y >= m:
                            continue
                        edges[i, j] += abs(subband_prim[i + x, j + y])
        edges_array = edges.flatten()
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
        """Extracts a specific block from the cover image based on the block indices and block size."""
        Starti = i * self.BS
        Startj = j * self.BS
        Endi = (i + 1) * self.BS
        Endj = (j + 1) * self.BS
        self.cover_k = self.cover_image[Starti: Endi, Startj: Endj]

    def GetSubBlDataK(self, data_bin, len_data_block,  k):
        """Retrieves a segment of binary data intended for embedding into a specific block of the image."""
        return data_bin[(k - 1) * len_data_block: k * len_data_block]

    def SetSubBl(self, stego_k, i, j):
        """Writes a modified block back into the stego image at the specified position."""
        Starti = i * self.BS
        Startj = j * self.BS
        Endi = (i + 1) * self.BS
        Endj = (j + 1) * self.BS
        self.stego_image[Starti:Endi, Startj:Endj] = stego_k
