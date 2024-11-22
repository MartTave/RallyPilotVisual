import matplotlib.pyplot as plt
import numpy as np

file = np.load("./data/record0.npz")

array = file["images"][0][0]


plt.imshow(array, cmap="gray")
plt.axis("off")  # Remove axes
plt.savefig("data/grayscale_image.png", bbox_inches="tight", pad_inches=0, dpi=300)
