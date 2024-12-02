import json
from math import sqrt
import os
from time import sleep
from computeGAMaths import GaMaths
from conversions import Convertion
from rallyrobopilot.remote import Remote
import time


class ControlsExamplesGA():
    def __init__(self, folder_name: str):
        self.jsonFile = Convertion(folder_name)
        self.jsonData = self.jsonFile.readJson()
        self.data = []      
        self.positions = []    

    def computeSimulation(self):
        detectedF = False
        endLineReached = False
        self.data = []
        endLine = [(self.jsonData['endLine']['point1']['x'], self.jsonData['endLine']['point1']['y'],self.jsonData['endLine']['point1']['z']),(self.jsonData['endLine']['point2']['x'],self.jsonData['endLine']['point2']['y'],self.jsonData['endLine']['point2']['z'])]
        pos  = [self.jsonData['startPoint']['x'],self.jsonData['startPoint']['y'], self.jsonData['startPoint']['z']]
        computeMaths = GaMaths(endLine,pos)

        remote = Remote("http://127.0.0.1", 5000, lambda :'')

        remote.setStartPositionGAModel(
            pos, self.jsonData["startAngle"], self.jsonData["startVelocity"]
        )
        remote.startRecording()
        print("Press enter to stop recording")
        input()
        res = remote.stopRecording()
        detectedF = False
        for i, p in enumerate(res):
            if not detectedF and p["up"] == 1 :
                detectedF = True
            if detectedF:
                self.data.append([p["up"], p["down"], p["left"], p["right"]])
                self.positions.append([p['car_position x'], p["car_position y"], p["car_position z"]])
                print(
                    computeMaths.computeDistance(
                        self.positions[-1][0], self.positions[-1][2]
                    )
                )
                if computeMaths.isArrivedToEndLine(self.positions[-1][0], self.positions[-1][2]):
                    endLineReached = True
                    break
        if endLineReached:
            self.jsonFile.writeControls(self.data)
            print("Written !")
        else:
            print("End line not reached ! - File not saved !!!")


FOLDERNAME = [f"ga_{i}" for i in range(9, 12)]

for f in FOLDERNAME:
    test = ControlsExamplesGA(f)
    test.computeSimulation()
