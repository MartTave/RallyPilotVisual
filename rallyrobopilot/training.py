from math import sqrt
from multiprocessing import Pool
import os
import sys
import torch
import torch.optim as optim
from torch.optim.lr_scheduler import ExponentialLR
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from torch.utils.data import TensorDataset
from torchvision import transforms

import numpy as np
import pickle
import lzma
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from model import AlexNetAtHome

model = AlexNetAtHome()


DATA_INDEXES = [0, 1, 2, 3]

USE_SYMETRIC = True

TRAINED_MODELS = ""

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device is : {device}")
if len(sys.argv) > 1:
    USE_SYMETRIC = bool(sys.argv[1])
    if len(sys.argv) > 2:
        TRAINED_MODEL = str(sys.argv[3])
        if TRAINED_MODEL != "None":
            model.load_state_dict(torch.load(f"./models/{TRAINED_MODEL}/model.pth"), weights_only=True)  
            model.to(device)
        # if len(sys.argv) > 3 :
        #     DATA_INDEXES = [int(i) for i in sys.argv[3 :]]



num_epochs = 100

BASE_FOLDER = "./data/"
TRAIN_FOLDER = f"{BASE_FOLDER}train"
TEST_FOLDER = f"{BASE_FOLDER}test"

train_files = []
test_files = []

for f in [(TRAIN_FOLDER, train_files), (TEST_FOLDER, test_files)]:
    files = os.listdir(f[0])
    for fi in files:
        curr_path = f"{f[0]}/{fi}"
        if os.path.isfile(curr_path):
            f[1].append(curr_path)

print(f"Loading {train_files} for training")
print(f"Loading {test_files} for testing")

xData = []
yData = []




def prepareData(npData):
    x = np.concatenate((npData["images"], npData["distances"][:, np.newaxis, :, :]), axis=1)
    assert x[0][0][0][0] != 0
    y = npData["controls"]
    return x, y

def loadFile(filename):
    loaded = np.load(filename)
    print("Preparing file : ", filename)
    x, y = prepareData(loaded)
    print(x.shape, " for file ", filename)
    assert len(x) == len(y)
    return x, y


testX = []
testY = []

with Pool() as pool:
    results = pool.map(loadFile, train_files)
    xData = np.concatenate([x for x, _ in results])
    yData = np.concatenate([y for _, y in results])
    
with Pool() as pool:
    results = pool.map(loadFile, test_files)
    testX = np.concatenate([x for x, _ in results])
    testY = np.concatenate([y for _, y in results])

assert len(xData) == len(yData)
assert len(testX) == len(testY)

print(f"Data prepared, {len(xData)} samples")

targetTensor = torch.tensor(yData, dtype=torch.float32)
targetTensor.to(device)
print("Target tensor created")
sourceTensor = torch.tensor(xData, dtype=torch.float32)
sourceTensor.to(device)
print("Source tensor created")

testTargetTensor = torch.tensor(testY, dtype=torch.float32)
testTargetTensor.to(device)
testSourceTensor = torch.tensor(testX, dtype=torch.float32)
testSourceTensor.to(device)

dataset = TensorDataset(sourceTensor, targetTensor)

print("Created tensors")

train_size = int(0.8 * len(dataset))
validate_size = len(dataset) - train_size

train_data, validate_data = random_split(dataset, [train_size, validate_size])

train_loader = DataLoader(train_data, batch_size=32)

validate_loader = DataLoader(validate_data, batch_size=32)

# Define loss function and optimizer
classification_loss = nn.BCEWithLogitsLoss(
    torch.tensor([0.3, 1, 1, 1], dtype=torch.float32)
)

# Keep weight decays really small
optimizer = optim.Adam(model.parameters(), lr=1e-4, weight_decay=1e-6)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.1, patience=3
)

classification_loss.to(device)
model.to(device)

losses = {
    "train": [],
    "eval": [],
    "test": []
}
accuracies = {
    "train": [],
    "eval": [],
    "test": []
}

# Training loop


for epoch in range(num_epochs):

    for step in ["train", "eval", "test"]:
        if step == "test":
            model.eval()
            optimizer.zero_grad()
            y_pred = model(testSourceTensor)
            loss = classification_loss(y_pred, testTargetTensor[:, :4])
            y_pred = (y_pred > 0.5).float()
            correct += (y_class == labels[:, :4]).sum().item()
            total += labels.size(0) * labels.size(1)
            losses[step].append(loss.item())
            accuracies[step].append(correct / total)
            continue
        currLoader = train_loader if step == "train" else validate_loader
        if step == "train":
            model.train()
        else:
            model.eval()
        curr_loss = 0
        nbr_items = 0
        correct = 0
        total = 0
        for inputs, labels in currLoader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            y_class = model(inputs)
            class_loss = classification_loss(y_class, labels[:, :4])
            if step == "train":
                class_loss.backward()
                optimizer.step()
            curr_loss += class_loss.item()
            y_class = (y_class > 0.5).float()
            correct += (y_class == labels[:, :4]).sum().item()
            total += labels.size(0) * labels.size(1)
            nbr_items += 1
        if step == "eval":
            scheduler.step(curr_loss)
        losses[step].append(curr_loss / nbr_items)
        accuracies[step].append(correct / total)

    print(
        f"Epoch [{epoch+1}/{num_epochs}], Loss: {class_loss.item():.4f}, Acc : {accuracies['eval'][-1]:.4f} - Test loss : {losses['test'][-1]}, Test Acc : {accuracies['test'][-1]}"
    )


MODEL_BASE_PATH = "./models/"


def saveResults():
    currIndex = 0
    currPath: str
    if not os.path.exists(MODEL_BASE_PATH):
        os.mkdir(MODEL_BASE_PATH)
    while True:
        currPath = MODEL_BASE_PATH + f"model_{currIndex}"
        if not os.path.exists(currPath):
            break
        currIndex += 1

    os.mkdir(currPath)
    torch.save(model.state_dict(), currPath + "/model.pth")
    print("Saved model to ", currPath)
    plt.figure()
    plt.plot(losses["train"], label="Training loss")
    plt.plot(losses["eval"], label="Validation loss")
    plt.yscale("log")
    plt.legend()
    plt.title("Loss")
    plt.savefig(currPath + "/loss.png")
    plt.figure()
    plt.plot(accuracies["train"], label="Training accuracy")
    plt.plot(accuracies["eval"], label="Validation accuracy")
    plt.ylim((0, 1))
    plt.legend()
    plt.title("Accuracy")
    plt.savefig(currPath + "/accuracy.png")


saveResults()
