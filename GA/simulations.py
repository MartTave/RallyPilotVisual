import os
from time import sleep
from rallyrobopilot.remote import Remote
import csv

dataCar = []
def getData(x):
    global dataCar 
    dataCar.append(x)
    

remote = Remote("http://127.0.0.1", 5000, getData)

controls = []
remote.startSensing()
sleep(15)
for i in dataCar:
    controls.append(remote.getControlsFromData(i))
remote.stopSensing()
print(controls)

with open("./gaData/controls1.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(controls)
