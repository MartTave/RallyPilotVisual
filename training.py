import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from torch.utils.data import TensorDataset
# import numpy
import pickle
import lzma
import matplotlib.pyplot as plt

from model import AlexNet


def prepareData(datas):
    x = []
    y = []
    for data in datas:
        for d in data:
            x.append(d.image.tolist())
            y.append(d.current_controls)
    return x, y


preparedData = ()


datas = []
BASE_FOLDER = "data/"
file_names = ["record_2.npz"]

for f in file_names:
    datas.append(pickle.load(lzma.open(BASE_FOLDER + f, "rb")))
preparedData = prepareData(datas)


print(f"Data prepared, {len(preparedData[0])} samples")

targetTensor = torch.tensor(preparedData[1], dtype=torch.uint8)
print("Target tensor created")
import ipdb

ipdb.set_trace()
sourceTensor = torch.tensor(preparedData[0], dtype=torch.float32)
print("Source tensor created")

dataset = TensorDataset(sourceTensor, targetTensor)

print("Created tensors")

train_size = int(0.8 * len(dataset))
validate_size = len(dataset) - train_size

train_data, validate_data = random_split(dataset, [train_size, validate_size])
print("Data splitted")
model = AlexNet()
print("Model initialized")

# Assuming you have your dataset prepared
train_loader = DataLoader(train_data, batch_size=64)

# Define loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# Training loop
num_epochs = 50
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device is : {device}")


criterion.to(device)
model.to(device)

train_losses = []
train_accuracies = []
validation_losses = []
validation_accuracies = []

for epoch in range(num_epochs):
    model.train()
    curr_loss = 0
    nbr_items = 0
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        curr_loss += loss.item()
        nbr_items += 1
    train_losses.append(curr_loss / nbr_items)

    curr_loss = 0
    nbr_items = 0

    for inputs, labels in validate_data:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        curr_loss += loss.item()
        nbr_items += 1
    validation_losses.append(curr_loss / nbr_items)

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

plt.figure()
plt.plot(train_losses, label="Training loss")
plt.plot(validation_losses, label="Validation loss")
plt.savefig("loss.png")
