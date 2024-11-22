import numpy as np


# Define the weights for RGB to grayscale conversion
weights = np.array([0.299, 0.587, 0.114])

# Reshape weights to broadcast correctly
weights = weights.reshape(1, 3, 1, 1)


weights_single = np.array([0.299, 0.587, 0.114], dtype=np.float32)

def convertToBw(images):
    bw = np.zeros(
        (images.shape[0], 2, images.shape[2], images.shape[3]), dtype=np.float32
    )
    bw[:, 0] = np.sum(images[:, :3] * weights, axis=1) / 255
    bw[:, 1] = np.sum(images[:, 3:6] * weights, axis=1) / 255
    return bw


def convertToBwSingle(image):
    return np.dot(image.transpose(1, 2, 0), weights_single) / 255
