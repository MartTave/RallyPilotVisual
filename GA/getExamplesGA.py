import json
from math import sqrt
import os
from time import sleep
from GA.computeGAMaths import GaMaths
from GA.conversions import Convertion
from rallyrobopilot.remote import Remote
import time


class ControlsExamplesGA():
    def __init__(self, folder_name: str):
        self.jsonFile = Convertion(folder_name)
        self.jsonData = self.jsonFile.readJson()
        self.data = []      
        self.positions = []    

    def computeSimulation(self):
        print(self.jsonData)
        detectedF = False
        endLineReached = False
        self.data = []
        endLine = [(self.jsonData['endLine']['point1']['x'], self.jsonData['endLine']['point1']['y'],self.jsonData['endLine']['point1']['z']),(self.jsonData['endLine']['point2']['x'],self.jsonData['endLine']['point2']['y'],self.jsonData['endLine']['point2']['z'])]
        pos  = [self.jsonData['startPoint']['x'],self.jsonData['startPoint']['y'], self.jsonData['startPoint']['z']]
        computeMaths = GaMaths(endLine,pos)

        def getData(x):
            nonlocal detectedF, endLineReached, remote
            if not detectedF and x["up"] == 1 :
                self.then = time.time()
                detectedF = True
            if detectedF and not endLineReached:
                self.data.append([x["up"], x["down"], x["left"], x["right"]])
                self.positions.append([x['car_position x'], x["car_position y"], x["car_position z"]])
                if computeMaths.isArrivedToEndLine(self.positions[-1][0], self.positions[-1][2]):
                    print(f"I got {len(self.positions)} position for {time.time() - self.then} seconds")
                    endLineReached = True
                    remote.stopSensing()

        remote = Remote("http://127.0.0.1", 5000, getData)

        remote.setStartPositionGAModel(
            pos, self.jsonData["startAngle"], self.jsonData["startVelocity"]
        )
        remote.startSensing()
        while True:
            sleep(1)
            if endLineReached:
                self.jsonFile.writeControls(self.data)
                print("Written !")
                break


FOLDERNAME = "ga_0"

test = ControlsExamplesGA(FOLDERNAME)
test.computeSimulation()
