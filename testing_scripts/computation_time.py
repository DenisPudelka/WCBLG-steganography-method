from stego.Utils import *
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
import tifffile
import mylibpkg
import cProfile
import pstats
import time


def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()
    return result


def save_computation_time(name, time, path):
    """ Saving the computation time values to a file, for later analysis."""
    with open(path, 'a') as file:
        file.write(f"{name}: {time}\n")


def create_name(variety, block_size, mul):
    """ Generating a formatted name string combining parameters."""
    return variety + "_" + str(block_size) + "_" + str(mul)


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
    # Initializing engine and library for MATLAB.
    eng = mylibpkg.initialize()

    original_image_path = "../data/dataset/peppers.tiff"

    # List of message file names for different test cases.
    messages_array = ['Lorem Ipsum 6826 for mul 1,2.txt', "Lorem Ipsum 13652 for mul 1,2.txt",
                      "Lorem Ipsum 20478 for mul 1,2.txt"]

    block_size = 64
    mul = 1.2
    key = 12345
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 50

    # Looping through each message file
    for message_name in messages_array:
        # Read message data from file
        message_data = read_message("../data/message/" + message_name)

        # Embedding
        start_time_embedding = time.perf_counter()  # Begin timing the embedding process
        cover_image, stego_image, best_seeds = encrypt(original_image_path, key, block_size, mul, Npop, Pc, Pm, Epoch,
                                                       message_data, eng)
        end_time_embedding = time.perf_counter()    # End timing the embedding process
        encrypt_time = end_time_embedding - start_time_embedding    # Calculate duration of embedding

        # Extraction
        start_time_extraction = time.perf_counter() # Begin timing the extraction process
        hidden_message = decrypt(stego_image, best_seeds, key, block_size, mul, message_data, eng)
        end_time_extraction = time.perf_counter()   # End timing the extraction process
        extraction_time = end_time_extraction - start_time_extraction   # Calculate duration of extraction

        # Check if the extraction was successful
        if hidden_message == message_data:
            name = create_name("embedding_time", block_size, message_name)
            save_computation_time(name, encrypt_time,
                                  "../test_results/stego_images/computation_time/computation_time.txt")
            name = create_name("extraction_time", block_size, message_name)
            save_computation_time(name, extraction_time,
                                  "../test_results/stego_images/computation_time/computation_time.txt")
            with open("../test_results/stego_images/computation_time/computation_time.txt", 'a') as file:
                file.write('\n')

    eng.terminate()

if __name__ == '__main__':
    main()
