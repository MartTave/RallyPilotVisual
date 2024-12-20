import torch
import torch.nn as nn
import numpy as np

class AlexNetAtHome(nn.Module):

    @staticmethod
    def concatTwoPics(pic1, pic2):
        return np.stack((pic1, pic2), axis=0)

    def __init__(self):
        super(AlexNetAtHome, self).__init__()

        firstLayerSize = 25
        secondLayerSize = 45
        thirdLayerSize = 60
        fourthLayerSize = 60
        fifthLayerSize = 45
        # Calculate the input size of the predictor layer, this is the size of the last layer of the features flattenend
        predictorInputSize = 1620

        # Maybe diminish stride -> reduce kernel size and

        self.features = nn.Sequential(
            nn.Conv2d(3, firstLayerSize, kernel_size=11, stride=4, padding=2),
            nn.BatchNorm2d(firstLayerSize),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(firstLayerSize, secondLayerSize, kernel_size=5, padding=2),
            nn.BatchNorm2d(secondLayerSize),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(secondLayerSize, thirdLayerSize, kernel_size=3, padding=1),
            nn.BatchNorm2d(thirdLayerSize),
            nn.ReLU(inplace=True),
            nn.Conv2d(thirdLayerSize, fourthLayerSize, kernel_size=3, padding=1),
            nn.BatchNorm2d(fourthLayerSize),
            nn.ReLU(inplace=True),
            nn.Conv2d(fourthLayerSize, fifthLayerSize, kernel_size=3, padding=1),
            nn.BatchNorm2d(fifthLayerSize),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )
        self.predictor = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(predictorInputSize, 100),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(100, 4),
        )

    def forward(self, x):
        x = self.features(x)
        # TODO: Maybe add a avgPool ?
        x = torch.flatten(x, 1)
        x = self.predictor(x)
        return x
