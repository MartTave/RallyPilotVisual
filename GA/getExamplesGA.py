import json
from math import sqrt
import os
from time import sleep
from GA.computeGAMaths import GaMaths
from GA.conversions import Convertion
from rallyrobopilot.remote import Remote
import time


class ControlsExamplesGA():
    def __init__(self):
 
        self.jsonsData = Convertion().readJsons()
        self.data = []      
        self.positions = []    
    def writeControlsJson(self, i): 
        json_path = f'./GA/ga_data/ga_{i}/metadata.json'
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
            data["baseControls"] = self.data
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def computeSimulations(self):
        for i in range(len(self.jsonsData)):
            detectedF = False
            endLineReached = False
            self.data = []
            def getData(x):
                nonlocal detectedF, endLineReached, remote
                if not detectedF and x["up"] == 1 :
                    print("here") 
                    detectedF = True
                if detectedF and not endLineReached:
                    self.data.append([x["up"], x["down"], x["left"], x["right"]])
                    self.positions.append([x['car_position x'], x["car_position z"], x["car_position y"]])
                    if computeMaths.isArrivedToEndLine(self.positions[-1][0], self.positions[-1][2]):
                        print("Got to endline !")
                        print(f"I got {len(self.positions)} position for {time.time() - self.then} seconds")
                        endLineReached = True
                        remote.stopSensing()
               
            remote = Remote("http://127.0.0.1", 5000, getData)
            endLine = [(self.jsonsData[i]['endLine']['point1']['x'], self.jsonsData[i]['endLine']['point1']['z'],self.jsonsData[i]['endLine']['point1']['y']),(self.jsonsData[i]['endLine']['point2']['x'],self.jsonsData[i]['endLine']['point2']['z'],self.jsonsData[i]['endLine']['point2']['y'])]
            pos  = [self.jsonsData[i]['startPoint']['x'],self.jsonsData[i]['startPoint']['z'], self.jsonsData[i]['startPoint']['y']]
            remote.setStartPositionGAModel(pos, self.jsonsData[i]['startAngle'], self.jsonsData[i]['startVelocity'])
            computeMaths = GaMaths(endLine,pos)
            self.then = time.time()
            remote.startSensing()
            while True:
                sleep(1)
                if endLineReached:
                    self.writeControlsJson(i)
                    print("Written !")
                    break
  

test = ControlsExamplesGA()
test.computeSimulations()