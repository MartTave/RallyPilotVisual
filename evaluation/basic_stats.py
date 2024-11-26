from multiprocessing import Pool
import sys
import numpy as np
import matplotlib.pyplot as plt
import torch

from model import AlexNetAtHome

MODEL_NUMBER = 0
DATA_NUMBER = [2, 3]

if len(sys.argv) > 1:
    MODEL_NUMBER = int(sys.argv[1])
    if len(sys.argv) > 2:
        DATA_NUMBER = [int(i) for i in sys.argv[2:]]

BASE_FOLDER = "./data/"

BASE_FILENAME = "record"
BASE_EXTENSION = ".npz"


LABELS = ["forward", "backward", "left", "right"]


def log(*arg):
    print("[EVAL] ", *arg)


class Stats:

    @staticmethod
    def accuracy(y_preds, y_true):
        total = y_true.size(0) * y_true.size(1)
        y_preds = torch.where(y_preds < 0.5, 0, 1)
        correct = (y_preds == y_true[:, :4]).sum().item()
        return correct / total

    @staticmethod
    def accuracyPerClass(
        y_preds, y_true, labels=["forward", "backward", "left", "right"]
    ):
        class_accuracies = {}
        for i, l in enumerate(labels):
            correct = (y_preds[:, i] == y_true[:, i]).sum().item()
            class_accuracies[l] = correct / len(y_preds)
        return class_accuracies


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

log("Device is : ", device)

model = AlexNetAtHome()
model.load_state_dict(
    torch.load(
        f"./models/model_{MODEL_NUMBER}/model.pth",
        map_location=device,
        weights_only=True,
    )
)
model = model.to(device)


log(f"Loaded model n° {MODEL_NUMBER}")


file_names = [BASE_FILENAME + str(i) + BASE_EXTENSION for i in DATA_NUMBER]


def prepareData(npData):
    x = npData["images"]
    assert x[0][0][0][0] != 0
    y = npData["controls"]
    return x, y


def loadFile(filename):
    loaded = np.load(BASE_FOLDER + filename)
    log("Preparing file : ", filename)
    x, y = prepareData(loaded)
    log(x.shape, " for file ", filename)
    assert len(x) == len(y)
    return x, y


with Pool() as pool:
    results = pool.map(loadFile, file_names)
    xData = np.concatenate([x for x, _ in results])
    yData = np.concatenate([y for _, y in results])

assert len(xData) == len(yData)

xData = torch.tensor(xData, dtype=torch.float32).to(device)
yData = torch.tensor(yData, dtype=torch.float32).to(device)

log(f"Data prepared, {len(xData)} samples")

with torch.no_grad():
    model.eval()

    y_preds = torch.sigmoid(model(xData))

    total = yData.size(0) * yData.size(1)
    y_preds = torch.where(y_preds < 0.5, 0, 1)

    log("Accuracy is : ", Stats.accuracy(y_preds, yData))
    class_accuracies = Stats.accuracyPerClass(y_preds, yData, LABELS)
    for l in class_accuracies.keys():
        log(f"Accuracy for {l} is : ", class_accuracies[l])
