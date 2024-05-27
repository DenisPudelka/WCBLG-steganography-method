import matplotlib.pyplot as plt
import re  # Importing the regex library
import os

# Function to read data from file
def read_data(filename):
    sizes = []
    values = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split(': ')
            size_match = re.search(r'(\d+)B.txt', parts[0])
            if size_match:
                size = int(size_match.group(1))
                value = float(parts[1])
                sizes.append(size)
                values.append(value)
            else:
                print("No match for size in:", parts[0])
    return sizes, values

# Function to read data from all test folders
def read_all_tests(metric):
    all_sizes = []
    all_values = []
    for i in range(1, 5):
        folder = f'test_{i}'
        filename = os.path.join(folder, f'{metric}.txt')
        sizes, values = read_data(filename)
        all_sizes.append(sizes)
        all_values.append(values)
    return all_sizes, all_values

# Reading data for all tests
psnr_sizes, psnr_values = read_all_tests('psnr')
ssim_sizes, ssim_values = read_all_tests('ssim')
mse_sizes, mse_values = read_all_tests('mse')

# Defining colors and line styles for each test
colors = ['blue', 'green', 'red', 'purple']
line_styles = ['-', '--', '-.', ':']
labels = ['Jet', 'Peppers', 'Baboon', 'Lena']

# Creating plots
plt.figure(figsize=(8, 15))

# Plot PSNR
plt.subplot(3, 1, 1)
for i in range(4):
    plt.plot(psnr_sizes[i], psnr_values[i], marker='o', linestyle=line_styles[i], color=colors[i], label=labels[i])
plt.title('PSNR')
plt.xlabel('Size (bytes)')
plt.ylabel('PSNR (dB)')
plt.legend()

# Plot SSIM
plt.subplot(3, 1, 2)
for i in range(4):
    plt.plot(ssim_sizes[i], ssim_values[i], marker='o', linestyle=line_styles[i], color=colors[i], label=labels[i])
plt.title('SSIM')
plt.xlabel('Size (bytes)')
plt.ylabel('SSIM')
plt.legend()

# Plot MSE
plt.subplot(3, 1, 3)
for i in range(4):
    plt.plot(mse_sizes[i], mse_values[i], marker='o', linestyle=line_styles[i], color=colors[i], label=labels[i])
plt.title('MSE')
plt.xlabel('Size (bytes)')
plt.ylabel('MSE')
plt.legend()

# Display the plots
plt.tight_layout()
plt.show()
