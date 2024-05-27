from stego.Utils import *
import matplotlib.pylab as plt
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
import tifffile
import numpy as np
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
    # Initialize the engine for processing
    eng = mylibpkg.initialize()

    original_image_path = "../data/dataset/matches.tif"
    stego_image_path = "../test_results/stego_images/security"

    # List of message file names for testing
    messages_array = ['Lorem Ipsum 2500B.txt', "Lorem Ipsum 5000B.txt", "Lorem Ipsum 6500B.txt"]

    # Set parameters
    block_size = 64
    mul = 1.2
    key = 12345
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 50

    # Process each message in the array
    for message_name in messages_array:
        i = 1
        message_data = read_message("../data/message/" + message_name)

        cover_image, stego_image, best_seeds = encrypt(original_image_path, key, block_size, mul, Npop, Pc, Pm, Epoch,
                                                       message_data, eng)
        hidden_message = decrypt(stego_image, best_seeds, key, block_size, mul, message_data, eng)

        # Verify if the decryption was successful
        if hidden_message == message_data:
            name = create_name("cover", message_name)
            save_image(cover_image, stego_image_path + "/test_5/" + name + ".tif")
            cover_image_array = np.array(cover_image)
            cover_hist, cover_bins = np.histogram(cover_image_array, bins=256, range=[0, 255])

            name = create_name("stego", message_name)
            save_image(stego_image, stego_image_path + "/test_5/" + name + ".tif")
            stego_image_array = np.array(stego_image)
            stego_hist, stego_bins = np.histogram(stego_image_array, bins=256, range=[0, 255])

            plt.figure(figsize=(20, 5))

            # Plot for cover image
            plt.subplot(1, 4, 1)
            plt.imshow(cover_image, cmap='gray')
            plt.title('Cover Image')
            plt.axis('off')

            # Plot for cover image histogram
            plt.subplot(1, 4, 2)
            plt.plot(cover_bins[:-1], cover_hist, label='Cover Image')
            plt.title('Cover Image Histogram')
            plt.xlabel('Pixel Intensity')
            plt.ylabel('Frequency')

            # Plot for stego image histogram
            plt.subplot(1, 4, 3)
            plt.plot(stego_bins[:-1], stego_hist, label='Stego Image')
            plt.title('Stego Image Histogram')
            plt.xlabel('Pixel Intensity')
            plt.ylabel('Frequency')

            # Plot the difference between the histograms
            plt.subplot(1, 4, 4)
            plt.plot(cover_bins[:-1], stego_hist - cover_hist, label='Difference')
            plt.title('Histogram Difference')
            plt.xlabel('Pixel Intensity')
            plt.ylabel('Frequency Difference')
            plt.tight_layout()

            plot_save_path = stego_image_path + "/test_5/" + str(i) + "_histograms.png"
            i += 1
            plt.savefig(plot_save_path)  # Save the plot to file
            plt.show()

    eng.terminate()

if __name__ == '__main__':
    main()