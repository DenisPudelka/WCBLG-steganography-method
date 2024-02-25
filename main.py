from stego.Utils import *
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
import tifffile
import mylibpkg


def prepare_image(image):
    row, col = image.shape
    for x in range(row):
        for y in range(col):
            if image[x, y] == 0:
                image[x, y] += 1
    return image


def encrypt(image_path, key, Bs, mul, Npop, Pc, Pm, Epoch, eng):
    # read image
    image_original = tifffile.imread(image_path)

    # convert image to grayscale
    size = len(image_original.shape)
    if size == 3:
        image_original = color_to_gray_matlab(image_original, eng)

    # prepare image
    image_original = prepare_image(image_original)

    # convert image to different datatype
    cover_image = convert_image_to_datatype_matlab(image_original, "uint16", eng)

    # read message
    data = read_message("message/Lorem Ipsum 15000B.txt")

    # calling embedding algorithm
    wcblgEmbedding = WCBLGAlgorithm(cover_image, data, key, Bs, mul, Npop, Pc, Pm, Epoch, eng, use_iwt)
    if not wcblgEmbedding.prepare_algorithm():
        print("embedding went wrong")
    bestSeeds, stego_image = wcblgEmbedding.wcblg()
    print(bestSeeds)

    # save seeds, cover image and stego image
    write_seeds_to_file(bestSeeds, "seeds_1.txt")
    save_image(cover_image, "cover_image/cover_image_1.tif")
    save_image(stego_image, "stego_image/stego_image_1.tif")


def decrypt(key, Bs, mul, eng):
    # read image
    stego_image = tifffile.imread("stego_image/stego_image_1.tif")

    # read best seeds
    bestSeeds = read_seeds_from_file("seeds_keys/seeds_1.txt")

    # read message and get length in bin
    data = read_message("message/Lorem Ipsum 15000B.txt")
    data_bin = string_to_bin(data)

    # calling extraction algorithm
    wcblgExtraction = WCBLGExtraction(stego_image, key, Bs, mul, bestSeeds, len(data_bin), eng, use_iwt)
    wcblgExtraction.prepare_algorithm()
    hidden_message = wcblgExtraction.extract_data()

    print(hidden_message)


def main():
    eng = mylibpkg.initialize()
    image_path = "original_images/baboon_color.tiff"

    key = 12345
    Bs = 256
    mul = 1.2
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 50

    encrypt(image_path, key, Bs, mul, Npop, Pc, Pm, Epoch, eng)
    decrypt(key, Bs, mul, eng)

    eng.terminate()


if __name__ == '__main__':
    main()
