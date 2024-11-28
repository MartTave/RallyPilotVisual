import os
import threading
from time import sleep
import time
from data_tools.getDistance import getDistancesSingle
from remote import Remote
import numpy as np

images = []
controls = []
speeds = []
distances = []

DATA_FOLDER = "./data/record"
FILENAME = ".npz"
START_TRIM = 10
END_TRIM = 10


collector = Remote("http://127.0.0.1", 5000, lambda: "", True)
# Cold starting the remote sensing
# (It is there to tell the game that it need to save screenshots...)
collector.reset()
print("Waiting for enter to start recording...")
input()
then = time.time()
collector.startRecording()
print("Waiting for enter to stop recording...")
input()
print("Recording stopped, this might take a while to get the data from the simulation")
now = time.time()
data = collector.stopRecording()
print(f"Saving data... {len(data)} frames for ", now - then, " seconds")

PURE_CYAN = [0, 255, 255]
PURE_RED = [255, 0, 0]
PURE_BLUE = [0, 0, 255]

CURRENT_COLOR = np.array(PURE_CYAN)

lastPicture = None
for d in data:
    x, y = Remote.convertFromMessageToTrainingData(d)
    if lastPicture is not None:
        distances.append(getDistancesSingle(np.array(d["picture"]), CURRENT_COLOR))
        newX = np.stack((lastPicture, x), axis=0)
        speeds.append(d["car_speed"])
        images.append(newX)
        controls.append(y)
    lastPicture = x

images = images[START_TRIM:-END_TRIM]
controls = controls[START_TRIM:-END_TRIM]
speeds = speeds[START_TRIM:-END_TRIM]
distances = distances[START_TRIM:-START_TRIM]

images = np.array(images)
controls = np.array(controls)
speeds = np.array(speeds)
distances = np.array(distances)

assert len(distances) == len(images)


currIndex = 0
full_path = DATA_FOLDER + str(currIndex) + FILENAME
while os.path.exists(full_path):
    currIndex += 1
    full_path = DATA_FOLDER + str(currIndex) + FILENAME

np.savez(full_path, images=images, controls=controls, speeds=speeds, distances=distances)

collector.reset()


print(f"Saved file : {full_path}")
