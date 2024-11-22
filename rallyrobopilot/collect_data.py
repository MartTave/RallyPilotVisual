import os
import threading
from time import sleep
import time
from remote import Remote
import numpy as np

images = []
controls = []
speeds = []

running = True

DATA_FOLDER = "./data/record"
FILENAME = ".npz"
START_TRIM = 10
END_TRIM = 10


firstSensing = True

lastPicture = None


freqIndex = 0

def appendNewData(newData):
    global images, controls, lastPicture, freqIndex, speeds, firstSensing
    if firstSensing:
        print("Data collector amorced")
        firstSensing = False
        return
    x, y = Remote.convertFromMessageToTrainingData(newData)
    if lastPicture is not None:
        newX = np.stack((lastPicture, x), axis=0)
        speeds.append(newData["car_speed"])
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
# Cold starting the remote sensing
# (It is there to tell the game that it need to save screenshots...)
collector._getSensingData()
collector.reset()
print("Waiting for enter to start recording...")
input()
then = time.time()
collector.startSensing()
freqCalc()
print("Waiting for enter to stop recording...")
input()
collector.stopSensing()
now = time.time()
print(f"Saving data... {len(images)} frames for ", now - then, " seconds")
sleep(1)
images = images[START_TRIM:-END_TRIM]
controls = controls[START_TRIM:-END_TRIM]

images = np.array(images)
controls = np.array(controls)
speeds = np.array(speeds)

currIndex = 0
full_path = DATA_FOLDER + str(currIndex) + FILENAME
while os.path.exists(full_path):
    currIndex += 1
    full_path = DATA_FOLDER + str(currIndex) + FILENAME

running = False
np.savez(full_path, images=images, controls=controls, speeds=speeds)

collector.reset()


print(f"Saved file : {full_path}")
