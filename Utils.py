import pywt
from math import floor, ceil
import numpy as np
import random

def string_to_bin(data):
    return ''.join(format(ord(i), '08b') for i in data)

def bin_to_string(binary):
    binary_str = ""
    for item in binary:
        binary_str += str(int(item))
    return ''.join(chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8))

def DWT(coverk):
    coeffs2 = pywt.dwt2(coverk, 'db2')
    LL, (LH, HL, HH) = coeffs2
    #HH = HH.astype(int)
    return LL, LH, HL, HH


def IDWT(LL, LH, HL, HH):
    coeffs = (LL, (LH, HL, HH))
    idwt_result = pywt.idwt2(coeffs, 'db2')

    #idwt_result = np.clip(np.round(idwt_result), 0, 255).astype(np.uint8)

    return idwt_result

def DWT_(image):
    """Apply lifting wavelet transform on a 2D image."""
    rows, cols = image.shape
    transformed_image = np.zeros_like(image)

    # Apply transform on rows
    for i in range(rows):
        transformed_image[i, :] = predict_update_1D(image[i, :])

    # Apply transform on columns
    intermediate_image = np.copy(transformed_image)
    for j in range(cols):
        transformed_image[:, j] = predict_update_1D(intermediate_image[:, j])

    # Divide the image into LL, LH, HL, HH
    half_row, half_col = rows // 2, cols // 2
    LL = transformed_image[:half_row, :half_col]
    LH = transformed_image[half_row:, :half_col]
    HL = transformed_image[:half_row, half_col:]
    HH = transformed_image[half_row:, half_col:]

    return LL, LH, HL, HH

def predict_update_1D(input_data):
    """Perform prediction and update on a 1D sequence."""
    half = len(input_data) // 2
    even_indices = np.arange(0, len(input_data), 2)
    odd_indices = np.arange(1, len(input_data), 2)

    predicted = input_data[odd_indices] - np.floor(input_data[even_indices] / 2)
    updated = input_data[even_indices] + np.floor(predicted / 2)

    result = np.zeros_like(input_data, dtype=input_data.dtype)
    result[even_indices] = updated
    result[odd_indices] = predicted

    return result

def IDWT_(LL, LH, HL, HH):
    """Apply inverse lifting wavelet transform on a 2D image components."""
    rows, cols = LL.shape[0] * 2, LL.shape[1] * 2
    reconstructed_image = np.zeros((rows, cols))

    # Combine subbands
    reconstructed_image[:rows // 2, :cols // 2] = LL
    reconstructed_image[rows // 2:, :cols // 2] = LH
    reconstructed_image[:rows // 2, cols // 2:] = HL
    reconstructed_image[rows // 2:, cols // 2:] = HH

    # Apply inverse transform on columns
    intermediate_image = np.copy(reconstructed_image)
    for j in range(cols):
        reconstructed_image[:, j] = inverse_predict_update_1D(intermediate_image[:, j])

    # Apply inverse transform on rows
    for i in range(rows):
        reconstructed_image[i, :] = inverse_predict_update_1D(reconstructed_image[i, :])

    return reconstructed_image

def inverse_predict_update_1D(transformed_data):
    """Inverse of prediction and update on a 1D sequence."""
    half = len(transformed_data) // 2
    even_indices = np.arange(0, len(transformed_data), 2)
    odd_indices = np.arange(1, len(transformed_data), 2)

    updated = transformed_data[even_indices]
    predicted = transformed_data[odd_indices]

    original_even = updated - np.floor(predicted / 2)
    original_odd = predicted + np.floor(original_even / 2)

    result = np.zeros_like(transformed_data, dtype=transformed_data.dtype)
    result[even_indices] = original_even
    result[odd_indices] = original_odd

    return result