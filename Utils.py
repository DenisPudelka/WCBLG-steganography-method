import pywt
import numpy as np
import struct
import os
import tifffile


def string_to_bin(data):
    return ''.join(format(ord(i), '08b') for i in data)


def bin_to_string(binary):
    binary_str = ""
    for item in binary:
        binary_str += str(int(item))
    return ''.join(chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8))


def float_to_bin(num):
    return struct.unpack('>Q', struct.pack('>d', num))[0]


def bin_to_float(binary):
    return struct.unpack('>d', struct.pack('>Q', binary))[0]


def modify_lsb_of_float(num, bit):
    binary = float_to_bin(num)
    if (binary & 1) != bit:
        binary ^= 1
    return bin_to_float(binary)


def color_to_gray_matlab(image, eng):
    image_matlab_gray = eng.convert_rgb_to_gray(image)
    image_gray = np.array(image_matlab_gray)
    return image_gray


def convert_image_to_datatype_matlab(image, data_type, eng):
    # uint8, uint16, single, double
    image_matlab_converted = eng.convert_image_to_datatype(image, data_type)
    image_converted = np.array(image_matlab_converted)
    return image_converted


def convert_image_datatype(image, data_type):
    # np.uint8, np.uint16, np.int8, np.int16, np.float32, np.float64
    if image.dtype != data_type:
        return image.astype(data_type)
    return image


def save_image(image, file_path):
    tags = {
        'dtype': str(image.dtype),
        'shape': image.shape,
        'compression': None,
        'photometric': 'minisblack',
        'planarconfig': 'contig',
        'resolution': (1, 1),
        'description': 'This is a {} TIF image'.format(image.dtype)
    }
    tifffile.imwrite(file_path, image, **tags)


def write_seeds_to_file(seeds, file_name, directory='seeds_keys'):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w') as file:
        file.write('\n'.join(str(seed) for seed in seeds))


def save_hidden_message(message, file_path):
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        file_path = os.path.join(file_path, "hidden_message.txt")

        with open(file_path, 'w') as file:
            file.write(message)

        print(f"Hidden message successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving hidden message: {e}")


def read_seeds_from_file(file_name):
    file_path = os.path.join(file_name)

    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    seeds = [int(line.strip()) for line in lines if line.strip()]
    return seeds


def read_message(file_path):
    try:
        with open(file_path, 'r') as file:
            message = file.read()
        return message
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def DWT_version_2(coverk, eng):
    # we send image that can be type of double, single, uint8, probably also (uint16)
    coverk_contiguous = np.ascontiguousarray(coverk)
    dwt_result = eng.perform_dwt(coverk_contiguous, 'bior1.1')
    # this returns me always double
    LL = np.array(dwt_result[0])
    LH = np.array(dwt_result[1])
    HL = np.array(dwt_result[2])
    HH = np.array(dwt_result[3])
    return LL, LH, HL, HH


def DWT(coverk):
    coeffs2 = pywt.dwt2(coverk, 'db2')
    LL, (LH, HL, HH) = coeffs2
    return LL, LH, HL, HH


def IDWT_version_2(LL, LH, HL, HH, eng):
    LL_contiguous = np.ascontiguousarray(LL)
    LH_contiguous = np.ascontiguousarray(LH)
    HL_contiguous = np.ascontiguousarray(HL)
    HH_contiguous = np.ascontiguousarray(HH)
    idwt_result = eng.perform_idwt(LL_contiguous, LH_contiguous, HL_contiguous, HH_contiguous, 'bior1.1')
    reconstructed_image = np.array(idwt_result)
    return reconstructed_image


def IDWT(LL, LH, HL, HH):
    coeffs = (LL, (LH, HL, HH))
    idwt_result = pywt.idwt2(coeffs, 'db2')
    return idwt_result


def IWT_version_2(coverk, eng):
    coverk_contiguous = np.ascontiguousarray(coverk)
    iwt_result = eng.perform_iwt(coverk_contiguous, 'haar', 1)
    LL = np.array(iwt_result[0])
    LH = np.array(iwt_result[1][0])
    HL = np.array(iwt_result[2][0])
    HH = np.array(iwt_result[3][0])
    return LL, LH, HL, HH


def IIWT_version_2(LL, LH, HL, HH, eng):
    iiwt_result = eng.perform_iiwt_version2(LL, LH, HL, HH, 'haar', 0)
    reconstructed_image = np.array(iiwt_result)
    return reconstructed_image

