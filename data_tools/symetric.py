import os
import numpy as np
import matplotlib.pyplot as plt

BASEPATH = "data/record_norm"
BASE_EXTENSION = ".npz"
files = [4, 5, 6, 7]

for f in files:
    newPath = f"{BASEPATH}{str(f)}_noise_flipped{BASE_EXTENSION}"
    if os.path.exists(newPath):
        print("Found ", newPath, " skipping...")
        continue
    fullPath = BASEPATH + str(f) + "_noise" + BASE_EXTENSION
    data = np.load(fullPath)
    images = data["images"]
    controls = data["controls"]
    speeds = data["speeds"]
    distances = data["distances"]
    images = np.flip(images, axis=3)
    np.savez(
        newPath,
        images=images,
        controls=controls,
        speeds=speeds,
        distances=distances
    )
