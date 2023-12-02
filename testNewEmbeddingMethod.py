import struct

def float_to_bin(num):
    # Convert a float into its binary representation (as an integer).
    return struct.unpack('>Q', struct.pack('>d', num))[0]

def bin_to_float(binary):
    # Convert a binary representation (as an integer) back into a float.
    return struct.unpack('>d', struct.pack('>Q', binary))[0]

num = 0.000123
bin_representation = float_to_bin(num)
newNum = bin_to_float(bin_representation)

print(bin_representation)
print(newNum)