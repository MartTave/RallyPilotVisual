import numpy as np
import cv2
import os 

def add_gaussian_noise(images, noise_scale=0.1, blur_size=(5,5), blur_sigma=1.0):
    images = np.array(images).astype(np.float32)
    if images.max() > 1.0:
        images /= 255.0
    
    processed_images = np.empty_like(images)
    
    noise = np.random.normal(0, noise_scale, images.shape)
    
    for i in range(len(images)):
        noisy_image = np.clip(images[i] + noise[i], 0, 1)
        
        blurred_image = cv2.GaussianBlur(noisy_image, blur_size, blur_sigma)
        
        processed_images[i] = blurred_image
    
    return processed_images

BASEPATH = "data/record_norm"
BASE_EXTENSION = ".npz"
files = [4,5,6,7]

for f in files:
    newPath = f"{BASEPATH}{str(f)}_noise{BASE_EXTENSION}"
    if os.path.exists(newPath):
        print("Found ", newPath, " skipping...")
        continue
    fullPath = BASEPATH + str(f) + BASE_EXTENSION
    data = np.load(fullPath)
    images = data["images"]
    controls = data["controls"]
    speeds = data["speeds"]
    distances = data["distances"]
    images_noise = add_gaussian_noise(images)
    np.savez(
        newPath,
        images=images_noise,
        controls=controls,
        speeds=speeds,
        distances=distances
    )
