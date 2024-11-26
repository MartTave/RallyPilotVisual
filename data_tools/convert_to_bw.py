import numpy as np

DATA_NUMBER = 0

DATA_FILE = f"./data/record{DATA_NUMBER}.npz"


# Define the weights for RGB to grayscale conversion
weights = np.array([0.299, 0.587, 0.114])

# Reshape weights to broadcast correctly
weights = weights.reshape(1, 3, 1, 1)


# Convert the image array to black and white value
def convertToBW(images):
    bw = np.zeros(
        (images.shape[0], 2, images.shape[2], images.shape[3]), dtype=np.float32
    )
    bw[:, 0] = np.sum(images[:, :3] * weights, axis=1) / 255
    bw[:, 1] = np.sum(images[:, 3:6] * weights, axis=1) / 255
    return bw


arr = np.load(DATA_FILE)
images = arr["images"]
controls = arr["controls"]
speed = arr["speeds"]

bwImages = convertToBW(images)

print("Converted to black and white")

np.savez_compressed(
    f"./data/record_bw{DATA_NUMBER}.npz",
    images=bwImages,
    controls=controls,
    speeds=speed,
)
