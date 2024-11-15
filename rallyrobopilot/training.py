import os
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
import matplotlib.pyplot as plt

from model import AlexNetAtHome

model = AlexNetAtHome()


preparedData = ()


num_epochs = 25

BASE_FOLDER = "./data/"
indexes = [0, 1]
BASE_FILENAME = "record"
BASE_EXTENSION = ".npz"
file_names = [BASE_FILENAME + str(i) + BASE_EXTENSION for i in indexes]

xData = []
yData = []


def prepareData(npData):
    lastPic = None
    x = npData["images"].tolist()
    assert x[0][0][0] != 0
    y = npData["controls"].tolist()
    return x, y


for f in file_names:
    loaded = np.load(BASE_FOLDER + f)
    x, y = prepareData(loaded)
    xData += x
    yData += y

assert len(xData) == len(yData)

print(f"Data prepared, {len(xData)} samples")

targetTensor = torch.tensor(yData, dtype=torch.float32)
print("Target tensor created")
sourceTensor = torch.tensor(xData, dtype=torch.float32)
print("Source tensor created")

dataset = TensorDataset(sourceTensor, targetTensor)

print("Created tensors")

train_size = int(0.8 * len(dataset))
validate_size = len(dataset) - train_size

train_data, validate_data = random_split(dataset, [train_size, validate_size])

train_loader = DataLoader(train_data, batch_size=32)

validate_loader = DataLoader(validate_data, batch_size=32)

# Define loss function and optimizer
criterion = nn.BCEWithLogitsLoss(torch.tensor([0.5, 2.5, 1, 1], dtype=torch.float32))
optimizer = optim.Adam(model.parameters(), lr=0.0001)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.1, patience=2, verbose=True
)

# Training loop
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device is : {device}")

criterion.to(device)
model.to(device)

losses = {
    "train": [],
    "eval": [],
}
accuracies = {
    "train": [],
    "eval": [],
}

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
            y_pred = model(inputs)
            loss = criterion(y_pred, labels)
            if step == "train":
                loss.backward()
                optimizer.step()
            curr_loss += loss.item()
            y_pred = (y_pred > 0.5).float()
            correct += (y_pred == labels).sum().item()
            total += labels.size(0) * labels.size(1)
            nbr_items += 1
        if step == "eval":
            scheduler.step(curr_loss)
        losses[step].append(curr_loss / nbr_items)
        accuracies[step].append(correct / total)

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")


MODEL_BASE_PATH = "./models/"


def saveResults():
    currIndex = 0
    currPath: str
    while True:
        currPath = MODEL_BASE_PATH + f"model_{currIndex}"
        if not os.path.exists(currPath):
            break
        currIndex += 1

    os.mkdir(currPath)
    torch.save(model.state_dict(), currPath + "/model.pth")
    plt.figure()
    plt.plot(losses["train"], label="Training loss")
    plt.plot(losses["eval"], label="Validation loss")
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
