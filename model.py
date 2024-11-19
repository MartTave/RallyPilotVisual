import torch
import torch.nn as nn
import numpy as np

class AlexNetAtHome(nn.Module):

    @staticmethod
    def concatTwoPics(pic1, pic2):
        return np.concatenate((pic1, pic2), axis=0).tolist()

    def __init__(self):
        super(AlexNetAtHome, self).__init__()

        self.features = nn.Sequential(
            nn.Conv2d(6, 32, kernel_size=11, stride=4, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(64, 80, kernel_size=3, padding=1),
            nn.BatchNorm2d(80),
            nn.ReLU(inplace=True),
            nn.Conv2d(80, 80, kernel_size=3, padding=1),
            nn.BatchNorm2d(80),
            nn.ReLU(inplace=True),
            nn.Conv2d(80, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )
        self.predictor = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(2304, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 4),
        )

    def forward(self, x):
        x = self.features(x)
        # TODO: Maybe add a avgPool ?
        x = torch.flatten(x, 1)
        x = self.predictor(x)
        return x
