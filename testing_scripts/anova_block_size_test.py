from scipy.stats import f_oneway
import numpy as np

psnr_values = np.array([
    # Entries for "Jet"
    62.112, 62.073, 62.028, 61.997,  # Jet, BS = 512
    62.219, 62.165, 62.193, 62.152,  # Jet, BS = 256
    62.536, 62.571, 62.511, 62.512,  # Jet, BS = 128
    63.245, 63.272, 63.246, 63.243,  # Jet, BS = 64
    # Entries for "Peppers"
    61.966,	61.968,	61.910,	61.903,  # Peppers, BS = 512
    62.165,	62.145,	62.138,	62.093,  # Peppers, BS = 256
    62.530,	62.481,	62.454,	62.462,  # Peppers, BS = 128
    63.194,	63.230,	63.193,	63.168,  # Peppers, BS = 64
    # Entries for "Baboon"
    62.138,	62.072,	61.999,	62.007,  # Baboon, BS = 512
    62.190,	62.141,	62.144,	62.160,  # Baboon, BS = 256
    62.471,	62.498,	62.439,	62.403,  # Baboon, BS = 128
    63.178,	63.198,	63.141,	63.186,  # Baboon, BS = 64
    # Entries for "Lena"
    62.077,	62.011,	62.008,	61.960,  # Lena, BS = 512
    62.186,	62.135,	62.120,	62.099,  # Lena, BS = 256
    62.468,	62.486,	62.422,	62.427,  # Lena, BS = 128
    63.120,	63.075,	63.052,	63.123,  # Lena, BS = 64
    # Entries for "Matches"
    61.985,	61.980,	61.957,	61.927,  # Matches, BS = 512
    62.142,	62.142,	62.148,	62.116,  # Matches, BS = 256
    62.490,	62.429,	62.477,	62.389,  # Matches, BS = 128
    63.167,	63.172,	63.129,	63.182,  # Matches, BS = 64
])

block_sizes = np.array([
    # Entries for "Jet"
    512, 512, 512, 512,  # block size 512
    256, 256, 256, 256,  # block size 256
    128, 128, 128, 128,  # block size 128
    64, 64, 64, 64,  # block size 64
    # Entries for "Peppers"
    512, 512, 512, 512,  # block size 512
    256, 256, 256, 256,  # block size 256
    128, 128, 128, 128,  # block size 128
    64, 64, 64, 64,  # block size 64
    # Entries for "Baboon"
    512, 512, 512, 512,  # block size 512
    256, 256, 256, 256,  # block size 256
    128, 128, 128, 128,  # block size 128
    64, 64, 64, 64,  # block size 64
    # Entries for "Lena"
    512, 512, 512, 512,  # block size 512
    256, 256, 256, 256,  # block size 256
    128, 128, 128, 128,  # block size 128
    64, 64, 64, 64,  # block size 64
    # Entries for "Matches"
    512, 512, 512, 512,  # block size 512
    256, 256, 256, 256,  # block size 256
    128, 128, 128, 128,  # block size 128
    64, 64, 64, 64,  # block size 64
])

# Perform the ANOVA
f_statistic, p_value = f_oneway(psnr_values[block_sizes == 512],
                                psnr_values[block_sizes == 256],
                                psnr_values[block_sizes == 128],
                                psnr_values[block_sizes == 64])

# Print the results for ANOVA
print(f"F-Statistic: {f_statistic}, P-Value: {p_value}")

