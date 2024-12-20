import os
import numpy as np
import matplotlib.pyplot as plt

BASEPATH = ["data/train", "data/test"]
BASE_EXTENSION = ".npz"

for b in BASEPATH:
    for f in os.listdir(b):
        path = f"{b}/{f}"
        if not os.path.isfile(path):
            continue
        data = np.load(path)
        images = data["images"]
        controls = data["controls"]
        distances = data["distances"]
        images = np.flip(images, axis=3)
        controls[:, [2, 3]] = controls[:, [3, 2]]
        distances = np.flip(distances, axis=2)
        np.savez(
            f"{b}/{f.split('.')[0]}_flipped.npz",
            images=images,
            controls=controls,
            distances=distances,
        )
