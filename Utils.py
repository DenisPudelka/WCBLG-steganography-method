import pywt
import numpy as np
import mylibpkg

def string_to_bin(data):
    return ''.join(format(ord(i), '08b') for i in data)

def bin_to_string(binary):
    binary_str = ""
    for item in binary:
        binary_str += str(int(item))
    return ''.join(chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8))

def color_to_gray_matlab(image):
    eng = mylibpkg.initialize()
    image_matlab_gray = eng.convert_rgb_to_gray(image)
    image_gray = np.array(image_matlab_gray)
    eng.terminate()
    return image_gray

def convert_image_to_datatype_matlab(image, data_type):
    # uint8, uint16, single, double
    eng = mylibpkg.initialize()
    image_matlab_converted = eng.convert_image_to_datatype(image, data_type)
    image_converted = np.array(image_matlab_converted)
    eng.terminate()
    return image_converted

def convert_image_datatype(image, data_type):
    # np.uint8, np.uint16, np.int8, np.int16, np.float32, np.float64
    if image.dtype != data_type:
        return image.astype(data_type)
    return image

def save_image():
    pass

def DWT_version_2(coverk):
    eng = mylibpkg.initialize()
    dwt_result = eng.perform_dwt(coverk, 'haar')
    LL = np.array(dwt_result[0])
    LH = np.array(dwt_result[1])
    HL = np.array(dwt_result[2])
    HH = np.array(dwt_result[3])
    eng.terminate()
    return LL, LH, HL, HH

def DWT(coverk):
    coeffs2 = pywt.dwt2(coverk, 'db2')
    LL, (LH, HL, HH) = coeffs2
    return LL, LH, HL, HH

def IDWT_version_2(LL, LH, HL, HH):
    eng = mylibpkg.initialize()
    idwt_result = eng.perform_idwt(LL,LH,HL,HH,'haar')
    reconstructed_image = np.array(idwt_result)
    eng.terminate()
    return reconstructed_image

def IDWT(LL, LH, HL, HH):
    coeffs = (LL, (LH, HL, HH))
    idwt_result = pywt.idwt2(coeffs, 'db2')
    return idwt_result

def IWT_version_2(coverk):
    eng = mylibpkg.initialize()
    iwt_result = eng.perform_iwt(coverk, 'haar', 1)
    LL = np.array(iwt_result[0])
    LH = np.array(iwt_result[1][0])
    HL = np.array(iwt_result[2][0])
    HH = np.array(iwt_result[3][0])
    eng.terminate()
    return LL, LH, HL, HH

def IIWT_version_2(LL, LH, HL, HH):
    eng = mylibpkg.initialize()
    iiwt_result = eng.perform_iiwt_version2(LL, LH, HL, HH, 'haar', 0)
    reconstructed_image = np.array(iiwt_result)
    eng.terminate()
    return reconstructed_image

