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

TRAINED_MODELS = []

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device is : {device}")
if len(sys.argv) > 1:
    USE_SYMETRIC = bool(sys.argv[1])
    if len(sys.argv) > 2:
        DATA_INDEXES = [int(i) for i in sys.argv[2:]]
        if len(sys.argv) > 3 :
            TRAINED_MODELS = [str(i) for i in sys.argv[len(DATA_INDEXES) +1 :]]
            for i in TRAINED_MODELS: 
                model.load_state_dict(torch.load(f"./models/{i}/model.pth"))  
                model.to(device)  
preparedData = ()


regression_weight = 0.2

num_epochs = 100

BASE_FOLDER = "./data/"
BASE_FILENAME = "record_norm"
BASE_EXTENSION = ".npz"
file_names = [BASE_FILENAME + str(i) + BASE_EXTENSION for i in DATA_INDEXES]
if USE_SYMETRIC:
    file_names += [
        BASE_FILENAME + str(i) + "_flipped" + BASE_EXTENSION for i in DATA_INDEXES
    ]

xData = []
yData = []




def prepareData(npData):
    x = np.concatenate((npData["images"], npData["distances"][:, np.newaxis, :, :]), axis=1)
    assert x[0][0][0][0] != 0
    y = npData["controls"]
    return x, y

def loadFile(filename):
    loaded = np.load(BASE_FOLDER + filename)
    print("Preparing file : ", filename)
    x, y = prepareData(loaded)
    print(x.shape, " for file ", filename)
    assert len(x) == len(y)
    return x, y


with Pool() as pool:
    results = pool.map(loadFile, file_names)
    xData = np.concatenate([x for x, _ in results])
    yData = np.concatenate([y for _, y in results])

assert len(xData) == len(yData)

print(f"Data prepared, {len(xData)} samples")

targetTensor = torch.tensor(yData, dtype=torch.float32)
targetTensor.to(device)
print("Target tensor created")
sourceTensor = torch.tensor(xData, dtype=torch.float32)
sourceTensor.to(device)
print("Source tensor created")

dataset = TensorDataset(sourceTensor, targetTensor)

print("Created tensors")

train_size = int(0.8 * len(dataset))
validate_size = len(dataset) - train_size

train_data, validate_data = random_split(dataset, [train_size, validate_size])

train_loader = DataLoader(train_data, batch_size=32)

validate_loader = DataLoader(validate_data, batch_size=32)

# Define loss function and optimizer
classification_loss = nn.BCEWithLogitsLoss(
    torch.tensor([0.3, 1.3, 1, 1], dtype=torch.float32)
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
}
accuracies = {
    "train": [],
    "eval": [],
}

# Training loop


for epoch in range(num_epochs):

    for step in ["train", "eval"]:
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
        f"Epoch [{epoch+1}/{num_epochs}], Loss: {class_loss.item():.4f}, Acc : {accuracies['eval'][-1]:.4f}"
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
