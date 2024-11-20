from math import sqrt
import numpy as np

class GaMaths(): 
    def __init__(self, endLine, startCarPosition):
        self.endLineA = (endLine[1][2] - endLine[0][2])/(endLine[1][0] -endLine[0][0])
        self.endLineB = endLine[1][2] - (self.endLineA*endLine[1][0])
        self.startCarPosition = startCarPosition
        
    def computeDistance(self, posX , posY):
        A = self.endLineA
        B = -1
        C = self.endLineB
        return A * posX + B * posY + C / sqrt(A**2 + B**2)
    
    def isArrivedToEndLine(self, posX, posY):
        print(self.computeDistance(posX,posY), self.computeDistance(self.startCarPosition[0], self.startCarPosition[2]))
        return np.sign(self.computeDistance(posX,posY))!= np.sign(self.computeDistance(self.startCarPosition[0], self.startCarPosition[2]))