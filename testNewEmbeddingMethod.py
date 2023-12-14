import math
import struct
import numpy as np

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


def increment_float(num):
    return math.nextafter(num, math.inf)


def increment_float_numpy(num):
    return np.nextafter(num, np.inf)


def increment_float_dynamic(num):
    decimal_places = str(num)[::-1].find('.')
    increment = 10 ** (-decimal_places)
    return round(num + increment, decimal_places)


def decrement_float_dynamic(num):
    decimal_places = str(num)[::-1].find('.')
    decrement = 10 ** (-decimal_places)
    decremented_num = round(num - decrement, decimal_places)
    if decremented_num == 0 and decimal_places > 0:
        decremented_num = round(num - (decrement / 10), decimal_places)
    return decremented_num

def increment_float_dynamic_2(num):
    num_str = '{:.15f}'.format(num).rstrip('0')
    decimal_places = num_str[::-1].find('.')
    increment = 10 ** (-decimal_places)
    incremented_num = round(num + increment, decimal_places)
    #return format(incremented_num, f'.{decimal_places}f')
    return incremented_num


def decrement_float_dynamic_2(num):
    num_str = '{:.15f}'.format(num).rstrip('0')
    decimal_places = num_str[::-1].find('.')
    decrement = 10 ** (-decimal_places)
    decremented_num = round(num - decrement, decimal_places)
    if decremented_num == 0 and decimal_places > 0:
        decremented_num = round(num - (decrement / 10), decimal_places)
    return format(decremented_num, f'.{decimal_places}f')


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

num = 0.00010
bin_representation = float_to_bin(num)
newNum = bin_to_float(bin_representation)
modyNum = modify_lsb_of_float(num, 1)

print("Number where i want to change LSB: ", num)
print("Float to binary representation: ", bin_representation)
print("Binary to float/int: ", newNum)
print("Modifying LSB of a float/integer num: ", modyNum)
print("Modified LSB to binary: ", float_to_bin(modyNum))
print("Incrementing by the smallest amount using math library: number:", increment_float(num), " binary: ", float_to_bin(increment_float(num)))
print("Incrementing by the smallest amount using numpy library: number:", increment_float_numpy(num), " binary: ", float_to_bin(increment_float(num)))
print("Incrementing by the smallest amount dynamically: number:", increment_float_dynamic_2(num), " binary: ", float_to_bin(increment_float(num)))
print("Decrement by the smallest amount dynamically: number:", decrement_float_dynamic(num), " binary: ", float_to_bin(increment_float(num)))
print("Decrement by the smallest amount dynamically: number:", decrement_float_dynamic_2(num), " binary: ", float_to_bin(increment_float(num)))