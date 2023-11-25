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
    #HH = HH.astype(int)
    return LL, LH, HL, HH

def IDWT_version_2(LL, LH, HL, HH):
    eng = mylibpkg.initialize()
    dwt_result = eng.perform_idwt(LL,LH,HL,HH,'haar')
    reconstructed_image = np.array(dwt_result)
    eng.terminate()
    return reconstructed_image

def IDWT(LL, LH, HL, HH):
    coeffs = (LL, (LH, HL, HH))
    idwt_result = pywt.idwt2(coeffs, 'db2')
    #idwt_result = np.clip(np.round(idwt_result), 0, 255).astype(np.uint8)
    return idwt_result

def IWT_version_2(coverk):
    eng = mylibpkg.initialize()
    iwt_result = eng.perform_iwt(coverk, 'haar', 1)
    LL = np.squeeze(np.array(iwt_result[0]))
    LH = np.squeeze(np.array(iwt_result[1]))
    HL = np.squeeze(np.array(iwt_result[2]))
    HH = np.squeeze(np.array(iwt_result[3]))
    eng.terminate()
    return LL, LH, HL, HH


