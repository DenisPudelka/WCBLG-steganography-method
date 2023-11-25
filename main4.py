import mylibpkg
import tifffile
import matplotlib.pyplot as plt
import numpy as np

image = tifffile.imread("original_images/baboon_color.tiff")

eng = mylibpkg.initialize()
image_gray_matlab = eng.convert_rgb_to_gray(image)
image_gray = np.array(image_gray_matlab)
output = eng.perform_iwt(image_gray,'haar',1)

eng.terminate()

print("Output type: " + str(type(output)))
print("Output len: " + str(len(output)))
print("Output[1] type: " + str(type(output[1])))
print("Output[1] len: " + str(len(output[1])))
print(np.array(output[1]))

