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

    def checkIfCrossedLine(self, remote: Remote, computeMaths: GaMaths):
        data = remote._getSensingData()
        if not data:
            return False
        return computeMaths.isArrivedToEndLine(
            data["car_position x"], data["car_position z"]
        )

    def computeSimulation(self):
        detectedF = False
        endLineReached = False
        self.data = []
        endLine = [(self.jsonData['endLine']['point1']['x'], self.jsonData['endLine']['point1']['y'],self.jsonData['endLine']['point1']['z']),(self.jsonData['endLine']['point2']['x'],self.jsonData['endLine']['point2']['y'],self.jsonData['endLine']['point2']['z'])]
        pos  = [self.jsonData['startPoint']['x'],self.jsonData['startPoint']['y'], self.jsonData['startPoint']['z']]
        computeMaths = GaMaths(endLine,pos)

        remote = Remote("http://127.0.0.1", 5000, lambda x: "", sanitiyChecks=False)

        remote.setStartPositionGAModel(
            pos, self.jsonData["startAngle"], self.jsonData["startVelocity"]
        )
        remote.startRecording()
        print("Detecting cross line...")
        while not self.checkIfCrossedLine(remote, computeMaths):
            sleep(0.5)
        # This is here to ensure we have crossed the line !
        sleep(0.5)
        print("Detected ! - Stopping recording")
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
        print("Loading next one !")
        sleep(2)


FOLDERNAME = [f"ga_{i}" for i in range(1, 2)]

for f in FOLDERNAME:
    test = ControlsExamplesGA(f)
    test.computeSimulation()
