import sys
import threading
from time import sleep
from data_tools.getDistance import getDistancesSingle
from rallyrobopilot.normalize_distances import normalize_distances
import torch
from model import AlexNetAtHome
from remote import Remote
import numpy as np
from convert_to_bw import convertToBwSingle

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

print("Device is : ", device)

MODEL_NUMBER = 0
if len(sys.argv) > 1:
    MODEL_NUMBER = int(sys.argv[1])

model = AlexNetAtHome()
model.load_state_dict(
    torch.load(f"./models/model_{MODEL_NUMBER}/model.pth", map_location=device)
)
lastPic = None

model = model.to(device)

CURRENT_COLOR = np.array([255,0,0])

model.eval()

with torch.no_grad():

    def sensingNewData(newData):
        global lastPic
        if "picture" not in newData:
            return
        pic = np.array(newData["picture"])
        pic = convertToBwSingle(pic)
        if lastPic is not None:
            distances = getDistancesSingle(np.array(newData["picture"]), CURRENT_COLOR)
            distances_normalized = normalize_distances(distances)
            x = np.concatenate((AlexNetAtHome.concatTwoPics(lastPic, pic), distances_normalized[np.newaxis, :, :]), axis=0)
            xTensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(device)
            classification = model(xTensor)
            probs = torch.sigmoid(classification)
            probList = probs[0].tolist()
            controls = [1 if p > 0.5 else 0 for p in probList]
            remote.sendControl(controls)
        lastPic = pic

    remote = Remote("http://127.0.0.1", 5000, sensingNewData, True)
    remote.startSensing()
    print("Press enter to quit...")
    input()
    remote.stopSensing()
