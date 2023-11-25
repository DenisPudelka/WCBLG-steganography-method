import mylibpkg
import tifffile
import numpy as np
import Utils
import matplotlib.pyplot as plt

image = tifffile.imread("original_images/baboon_color.tiff")

if image.dtype != np.uint8:
    image = image.astype(np.uint8)

eng = mylibpkg.initialize()
image_gray_matlab = eng.convert_rgb_to_gray(image)
image_gray = np.array(image_gray_matlab)
eng.terminate()

LL, LH, HL, HH = Utils.DWT_version_2(image_gray)

reconstructed_image = Utils.IDWT_version_2(LL, LH, HL, HH)

# Display - Original image and Reconstructed
fig, axs = plt.subplots(1, 2, figsize=(10, 5))

axs[0].imshow(image, cmap='gray')
axs[0].set_title('Original Image')
axs[0].axis('off')

axs[1].imshow(reconstructed_image, cmap='gray')
axs[1].set_title('Reconstructed Image')
axs[1].axis('off')

plt.show()