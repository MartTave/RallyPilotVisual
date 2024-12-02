from data_tools.getDistance import getDistancesSingle
from data_tools.noise import add_gaussian_noise
import numpy as np
from rallyrobopilot.convert_to_bw import convertToBwSingle
from rallyrobopilot.normalize_distances import normalize_distances
from rallyrobopilot.remote import Remote
import os
file = np.load("data/record_color0.npz")

import ipdb; ipdb.set_trace()
colors = [
    [255,0 ,0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [0, 255, 255],
    [255, 0, 255],
    [255, 128, 0],
    [255,0 , 128],
    [128, 255, 0],
    [0, 255, 128],
    [128, 0, 255],
    [0, 128, 255],
]

START_TRIM = 10
END_TRIM = 10
lastPicture = None

for c in colors: 
    distances_normalized = []
    controls = []
    images = []
    for p in file["images"]: 

        x = convertToBwSingle(np.array(p, dtype=np.uint8))

        if lastPicture is not None :
            distances = getDistancesSingle(np.array(p), np.array(c))
            distances_normalized.append(normalize_distances(distances))
            newX = np.stack((lastPicture, x), axis=0)
            images.append(newX)
        lastPicture = x
    DATA_FOLDER = "./data/record_color_separated"
    FILENAME = ".npz"
    
    currIndex = 0
    full_path = DATA_FOLDER + str(currIndex) + FILENAME
    while os.path.exists(full_path):
        currIndex += 1
        full_path = DATA_FOLDER + str(currIndex)  + FILENAME
    images_noise = add_gaussian_noise(images)
            
 
    distances_normalized = np.array(distances_normalized)


    np.savez(full_path, images=images_noise, controls=file["controls"], distances=distances_normalized)
