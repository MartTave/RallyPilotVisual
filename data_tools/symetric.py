import os
import numpy as np
import matplotlib.pyplot as plt

BASEPATH = "data/record"
BASE_EXTENSION = ".npz"
files = [0, 1, 2, 3]

for f in files:
    newPath = f"{BASEPATH}_flipped{str(f)}{BASE_EXTENSION}"
    if os.path.exists(newPath):
        continue
    fullPath = BASEPATH + str(f) + BASE_EXTENSION
    data = np.load(fullPath)
    images = data["images"]
    controls = data["controls"]
    speeds = data["speeds"]
    images = np.flip(images, axis=3)
    np.savez(
        newPath,
        images=images,
        controls=controls,
        speeds=speeds,
    )
