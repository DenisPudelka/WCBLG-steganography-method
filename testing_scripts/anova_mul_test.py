from scipy.stats import f_oneway

# PSNR values for "mul" parameter 1
mul_1_values = [62.112, 62.219, 62.536, 63.245, 61.966, 62.165, 62.530,
                63.194, 62.138, 62.190, 62.471, 63.178, 62.077, 62.186,
                62.468, 63.120, 61.985, 62.490, 63.167]
# PSNR values for "mul" parameter 1.1
mul_1_1_values = [62.073, 62.165, 62.571, 63.272, 61.968, 62.145, 62.481,
                  63.230, 62.072, 62.141, 62.498, 63.198, 62.011, 62.135,
                  62.486, 63.075, 61.980, 62.142, 62.429, 63.172]
# PSNR values for "mul" parameter 1.2
mul_1_2_values = [62.028, 62.193, 62.511, 63.246, 61.910, 62.138,
                  62.454, 63.193, 61.999, 62.144, 62.439, 63.141,
                  62.008, 62.120, 62.422, 63.052, 61.957, 62.148,
                  62.477, 63.129]
# PSNR values for "mul" parameter 1.3
mul_1_3_values = [61.997, 62.152, 62.512, 63.243, 61.903, 62.093,
                  62.462, 63.168, 62.007, 62.160, 62.403, 63.186,
                  61.960, 62.099, 62.427, 63.123, 61.927, 62.116,
                  62.389, 63.182]

# Perform the ANOVA
f_statistic, p_value = f_oneway(mul_1_values, mul_1_1_values, mul_1_2_values, mul_1_3_values)

print(f"F-Statistic: {f_statistic}, P-Value: {p_value}")