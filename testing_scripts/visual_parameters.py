from stego.Utils import *
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
import tifffile
import mylibpkg
import math
import cv2
import sewar


def save_values(name, value, path):
    """ Save the values to a specified file."""
    with open(path, 'a') as file:
        file.write(f"{name}: {value}\n")


def create_name(image_name, message_length):
    """ Generating a formatted name string combining parameters."""
    return image_name + "_" + message_length


def calculate_psnr(cover, stego):
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
    # Initialize the engine for MATLAB
    eng = mylibpkg.initialize()

    original_image_path = "../data/dataset/matches.tif"
    stego_image_path = "../test_results/stego_images/visual_parameters"

    # List of message files to be embedded in increasing size.
    messages_array = ['Lorem Ipsum 1000B.txt', "Lorem Ipsum 2000B.txt", "Lorem Ipsum 3000B.txt", "Lorem Ipsum 4000B.txt",
                      "Lorem Ipsum 5000B.txt", "Lorem Ipsum 6000B.txt", "Lorem Ipsum 7000B.txt", "Lorem Ipsum 8000B.txt",
                      "Lorem Ipsum 9000B.txt", "Lorem Ipsum 10000B.txt", "Lorem Ipsum 11000B.txt", "Lorem Ipsum 12000B.txt",
                      "Lorem Ipsum 13000B.txt", "Lorem Ipsum 14000B.txt", "Lorem Ipsum 15000B.txt", "Lorem Ipsum 16000B.txt",
                      "Lorem Ipsum 17000B.txt", "Lorem Ipsum 18000B.txt", "Lorem Ipsum 19000B.txt", "Lorem Ipsum 20000B.txt"]

    # Set parameters
    block_size = 64
    mul = 1.2
    key = 12345
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 50

    # Process each message
    for message in messages_array:
        original_message = read_message("../data/message/" + message)
        cover_image, stego_image, best_seeds = encrypt(original_image_path, key, block_size, mul, Npop, Pc, Pm, Epoch,
                                                       original_message, eng)
        hidden_message = decrypt(stego_image, best_seeds, key, block_size, mul, original_message, eng)

        # Verify successful encryption/decryption before proceeding.
        if hidden_message == original_message:
            name = create_name("matches", message)
            # Calculate and save PSNR value.
            psnr_value = calculate_psnr(cover_image, stego_image)
            save_values(name, psnr_value, stego_image_path + "/test_5/psnr.txt")
            # Calculate and save MSE value.
            mse_value = sewar.full_ref.mse(cover_image, stego_image)
            save_values(name, mse_value, stego_image_path + "/test_5/mse.txt")
            # Calculate and save SSIM value.
            ssim_value, _ = sewar.full_ref.ssim(cover_image, stego_image, ws=11, K1=0.01, K2=0.03, MAX=255)
            save_values(name, ssim_value, stego_image_path + "/test_5/ssim.txt")

    eng.terminate()


if __name__ == '__main__':
    main()
