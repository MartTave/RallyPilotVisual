import os
import threading
from time import sleep
import time
from remote import Remote
import numpy as np

images = []
controls = []
speeds = []

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
data = collector.stopRecording()
now = time.time()
print(f"Saving data... {len(data)} frames for ", now - then, " seconds")


lastPicture = None
for d in data:
    x, y = Remote.convertFromMessageToTrainingData(d)
    if lastPicture is not None:
        newX = np.stack((lastPicture, x), axis=0)
        speeds.append(d["car_speed"])
        images.append(newX)
        controls.append(y)
    lastPicture = x

images = images[START_TRIM:-END_TRIM]
controls = controls[START_TRIM:-END_TRIM]
speeds = speeds[START_TRIM:-END_TRIM]

images = np.array(images)
controls = np.array(controls)
speeds = np.array(speeds)

currIndex = 0
full_path = DATA_FOLDER + str(currIndex) + FILENAME
while os.path.exists(full_path):
    currIndex += 1
    full_path = DATA_FOLDER + str(currIndex) + FILENAME

np.savez(full_path, images=images, controls=controls, speeds=speeds)

collector.reset()


print(f"Saved file : {full_path}")
