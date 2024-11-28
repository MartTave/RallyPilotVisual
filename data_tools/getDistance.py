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
    # Ensure image is of shape (3, 224, 224) and color is of shape (3,)
    assert image.shape == (3, 224, 224) and color.shape == (3,)
    
    # Reshape color to (3, 1, 1) for broadcasting
    color_reshaped = color[:, np.newaxis, np.newaxis]
    
    # Calculate squared differences
    squared_diff = (image - color_reshaped) ** 2
    
    # Sum along the color channel axis and take the square root
    distance = np.sqrt(np.sum(squared_diff, axis=0))
    
    return distance
