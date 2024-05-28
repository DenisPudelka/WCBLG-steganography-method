import numpy as np
import struct
import os
import tifffile


def string_to_bin(data):
    """Converts a string to a binary representation."""
    return ''.join(format(ord(i), '08b') for i in data)


def bin_to_string(binary):
    """Converts a binary string back to a human-readable string."""
    binary_str = ""
    for item in binary:
        binary_str += str(int(item))
    return ''.join(chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8))


def color_to_gray_matlab(image, eng):
    """Converts a color image to grayscale using a MATLAB engine."""
    image_matlab_gray = eng.convert_rgb_to_gray(image)
    image_gray = np.array(image_matlab_gray)
    return image_gray


def convert_image_to_datatype_matlab(image, data_type, eng):
    """Converts an image to a specified data type using a MATLAB engine."""
    # Acceptable datatypes: uint8, uint16, single, double
    image_matlab_converted = eng.convert_image_to_datatype(image, data_type)
    image_converted = np.array(image_matlab_converted)
    return image_converted


def convert_image_datatype(image, data_type):
    """Converts an image to a specified numpy data type."""
    # Acceptable datatypes: np.uint8, np.uint16, np.int8, np.int16, np.float32, np.float64
    if image.dtype != data_type:
        return image.astype(data_type)
    return image


def save_image(image, file_path):
    """Saves an image to a file with metadata tags."""
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
    """Writes seeds to a file in a specified directory."""
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w') as file:
        file.write('\n'.join(str(seed) for seed in seeds))


def save_hidden_message(message, file_path):
    """Saves a hidden message to a file."""
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
    """Reads seeds from a file."""
    file_path = os.path.join(file_name)

    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    seeds = [int(line.strip()) for line in lines if line.strip()]
    return seeds


def read_message(file_path):
    """Reads a message from a file."""
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


def IWT_version_2(coverk, eng):
    """Performs integer wavelet transform using a MATLAB engine."""
    coverk_contiguous = np.ascontiguousarray(coverk)
    iwt_result = eng.perform_iwt(coverk_contiguous, 'haar', 1)
    LL = np.array(iwt_result[0])
    LH = np.array(iwt_result[1][0])
    HL = np.array(iwt_result[2][0])
    HH = np.array(iwt_result[3][0])
    return LL, LH, HL, HH


def IIWT_version_2(LL, LH, HL, HH, eng):
    """Performs inverse integer wavelet transform using a MATLAB engine."""
    iiwt_result = eng.perform_iiwt_version2(LL, LH, HL, HH, 'haar', 0)
    reconstructed_image = np.array(iiwt_result)
    return reconstructed_image

