from math import sqrt, tan
import csv
import os

from rallyrobopilot.remote import Remote

class Positions(): 
    def __init__(self, carPosX, carPosY, carAngle, carSpeed):
        self.carPosX = carPosX
        self.carPosY = carPosY
        self.carAngle = carAngle
        self.carSpeed = carSpeed
        
    def getPositions(self,distance):
        mPerp = -(1/tan(self.carAngle))
        x1 = self.carPosX + (distance/sqrt(1 + pow(mPerp,2)))
        x2 = self.carPosX - (distance/sqrt(1 + pow(mPerp,2)))
        y1 = self.carPosY + ((distance*mPerp)/sqrt(1 + pow(mPerp,2)))
        y2 = self.carPosY - ((distance*mPerp)/sqrt(1 + pow(mPerp,2)))
        return [(self.carPosX, 0.0 ,self.carPosY), (x1,0.0,y1), (x2,0.0,y2), (self.carAngle, self.carSpeed)]
    def write_positions_to_csv(self,distance, filename='positions.csv'):
        positions = self.getPositions(distance)
        print("pos")
        flat_positions = [value for position in positions for value in position]

        file_empty = not os.path.exists(filename) or os.path.getsize(filename) == 0
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file_empty:
                writer.writerow(['carPosX','carPosZ', 'carPosY', 'x1Point','z1Point', 'y1Point', 'x2Point','z2Point','y2Point','angle', 'speed']) 
            writer.writerow(flat_positions)
        print(f"Positions written to {filename}")

positionData = []
def getData(x):
    positionData.append((x["car_position x"], x["car_position z"], x["car_position y"]))
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
        positions = Positions(carPosX=positionData[0][0], carPosY=positionData[0][1], carAngle=positionData[1], carSpeed=positionData[2])
        positions.write_positions_to_csv(distance=40)
        positionData = []
        print("Saved position")



