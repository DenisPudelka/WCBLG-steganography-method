import mylibpkg
import tifffile
import numpy as np
from Utils import *
import matplotlib.pyplot as plt

image = tifffile.imread("original_images/peppers_color.tiff")

# if image.dtype != np.uint8:
#     image = image.astype(np.uint8)

eng = mylibpkg.initialize()

image_gray_matlab = color_to_gray_matlab(image, eng)
image_converte_datatype_matlab = convert_image_to_datatype_matlab(image_gray_matlab, "double", eng)
image_gray = np.array(image_converte_datatype_matlab)

LL, LH, HL, HH = DWT_version_2(image_gray, eng)

reconstructed_image = IDWT_version_2(LL, LH, HL, HH, eng)

eng.terminate()
# Display - Original image and Reconstructed
fig, axs = plt.subplots(1, 2, figsize=(10, 5))

axs[0].imshow(image, cmap='gray')
axs[0].set_title('Original Image')
axs[0].axis('off')

axs[1].imshow(reconstructed_image, cmap='gray')
axs[1].set_title('Reconstructed Image')
axs[1].axis('off')

plt.show()