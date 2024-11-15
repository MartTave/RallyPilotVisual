from math import sqrt
from time import sleep
from GA.conversions import Convertion
from rallyrobopilot.remote import Remote


class ControlsExamplesGA():
    def __init__(self):
 
        self.jsonsData = Convertion().readJsons()
        self.data = []           
        
        for i in range(len(self.jsonsData)):
            detectedF = False
            endLineReached = False
            remote = Remote("127.0.0.1", 5000, getData)

            def getData(x):
                if x["up"] == 1 : 
                    self.detectedF = True
                if detectedF:
                    self.data.append(x["up"], x["down"], x["left"], x["right"])
                if endLineReached : 
                    remote.stopSensing()
            
            pos  = [self.jsonsData[i]['startPoint']['x'],self.jsonsData[i]['startPoint']['z'], self.jsonsData[i]['startPoint']['y']]
            remote.setStartPositionGAModel(pos, self.jsonsData[i]['startaAngle'], self.jsonsData[i]['startVelocity'])
            remote.startSensing()
            while True: 
                remote._getSensingData()
                sleep(1)
    def writeControlsJson(self): 
        
    