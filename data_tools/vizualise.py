from time import sleep
import numpy as np
from PIL import Image

file = np.load("./data/record0.npz")

pictures = file["images"]


# Transpose the array to get the correct shape (224, 224, 3)


for i, pic in enumerate(pictures):
    array = pic.transpose(1, 2, 0).astype(np.uint8)
    firstPic = array[:, :, :3]
    secondPic = array[:, :, 3:]
    # Create an image from the array
    image = Image.fromarray(firstPic)
    image.save("./data/trash/test_n-1.png")
    # Display the image
    image = Image.fromarray(secondPic)
    # Display the image
    image.save("./data/trash/test_n.png")
    print("Showing image for time : ", i)
    sleep(1.5)

# # Optionally, save the image
# image.save("output_image.png")
