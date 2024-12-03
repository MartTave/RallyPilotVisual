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




def getDistance(images, color):
    """
    Return the distance between the images and the color for each pixel of the images.
    """
    return np.sqrt(
        np.sum((images - color[np.newaxis, :, np.newaxis, np.newaxis]) ** 2, axis=1),
    )


def getDistancesSingle(image, color):
    """
    Return the distance between a single image and the color for each pixel of the
    """
    # Ensure image is of shape (3, 224, 224) and color is of shape (3,)
    assert image.shape == (3, 224, 224) and color.shape == (3,)
    
    # Reshape color to (3, 1, 1) for broadcasting
    color_reshaped = color[:, np.newaxis, np.newaxis]
    
    # Calculate squared differences
    squared_diff = (image - color_reshaped) ** 2
    
    # Sum along the color channel axis and take the square root
    distance = np.sqrt(np.sum(squared_diff, axis=0))
    
    return distance
