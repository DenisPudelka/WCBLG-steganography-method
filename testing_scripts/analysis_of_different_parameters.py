from stego.Utils import *
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
import tifffile
import mylibpkg
import math
import cv2


def save_best_seeds(name, best_seeds, path):
    """ Save the best seed values used in the steganography to a specified file."""
    seeds_str = ', '.join(str(seed) for seed in best_seeds)
    with open(path, 'a') as file:
        file.write(f"{name}: {seeds_str}\n")


def save_psnr_values(name, psnr, path):
    """ Save the PSNR values to a file, for later analysis."""
    with open(path, 'a') as file:
        file.write(f"{name}: {psnr}\n")


def create_name(variety, block_size, mul):
    """ Generating a formatted name string combining parameters."""
    return variety + "_" + str(block_size) + "_" + str(mul)


def calculate_psnr_1(cover, stego):
    m, n = cover.shape
    suma = 0

    for i in range(m):
        for j in range(n):
            suma += pow(cover[i, j] - stego[i, j], 2)
    MSE = suma / (m * n)

    fitness = 20 * math.log10(255 / math.sqrt(MSE))

    return fitness


def calculate_psnr_2(cover, stego):
    """ Calculating the PSNR using numpy's mean function to simplify calculation."""
    mse = np.mean((cover - stego) ** 2)
    if mse == 0:
        return float('inf')
    psnr = 20 * math.log10(255 / math.sqrt(mse))
    return psnr


def prepare_image(image):
    row, col = image.shape
    for x in range(row):
        for y in range(col):
            if image[x, y] == 0:
                image[x, y] += 1
            elif image[x, y] == 255:
                image[x, y] -= 1
    return image


def encrypt(image_path, key, Bs, mul, Npop, Pc, Pm, Epoch, message, eng):
    # Read cover image that will be used for embedding message.
    image_original = tifffile.imread(image_path)

    # Convert image to grayscale if not.
    size = len(image_original.shape)
    if size == 3:
        image_original = color_to_gray_matlab(image_original, eng)

    # Prepare image.
    image_original = prepare_image(image_original)

    # Convert image to different datatype.
    cover_image = convert_image_to_datatype_matlab(image_original, "uint8", eng)

    # Read message that will be embedded into image.
    data = message

    # Calling embedding algorithm.
    wcblgEmbedding = WCBLGAlgorithm(cover_image, data, key, Bs, mul, Npop, Pc, Pm, Epoch, eng)
    if not wcblgEmbedding.prepare_algorithm():
        print("embedding went wrong")
    bestSeeds, stego_image = wcblgEmbedding.wcblg()

    return cover_image, stego_image, bestSeeds


def decrypt(image, best_seeds, key, Bs, mul, message, eng):
    # Read stego image.
    stego_image = image

    # Read best seeds.
    bestSeeds = best_seeds

    # Read message and get length in bin.
    data = message
    data_bin = string_to_bin(data)

    # Calling extraction algorithm.
    wcblgExtraction = WCBLGExtraction(stego_image, key, Bs, mul, bestSeeds, len(data_bin), eng)
    wcblgExtraction.prepare_algorithm()
    hidden_message = wcblgExtraction.extract_data()

    return hidden_message


def main():
    # Initializing engine and library for MATLAB
    eng = mylibpkg.initialize()

    # Defining paths for input and output directories.
    original_image_path = "../data/dataset/matches.tif"
    original_message = read_message("../data/message/Lorem Ipsum 1500B.txt")
    cover_image_path = "../test_results/cover_images/analysis_of_different_parameters"
    stego_image_path = "../test_results/stego_images/analysis_of_different_parameters"
    error_image_path = "../test_results/stego_images/analysis_of_different_parameters"

    # Setting parameters.
    block_sizes = [512, 256, 128, 64]
    mul_values = [1, 1.1, 1.2, 1.3]
    key = 12345
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 50

    # Iterating over combinations of block sizes and multipliers.
    for block_size in block_sizes:
        for mul in mul_values:
            # Encrypt and decrypt.
            cover_image, stego_image, best_seeds = encrypt(original_image_path, key, block_size, mul, Npop, Pc, Pm, Epoch, original_message, eng)
            hidden_message = decrypt(stego_image, best_seeds, key, block_size, mul, original_message, eng)

            # Save results if decryption is successful, otherwise log to error directory.
            if hidden_message == original_message:
                # Save the images and PSNR values for successful encryption/decryption.
                name = create_name("cover", block_size, mul)
                save_image(cover_image, cover_image_path + "/test_1/" + name + ".tif")
                name = create_name("stego", block_size, mul)
                save_image(stego_image, stego_image_path + "/test_1/" + name + ".tif")
                save_best_seeds(name, best_seeds, stego_image_path + "/test_1/seeds.txt")
                psnr_value = calculate_psnr_2(cover_image, stego_image)
                save_psnr_values(name, psnr_value, stego_image_path + "/test_1/psnr.txt")
            else:
                # Save the images and seeds for failed cases to the error directory.
                name = create_name("cover", block_size, mul)
                save_image(cover_image, error_image_path + "/test_1/error/" + name + ".tif")
                name = create_name("stego", block_size, mul)
                save_image(stego_image, error_image_path + "/test_1/error/" + name + ".tif")
                save_best_seeds(name, best_seeds, error_image_path + "/test_1/error/seeds.txt")

    eng.terminate()


if __name__ == '__main__':
    main()
