from math import cos, sin, sqrt, tan
import csv
import math
import os

from rallyrobopilot.remote import Remote

class Positions(): 
    def __init__(self, carPosX, carPosZ, carAngle, carSpeed):
        self.carPosX = carPosX
        self.carPosZ = carPosZ
        self.carAngle = carAngle
        self.carSpeed = carSpeed
        
    def getPositions(self,distance):
        mPerp = -(1/tan(-self.carAngle))
        xChange = cos(self.carAngle * math.pi / 180) * distance
        zChange = sin(self.carAngle * math.pi / 180) * distance
        x1 = self.carPosX + xChange
        x2 = self.carPosX - xChange
        z1 = self.carPosZ + zChange
        z2 = self.carPosZ - zChange
        return [(self.carPosX, 0.0 ,self.carPosZ), (x1,0.0,z1), (x2,0.0,z2), (self.carAngle, self.carSpeed)]
    def write_positions_to_csv(self,distance, filename='positions.csv'):
        positions = self.getPositions(distance)
        print("pos")
        flat_positions = [value for position in positions for value in position]

        file_empty = not os.path.exists(filename) or os.path.getsize(filename) == 0
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file_empty:
                writer.writerow(['carPosX','carPosY', 'carPosZ', 'x1Point','y1Point', 'z1Point', 'x2Point','y2Point','z2Point','angle', 'speed']) 
            writer.writerow(flat_positions)
        print(f"Positions written to {filename}")

positionData = []
def getData(x):
    positionData.append((x["car_position x"], x["car_position y"], x["car_position z"]))
    positionData.append(x["car_angle"])
    positionData.append(x['car_speed'])
    
remote =Remote("http://127.0.0.1", 5000, getData)
while True:
    print("Press enter so save position. q to quit")
    letter = input()
    if letter == "q":
        break
    else:
        remote._getSensingData()
        print(positionData)
        positions = Positions(carPosX=positionData[0][0], carPosZ=positionData[0][2], carAngle=positionData[1], carSpeed=positionData[2])
        positions.write_positions_to_csv(distance=5)
        positionData = []
        print("Saved position")



