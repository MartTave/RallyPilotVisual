import matplotlib.pyplot as plt
import numpy as np

file = np.load("./data/train/record0.npz")

for pic in file["images"]:
    plt.imshow(pic[0], cmap="gray")
    plt.axis("off")  # Remove axes
    plt.savefig("data/trash/bw_n-1.png", bbox_inches="tight", pad_inches=0, dpi=50)
    plt.imshow(pic[1], cmap="gray")
    plt.axis("off")  # Remove axes
    plt.savefig("data/trash/bw_n.png", bbox_inches="tight", pad_inches=0, dpi=50)
    input()
