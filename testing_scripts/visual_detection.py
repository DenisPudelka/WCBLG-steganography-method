from stego.Utils import *
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
import tifffile
import mylibpkg


def create_name(variety, bpp):
    """ Generating a formatted name string combining parameters."""
    return variety + "_" + str(bpp)


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
    # Initialize the MATLAB engine
    eng = mylibpkg.initialize()

    original_image_path = "../data/dataset/lena.tif"
    stego_image_path = "../test_results/stego_images/visual_detection"

    # List of message filenames for embedding within the image
    messages_array = ['Lorem Ipsum 6826 for mul 1,2.txt', "Lorem Ipsum 13652 for mul 1,2.txt",
                      "Lorem Ipsum 20478 for mul 1,2.txt"]

    # Set parameters
    block_size = 64
    mul = 1.2
    key = 12345
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 50

    # Process each message,
    for message_name in messages_array:
        message_data = read_message("../data/message/" + message_name)

        cover_image, stego_image, best_seeds = encrypt(original_image_path, key, block_size, mul, Npop, Pc, Pm, Epoch,
                                                       message_data, eng)
        hidden_message = decrypt(stego_image, best_seeds, key, block_size, mul, message_data, eng)

        # Save the original and stego images if the message was correctly decrypted
        if hidden_message == message_data:
            name = create_name("cover", message_name)
            save_image(cover_image, stego_image_path + "/test_5/" + name + ".tif")
            name = create_name("stego", message_name)
            save_image(stego_image, stego_image_path + "/test_5/" + name + ".tif")

    eng.terminate()

if __name__ == '__main__':
    main()
