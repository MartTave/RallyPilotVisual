from model import AlexNetAtHome
import torch

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

MODEL_NUMBER = 1
model = AlexNetAtHome()
model.load_state_dict(
    torch.load(f"./models/model_{MODEL_NUMBER}/model.pth", map_location=device)
)

lastPic = None

model = model.to(device)

CURRENT_COLOR = np.array([0, 0, 255])

model.eval()

with torch.no_grad():

 lastPic
    if "picture" not in newData:
        return
    pic = np.array(newData["picture"])
    pic = convertToBwSingle(pic)
    if lastPic is not None:
        x = np.concatenate((AlexNetAtHome.concatTwoPics(lastPic, pic), getDistancesSingle(np.array(newData["picture"]), CURRENT_COLOR)[np.newaxis, :, :]), axis=0)
        xTensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(device)
        classification = model(xTensor)
        probs = torch.sigmoid(classification)
        probList = probs[0].tolist()
        controls = [1 if p > 0.5 else 0 for p in probList]
        remote.sendControl(controls)
    lastPic = pic
