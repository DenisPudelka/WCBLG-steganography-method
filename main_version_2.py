from stego.Utils import *
from stego.WCBLGAlgorithm_version_2 import WCBLGAlgorithm
from stego.WCBLGExtraction_version_2 import WCBLGExtraction
from ui.gui import GUI
import tifffile
import mylibpkg

def encrypt(image_path, key, Bs, mul, Npop, Pc, Pm, Epoch, eng, use_iwt):
    # read image
    image_original = tifffile.imread(image_path)

    # convert image to grayscale
    cover_image = color_to_gray_matlab(image_original, eng)

    # convert image to different datatype
    # cover_image = convert_image_to_datatype_matlab(cover_image, "int8", eng)

    # read message
    data = read_message("message/Lorem Ipsum 1000B.txt")

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


def decrypt(key, Bs, mul, eng, use_iwt):
    # read image
    stego_image = tifffile.imread("stego_image/stego_image_1.tif")

    # read best seeds
    bestSeeds = read_seeds_from_file("seeds_1.txt")

    # read message and get length in bin
    data = read_message("message/Lorem Ipsum 1000B.txt")
    data_bin = string_to_bin(data)

    # calling extraction algorithm
    wcblgExtraction = WCBLGExtraction(stego_image, key, Bs, mul, bestSeeds, len(data_bin), eng, use_iwt)
    wcblgExtraction.prepare_algorithm()
    hidden_message = wcblgExtraction.extract_data()

    print(hidden_message)


def main():
    eng = mylibpkg.initialize()
    app = GUI(eng)
    app.mainloop()
    eng.terminate()


if __name__ == '__main__':
    main()