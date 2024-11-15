import os
import threading
from time import sleep
from remote import Remote
import numpy as np

images = []
controls = []


running = True

DATA_FOLDER = "./data/record"
FILENAME = ".npz"
START_TRIM = 10
END_TRIM = 10


lastPicture = None


freqIndex = 0

def appendNewData(newData):
    global images, controls, lastPicture, freqIndex
    x, y = Remote.convertFromMessageToTrainingData(newData)
    if lastPicture is not None:
        newX = np.concatenate((lastPicture, x), axis=0)
        images.append(newX)
        controls.append(y)
    lastPicture = x
    freqIndex += 1


def freqCalc():
    global running, freqIndex
    if not running:
        return
    threading.Timer(10, freqCalc).start()
    print(f"Data frequency is : ", freqIndex / 10)
    freqIndex = 0


collector = Remote("http://127.0.0.1", 5000, appendNewData, True)

collector.reset()
print("Waiting for enter to start recording...")
input()
collector.startSensing()
freqCalc()
print("Waiting for enter to stop recording...")
input()
collector.stopSensing()
print(f"Saving data... {len(images)} frames")
sleep(1)
images = images[START_TRIM:-END_TRIM]
controls = controls[START_TRIM:-END_TRIM]

images = np.array(images)
controls = np.array(controls)

currIndex = 0
full_path = DATA_FOLDER + str(currIndex) + FILENAME
while os.path.exists(full_path):
    currIndex += 1
    full_path = DATA_FOLDER + str(currIndex) + FILENAME

np.savez(full_path, images=images, controls=controls)

collector.reset()
