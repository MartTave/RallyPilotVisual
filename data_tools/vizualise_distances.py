import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

file = np.load("data/train/record_GA_Visual1.npz")

distances = file["distances"]

for d in distances:
    plt.figure()
    plt.imshow(d, vmin=0, vmax=1)
    plt.colorbar()
    plt.title("Distances heatmap")
    plt.xticks([])
    plt.yticks([])
    plt.savefig("./data/trash/distance_heatmap.png")
    input()
