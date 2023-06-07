import os
import matplotlib.pyplot as plt
import cv2
import numpy as np
from scipy import ndimage

pyramid_min_size = 32
EXTENSIONS = set(["bmp", "jpeg", "jpg", "png", "tif", "tiff"])
src_dir = "images/input/flower"

def align(images, iterations = 5000, epsilon = 1e-10):
    def _get_homography(image_1, image_2):
        warp_matrix = np.eye(3, 3, dtype=np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iterations,  epsilon)
        _, homography = cv2.findTransformECC(image_1, image_2, warp_matrix, cv2.MOTION_HOMOGRAPHY, criteria)
        return homography
    
    def _warp(image, shape, homography):
        return cv2.warpPerspective(image, homography, shape, flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    
    def _convert_to_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    gray_images = np.zeros(images.shape[:-1], dtype=np.uint8)
    gray_image_shape = gray_images[0].shape[::-1]
    
    aligned_images = np.zeros(images.shape, dtype=images.dtype)
    
    aligned_images[0] = images[0]
    gray_images[0] = _convert_to_grayscale(images[0])
    for index in range(1, images.shape[0]):
        image2_gray = _convert_to_grayscale(images[index])
        homography = _get_homography(gray_images[0], image2_gray)
        
        gray_images[index] = _warp(image2_gray, gray_image_shape, homography)
        aligned_images[index] = _warp(images[index], gray_image_shape, homography)

    return aligned_images, gray_images

def generating_kernel(a):
    kernel = np.array([0.25 - a / 2.0, 0.25, a, 0.25, 0.25 - a / 2.0])
    return np.outer(kernel, kernel)

def convolve(image, kernel=generating_kernel(0.4)):
    return ndimage.convolve(image.astype(np.float64), kernel, mode='mirror')

def reduce_layer(layer, kernel=generating_kernel(0.4)):
    if len(layer.shape) == 2:
        convolution = convolve(layer, kernel)
        return convolution[::2,::2]

    ch_layer = reduce_layer(layer[:,:,0])
    next_layer = np.zeros(list(ch_layer.shape) + [layer.shape[2]], dtype = ch_layer.dtype)
    next_layer[:, :, 0] = ch_layer

    for channel in range(1, layer.shape[2]):
        next_layer[:, :, channel] = reduce_layer(layer[:,:,channel])

    return next_layer

def gaussian_pyramid(images, levels):
    pyramid = [images.astype(np.float64)]
    num_images = images.shape[0]

    while levels > 0:
        next_layer = reduce_layer(pyramid[-1][0])
        next_layer_size = [num_images] + list(next_layer.shape)
        pyramid.append(np.zeros(next_layer_size, dtype=next_layer.dtype))
        pyramid[-1][0] = next_layer
        for layer in range(1, images.shape[0]):
            pyramid[-1][layer] = reduce_layer(pyramid[-2][layer])
        levels = levels - 1

    return pyramid

def expand_layer(layer, kernel=generating_kernel(0.4)):
    if len(layer.shape) == 2:
        expand = np.zeros((2 * layer.shape[0], 2 * layer.shape[1]), dtype=np.float64)
        expand[::2, ::2] = layer
        convolution = convolve(expand, kernel)
        return 4.*convolution

    ch_layer = expand_layer(layer[:,:,0])
    next_layer = np.zeros(list(ch_layer.shape) + [layer.shape[2]], dtype = ch_layer.dtype)
    next_layer[:, :, 0] = ch_layer

    for channel in range(1, layer.shape[2]):
        next_layer[:, :, channel] = expand_layer(layer[:,:,channel])

    return next_layer

def laplacian_pyramid(images, levels):
    gaussian = gaussian_pyramid(images, levels)

    pyramid = [gaussian[-1]]
    for level in range(len(gaussian) - 1, 0, -1):
        gauss = gaussian[level - 1]
        pyramid.append(np.zeros(gauss.shape, dtype=gauss.dtype))
        for layer in range(images.shape[0]):
            gauss_layer = gauss[layer]
            expanded = expand_layer(gaussian[level][layer])
            if expanded.shape != gauss_layer.shape:
                expanded = expanded[:gauss_layer.shape[0],:gauss_layer.shape[1]]
            pyramid[-1][layer] = gauss_layer - expanded

    return pyramid[::-1]

def get_probabilities(gray_image):
    levels, counts = np.unique(gray_image.astype(np.uint8), return_counts = True)
    probabilities = np.zeros((256,), dtype=np.float64)
    probabilities[levels] = counts.astype(np.float64) / counts.sum()
    return probabilities

def entropy(image, kernel_size):
    def _area_entropy(area, probabilities):
        levels = area.flatten()
        return -1. * (levels * np.log(probabilities[levels])).sum()
    
    probabilities = get_probabilities(image)
    pad_amount = int((kernel_size - 1) / 2)
    padded_image = cv2.copyMakeBorder(image,pad_amount,pad_amount,pad_amount,pad_amount,cv2.BORDER_REFLECT101)
    entropies = np.zeros(image.shape[:2], dtype=np.float64)
    offset = np.arange(-pad_amount, pad_amount + 1)
    for row in range(entropies.shape[0]):
        for column in range(entropies.shape[1]):
            area = padded_image[row + pad_amount + offset[:, np.newaxis], column + pad_amount + offset]
            entropies[row, column] = _area_entropy(area, probabilities)

    return entropies

def deviation(image, kernel_size):
    def _area_deviation(area):
        average = np.average(area).astype(np.float64)
        return np.square(area - average).sum() / area.size

    pad_amount = int((kernel_size - 1) / 2)
    padded_image = cv2.copyMakeBorder(image,pad_amount,pad_amount,pad_amount,pad_amount,cv2.BORDER_REFLECT101)
    deviations = np.zeros(image.shape[:2], dtype=np.float64)
    offset = np.arange(-pad_amount, pad_amount + 1)
    for row in range(deviations.shape[0]):
        for column in range(deviations.shape[1]):
            area = padded_image[row + pad_amount + offset[:, np.newaxis], column + pad_amount + offset]
            deviations[row, column] = _area_deviation(area)

    return deviations

def get_fused_base(images, kernel_size):
    layers = images.shape[0]
    entropies = np.zeros(images.shape[:3], dtype=np.float64)
    deviations = np.copy(entropies)
    for layer in range(layers):
        gray_image = cv2.cvtColor(images[layer].astype(np.float32), cv2.COLOR_BGR2GRAY).astype(np.uint8)
        probabilities = get_probabilities(gray_image)
        entropies[layer] = entropy(gray_image, kernel_size)
        deviations[layer] = deviation(gray_image, kernel_size)

    best_e = np.argmax(entropies, axis = 0)
    best_d = np.argmax(deviations, axis = 0)
    fused = np.zeros(images.shape[1:], dtype=np.float64)
    
    for layer in range(layers):
        fused += np.where(best_e[:,:,np.newaxis] == layer, images[layer], 0)
        fused += np.where(best_d[:,:,np.newaxis] == layer, images[layer], 0)

    return (fused / 2).astype(images.dtype)

def get_fused_laplacian(laplacians):
    layers = laplacians.shape[0]
    region_energies = np.zeros(laplacians.shape[:3], dtype=np.float64)

    for layer in range(layers):
        gray_lap = cv2.cvtColor(laplacians[layer].astype(np.float32), cv2.COLOR_BGR2GRAY)
        region_energies[layer] = convolve(np.square(gray_lap))

    best_re = np.argmax(region_energies, axis = 0)
    fused = np.zeros(laplacians.shape[1:], dtype=laplacians.dtype)

    for layer in range(layers):
        fused += np.where(best_re[:,:,np.newaxis] == layer, laplacians[layer], 0)
    
    return fused

def fuse_pyramids(pyramids, kernel_size):
    fused = [get_fused_base(pyramids[-1], kernel_size)]
    for layer in range(len(pyramids) - 2, -1, -1):
        fused.append(get_fused_laplacian(pyramids[layer]))

    return fused[::-1]

def collapse(pyramid):
    image = pyramid[-1]
    for layer in pyramid[-2::-1]:
        expanded = expand_layer(image)
        if expanded.shape != layer.shape:
            expanded = expanded[:layer.shape[0],:layer.shape[1]]
        image = expanded + layer

    return image

def get_pyramid_fusion(images, min_size = 32):
    smallest_side = min(images[0].shape[:2])
    depth = int(np.log2(smallest_side / min_size))
    kernel_size = 5

    pyramids = laplacian_pyramid(images, depth)
    fusion = fuse_pyramids(pyramids, kernel_size)

    return collapse(fusion)

src_contents = os.walk(src_dir)
dirpath, _, fnames = next(src_contents)

image_dir = os.path.split(dirpath)[-1]

image_files = sorted([os.path.join(dirpath, name) for name in fnames])
image_files = [cv2.imread(name) for name in image_files
          if os.path.splitext(name)[-1][1:].lower() in EXTENSIONS]
   
images = np.array(image_files, dtype=image_files[0].dtype)
aligned_images, gray_images = align(images)

_stacked = get_pyramid_fusion(aligned_images, pyramid_min_size)
stacked_image = cv2.convertScaleAbs(_stacked)
plt.figure(figsize=(16,11))
plt.imshow(cv2.cvtColor(stacked_image, cv2.COLOR_BGR2RGB))
plt.show()
