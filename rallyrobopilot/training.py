from multiprocessing import Pool
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
indexes = [0, 1, 2]
BASE_FILENAME = "record"
BASE_EXTENSION = ".npz"
file_names = [BASE_FILENAME + str(i) + BASE_EXTENSION for i in indexes]

xData = []
yData = []

def prepareData(npData):
    x = npData["images"]
    print(x.shape)
    assert x[0][0][0][0] != 0
    y = np.concatenate((npData["controls"], npData["speeds"][:].reshape(-1, 1)), axis=1)
    return x, y

def loadFile(filename):
    loaded = np.load(BASE_FOLDER + filename)
    print("Preparing file : ", filename)
    x, y = prepareData(loaded)
    assert len(x) == len(y)
    return x, y


with Pool() as pool:
    results = pool.map(loadFile, file_names)
    for x, y in results:
        xData += x.tolist()
        yData += y.tolist()

# for f in file_names:
#     loaded = np.load(BASE_FOLDER + f)
#     print("Preparing file : ", f)
#     x, y = prepareData(loaded)
#     assert len(x) == len(y)
#     xData += x
#     yData += y
#     print("Done... Added ", len(x), " samples")

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
classification_loss = nn.BCEWithLogitsLoss(torch.tensor([0.5, 2.5, 1, 1], dtype=torch.float32))
regression_loss = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.1, patience=2, verbose=True
)

# Training loop
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device is : {device}")

classification_loss.to(device)
regression_loss.to(device)
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
            y_class, y_reg = model(inputs)
            class_loss = classification_loss(y_class, labels[:, :4])
            reg_loss = regression_loss(y_reg.squeeze(), labels[:, 4])
            total_loss = class_loss + reg_loss
            if step == "train":
                total_loss.backward()
                optimizer.step()
            curr_loss += total_loss.item()
            y_class = (y_class > 0.5).float()
            correct += (y_class == labels[:, :4]).sum().item()
            total += labels.size(0) * labels.size(1)
            nbr_items += 1
        if step == "eval":
            scheduler.step(curr_loss)
        losses[step].append(curr_loss / nbr_items)
        accuracies[step].append(correct / total)

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {class_loss.item():.4f}")


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
