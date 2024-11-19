import threading
import torch
from model import AlexNetAtHome
from remote import Remote

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

print("Device is : ", device)

model_number = 4

model = AlexNetAtHome()
model.load_state_dict(torch.load(f"./models/model_{model_number}/model.pth", map_location=device))
lastPic = None

model = model.to(device)

model.eval()

inferCount = 0


def evalPerf():
    global inferCount
    print("Current frq: ", inferCount / 5, " infer/s")
    inferCount = 0
    threading.Timer(5, evalPerf).start()


with torch.no_grad():

    def sensingNewData(newData):
        global lastPic, inferCount
        pic = newData["picture"]
        if lastPic is not None:
            x = AlexNetAtHome.concatTwoPics(lastPic, pic)
            xTensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(device)
            classification = model(xTensor)
            probs = torch.sigmoid(classification)
            probList = probs[0].tolist()
            controls = [1 if p > 0.5 else 0 for p in probList]
            remote.sendControl(controls)
            inferCount += 1
        lastPic = pic

    remote = Remote("http://127.0.0.1", 5000, sensingNewData, True)
    remote.startSensing()
    evalPerf()
    print("Press enter to quit...")
    input()
