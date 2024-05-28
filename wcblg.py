from stego.Utils import *
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
import tifffile
import mylibpkg


def prepare_image(image):
    """ Ensureshs that image stays in 8-bit depth after embedding. """
    row, col = image.shape
    for x in range(row):
        for y in range(col):
            if image[x, y] == 0:
                image[x, y] += 1
            elif image[x, y] == 255:
                image[x, y] -= 1
    return image


def encrypt(image_path, key, Bs, mul, Npop, Pc, Pm, Epoch, eng):
    # read image
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
    data = read_message("data/message/Lorem Ipsum 1500B.txt") # editable

    # Calling embedding algorithm.
    wcblgEmbedding = WCBLGAlgorithm(cover_image, data, key, Bs, mul, Npop, Pc, Pm, Epoch, eng)
    if not wcblgEmbedding.prepare_algorithm():
        print("embedding went wrong")
    bestSeeds, stego_image = wcblgEmbedding.wcblg()
    print(bestSeeds)

    # Save best_seeds, cover image and stego image
    write_seeds_to_file(bestSeeds, "best_seeds_jet.txt")   # editable
    save_image(cover_image, "cover_image/cover_image_jet.tif")    # editable
    save_image(stego_image, "stego_image/stego_image_jet.tif")    # editable


def decrypt(key, Bs, mul, eng):
    # Read stego image.
    stego_image = tifffile.imread("stego_image/stego_image_jet.tif")  # editable

    # Read best seeds.
    bestSeeds = read_seeds_from_file("seeds_keys/best_seeds_jet.txt")  # editable

    # Read message and get length in bin.
    data = read_message("data/message/Lorem Ipsum 1500B.txt")   # editable (needs to be same as in embedding)
    data_bin = string_to_bin(data)

    # Calling extraction algorithm.
    wcblgExtraction = WCBLGExtraction(stego_image, key, Bs, mul, bestSeeds, len(data_bin), eng)
    wcblgExtraction.prepare_algorithm()
    hidden_message = wcblgExtraction.extract_data()

    print(hidden_message)


def main():
    # Initializing engine and library for MATLAB
    eng = mylibpkg.initialize()

    # Original image path that will be used for embedding
    image_path = "data/dataset/jet.tiff"

    # WCBLG parameters
    key = 12345
    Bs = 64
    mul = 1.2
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 50

    # Embedding proces
    encrypt(image_path, key, Bs, mul, Npop, Pc, Pm, Epoch, eng)
    # Extraction process
    decrypt(key, Bs, mul, eng)

    # Terminating engine when done
    eng.terminate()


if __name__ == '__main__':
    main()
