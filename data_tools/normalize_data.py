import numpy as np
from rallyrobopilot.normalize_distances import normalize_distances
DATA_NUMBER = 2

DATA_FILE = f"./data/record_flipped{DATA_NUMBER}_test.npz"



arr = np.load(DATA_FILE)
images = arr["images"]
controls = arr["controls"]
speed = arr["speeds"]
distances = arr["distances"]

normDistances = normalize_distances(distances)

print("Converted to black and white")

np.savez_compressed(
    f"./data/record_norm{DATA_NUMBER}_flipped_test.npz",
    images=images,
    controls=controls,
    speeds=speed,
    distances= normDistances
)