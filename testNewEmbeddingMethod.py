import struct

def float_to_bin(num):
    # Convert a float into its binary representation (as an integer).
    return struct.unpack('>Q', struct.pack('>d', num))[0]

def bin_to_float(binary):
    # Convert a binary representation (as an integer) back into a float.
    return struct.unpack('>d', struct.pack('>Q', binary))[0]

def modify_lsb_of_float(num, bit):
    # Modify the LSB of the binary representation of a float.
    binary = float_to_bin(num)
    if (binary & 1) != bit:
        binary ^= 1
    return bin_to_float(binary)

# def embedding(HH, HHprim, can_loc, best_seed, data_k, mul, HH_keys):
#     np.random.seed(int(best_seed))
#     lenData = len(data_k)
#     element_number = int(np.ceil(mul * lenData))
#     seq = np.random.choice(range(element_number), lenData, replace=False)
#     best_loc = [can_loc[i] for i in seq]
#     d = 0
#     HHS = HH.copy()  # Make sure to copy the array if you don't want to modify the original
#     for i, j in best_loc:
#         data_bit = int(data_k[d])
#         float_coeff = HHprim[i, j]
#         modified_coeff = modify_lsb_of_float(float_coeff, data_bit)
#         HHS[i, j] = struct.unpack('>d', modified_coeff)[0]
#         d += 1
#     return HHS

num = 0.000002132
bin_representation = float_to_bin(num)
newNum = bin_to_float(bin_representation)
modyNum = modify_lsb_of_float(num, 1)

print("Float to binary representation: ", bin_representation)
print("Binary to float/int: ", newNum)
print("Modifying LSB of a float/integer num: ", modyNum)