import mylibpkg
import tifffile
import numpy as np
import Utils
import matplotlib.pyplot as plt

image = tifffile.imread("original_images/tank_color.tiff")

if image.dtype != np.uint8:
    image = image.astype(np.uint8)

eng = mylibpkg.initialize()
image_gray_matlab = eng.convert_rgb_to_gray(image)
image_gray = np.array(image_gray_matlab)
eng.terminate()

LL, LH, HL, HH = Utils.IWT_version_2(image_gray)

# Display - Plot each component
fig, axs = plt.subplots(2, 2, figsize=(10, 10))

axs[0, 0].imshow(LL, cmap='gray')
axs[0, 0].set_title('LL - Approximation')

axs[0, 1].imshow(LH, cmap='gray')
axs[0, 1].set_title('LH - Horizontal Detail')

axs[1, 0].imshow(HL, cmap='gray')
axs[1, 0].set_title('HL - Vertical Detail')

axs[1, 1].imshow(HH, cmap='gray')
axs[1, 1].set_title('HH - Diagonal Detail')

for ax in axs.flat:
    ax.label_outer()

plt.show()