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
            nn.Conv2d(6, 96, kernel_size=11, stride=4, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(96, 256, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(256, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )
        self.predictor = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(9216, 4096),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(4096, 100),
            nn.ReLU(),
        )
        self.classification_head = nn.Sequential(
            nn.Linear(100, 4),
        )
        self.regression_head = nn.Sequential(
            nn.Linear(100, 1),
        )

    def forward(self, x):
        x = self.features(x)
        # TODO: Maybe add a avgPool ?
        x = torch.flatten(x, 1)
        x = self.predictor(x)
        classification = self.classification_head(x)
        regression = self.regression_head(x)
        return classification, regression
