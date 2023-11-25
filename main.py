from Utils import *
from WCBLGAlgorithm import WCBLGAlgorithm
from WCBLGExtraction import WCBLGExtraction
import tifffile
import cv2

def write_seeds_to_file(seeds):
    with open('seeds.txt', 'w') as file:
        file.write('\n'.join(str(seed) for seed in seeds))

def read_seeds_from_file():
    file1 = open('seeds.txt', 'r')
    Lines = file1.readlines()

    seeds = []
    for line in Lines:
        if line is None:
            break
        seeds.append(int(line.strip()))
    return seeds


if __name__ == '__main__':
    image_path = "128x128PNG.png"


    #data = "Nullam aliquet pellentesque ligula ut consectetur. Sed ac ante lacinia, vestibulum tortor in, vulputate nulla. Nunc viverra tempor orci a scelerisque. Pellentesque id tortor commodo, dignissim massa vitae, elementum tellus. Integer lectus sapien, tincidunt sit amet risus sed, vulputate gravida ex. Donec finibus, nibh in iaculis malesuada, est arcu gravida libero, sit amet luctus magna augue in tortor. Nunc ornare ut ipsum nec malesuada. Sed eget suscipit sapien. Mauris suscipit quam a ligula vulputate vestibulum. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce lobortis eros eu libero accumsan scelerisque. Nullam pharetra, mauris quis dignissim mollis, turpis nisi aliquet mi, a faucibus dolor enim vel lacus. Nullam aliquet pellentesque ligula ut consectetur. Sed ac ante lacinia, vestibulum tortor in, vulputate nulla."
    data = ""
    for i in range(0, 10):
        data += "Denis Pudelka123"
    key = 12345
    Bs = 16
    mul = 1.2
    Npop = 20
    Pc = 0.7
    Pm = 0.2
    Epoch = 20

    #cover_image = tifffile.imread(image_path)
    cover_image = cv2.imread(image_path, 0)

    wcblgEmbedding = WCBLGAlgorithm(image_path, data, key, Bs, mul, Npop, Pc, Pm, Epoch)
    bestSeeds, stego_image, tags = wcblgEmbedding.wcblg()
    write_seeds_to_file(bestSeeds)
    print(bestSeeds)
    #tifffile.imwrite("stego.tif", stego_image, **tags)
    cv2.imwrite("cover.png", cover_image)
    cv2.imwrite("stego.png", stego_image)
    stego_image = cv2.imread("stego.png", 0)
    #bestSeeds = read_seeds_from_file()

    data_bin = string_to_bin(data)
    wcblgExtraction = WCBLGExtraction(stego_image, key, Bs, mul, bestSeeds, len(data_bin))
    print(wcblgExtraction.extract_data())
