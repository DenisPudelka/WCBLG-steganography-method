from random import *
from random import seed
import math
from Utils import *


class WCBLGExtraction:
    def __init__(self, stego_image, key, bs, mul, best_seed, l, eng):
        self.stego_image = stego_image
        self.key = key
        self.bs = bs
        self.mul = mul
        self.best_seed = best_seed
        self.l = l
        self.len_data = None
        self.stego_k = None
        self.LL = None
        self.LH = None
        self.HL = None
        self.HHS = None
        self.HHSprim = None
        self.can_loc = None
        self.data_k = None
        self.data = np.zeros(l)
        self.message = None
        self.eng = eng

    def extract_data(self):
        m, n = self.stego_image.shape

        num_rows = m // self.bs
        num_cols = n // self.bs

        self.len_data = self.l // (num_rows * num_cols)

        k = 1
        for i in range(num_rows):
            for j in range(num_cols):
                # Get sub block
                self.getSubBl(i, j)

                # Wavelet transformation
                self.LL, self.LH, self.HL, self.HHS = DWT_version_2(self.stego_k, self.eng)

                # Selection of Embeding Location
                self.selEmbLoc()

                # Extraction
                self.extraction(k)

                # Set sub block
                self.setSubBl(k)

                k += 1

        self.message = bin_to_string(self.data)
        for i in self.message:
            print(i + '\n')

        return self.message

    def setSubBl(self, k):
        start_index = (k - 1) * self.len_data
        end_index = k * self.len_data
        self.data[start_index: end_index] = self.data_k

    def getSubBl(self, i, j):
        start_i = i * self.bs
        start_j = j * self.bs
        end_i = (i + 1) * self.bs
        end_j = (j + 1) * self.bs
        self.stego_k = self.stego_image[start_i: end_i, start_j: end_j]

    def selEmbLoc(self):
        seed(self.key)

        n, m = self.HHS.shape

        self.HHSprim = np.zeros((n, m))
        for i, item in enumerate(self.HHS):
            for j, num in enumerate(item):
                r = random.random()
                num_int = int(round(num))
                if num_int % 2 == 0:
                    self.HHSprim[i, j] = num
                else:
                    if r <= 0.5:
                        self.HHSprim[i, j] = num + 1
                    else:
                        self.HHSprim[i, j] = num - 1
        edges = np.zeros((n - 2, m - 2))
        for i in range(n - 2):
            for j in range(m - 2):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        edges[i, j] += abs(self.HHSprim[i + x + 1, j + y + 1])
        edges_array = edges.flatten()
        edges_array[::-1].sort()

        element_number = math.ceil(self.mul * self.len_data)

        treshold = edges_array[element_number - 1]

        self.can_loc = []
        elements_found = 0
        break_loop = False
        for i in range(n - 2):
            for j in range(m - 2):
                if edges[i, j] >= treshold:  # mozda udje vise indexa u can_loc jer moze par njih biti == T
                    self.can_loc.append((i + 1, j + 1))
                    elements_found += 1
                if elements_found == element_number:
                    break_loop = True
                    break
            if break_loop:
                break

        return self.can_loc, self.HHSprim  # returns locations in HH with hihgest edge and HHPrim(like HH but all even)

    def extraction(self, k):
        self.data_k = np.zeros(self.len_data)

        #best_seed_k = self.best_seed[k * 32: (k + 1) * 32]      #treba srediti keys da bi znali kako da ih saljemo(kao lsitu ili str)
        best_seed_k = self.best_seed[k - 1]
        #np.random.seed(best_seed_k)
        seed(int(best_seed_k))
        element_number = math.ceil(self.mul * self.len_data)
        #seq = np.random.choice(range(int(self.mul * self.len_data)), size=self.len_data, replace=False) #dodati ovo u embedding
        seq = random.sample(range(0, element_number), self.len_data)
        best_loc = [self.can_loc[i] for i in seq]

        d = 0
        for i, j in best_loc:
            num = int(round(self.HHS[i, j]))
            self.data_k[d] = int(num % 2)
            d += 1
