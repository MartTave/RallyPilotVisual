import numpy as np


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
    return np.sqrt(
        np.sum((image - color[:, np.newaxis, np.newaxis]) ** 2, axis=1),
    )
