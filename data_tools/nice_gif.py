import io
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

file = np.load("data/train/record0.npz")

distances = file["distances"]
images = file["images"]
START = 2
DURATION = 30


colors = ["black", "gray", "white"]
n_bins = 512  # Increase for more precision
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors, N=n_bins)


def createDistanceHeatmap(distances, images):
    plt.figure()
    plt.tight_layout()

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12), sharex=True)
    bw_axes = [ax1, ax2]

    for i in range(0, 2):
        im = bw_axes[i].imshow(images[i], cmap="gray")
        bw_axes[i].set_title("Picture t - 1" if i == 0 else "Picture t")
        bw_axes[i].set_xticks([])
        bw_axes[i].set_yticks([])

    im = ax3.imshow(distances, vmin=0, vmax=1)
    fig.colorbar(im, ax=ax3, pad=-0.05)
    ax3.set_title("Distances heatmap")
    ax3.set_xticks([])
    ax3.set_yticks([])
    xSize = ax3._position.x1 - ax3._position.x0
    ySize = ax3._position.y1 - ax3._position.y0
    ax3.set_position([-0.015, 0.11, xSize, ySize])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf)


def createBWVisualiation(d):
    images = []
    for i in range(0, 2):
        plt.figure()
        plt.imshow(d[i, :, :], cmap="gray")
        plt.xticks([])
        plt.yticks([])
        buf1 = io.BytesIO()
        plt.savefig(buf1, format="png")
        buf1.seek(0)
        images.append(Image.open(buf1))
    return images


distances_frames = [
    createDistanceHeatmap(distances, images)
    for distances, images in zip(
        distances[START : START + DURATION], images[START : START + DURATION]
    )
]

distances_frames[0].save(
    "./showcase_graphs/training_data.gif",
    save_all=True,
    append_images=distances_frames[1:],
    duration=DURATION * 10,
    loop=0,
)

# bw_t_frames[0].save(
#     "bw_t.gif",
#     save_all=True,
#     append_images=bw_t_frames[1:],
#     duration=DURATION * 10,
#     loop=0,
# )

# bw_t_1_frames[0].save(
#     "bw_t_1.gif",
#     save_all=True,
#     append_images=bw_t_1_frames[1:],
#     duration=DURATION * 10,
#     loop=0,
# )
