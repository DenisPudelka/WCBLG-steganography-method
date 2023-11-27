from Utils import *
from WCBLGAlgorithm import WCBLGAlgorithm
from WCBLGExtraction import WCBLGExtraction
import tifffile


def encrypt(image_path, key, Bs, mul, Npop, Pc, Pm, Epoch):
    # read image
    image_original = tifffile.imread(image_path)

    # convert image to grayscale
    cover_image = color_to_gray_matlab(image_original)

    # read message
    data = read_message("message/Lorem Ipsum 100B.txt")

    # calling embedding algorithm
    wcblgEmbedding = WCBLGAlgorithm(cover_image, data, key, Bs, mul, Npop, Pc, Pm, Epoch)
    bestSeeds, stego_image, tags = wcblgEmbedding.wcblg()
    print(bestSeeds)

    # save seeds, cover image and stego image
    write_seeds_to_file(bestSeeds, "seeds_1.txt")
    save_image(cover_image, "cover_image/cover_image_1.tif")
    save_image(stego_image, "stego_image/stego_image_1.tif")


def decrypt(key, Bs, mul):
    # read image
    stego_image = tifffile.imread("stego_image/stego_image_1.tif")

    # read best seeds
    bestSeeds = read_seeds_from_file("seeds_1.txt")

    # read message and get length in bin
    data = read_message("message/Lorem Ipsum 100B.txt")
    data_bin = string_to_bin(data)

    # calling extraction algorithm
    wcblgExtraction = WCBLGExtraction(stego_image, key, Bs, mul, bestSeeds, len(data_bin))
    hidden_message = wcblgExtraction.extract_data()

    print(hidden_message)


if __name__ == '__main__':
    image_path = "original_images/peppers_color.tiff"

    key = 12345
    Bs = 256
    mul = 1.2
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 20

    encrypt(image_path, key, Bs, mul, Npop, Pc, Pm, Epoch)

    decrypt(key, Bs, mul)
