from math import sqrt
import numpy as np

class GaMaths(): 
    def __init__(self, endLine, startCarPosition):
        self.lastPos = startCarPosition
        self.endLine = endLine
        self.endLineA = (endLine[1][2] - endLine[0][2])/(endLine[1][0] -endLine[0][0])
        self.endLineB = endLine[0][2] - (self.endLineA*endLine[0][0])
        self.endLineCenter = [
            (endLine[1][0] + endLine[0][0]) / 2,
            0,
            (endLine[1][2] + endLine[0][2]) / 2
        ]
        self.startCarPosition = startCarPosition

    def computeDistance(self, posX , posZ):
        A = self.endLineA
        C = self.endLineB
        return (A * posX - posZ + C) / sqrt(A**2 + 1)

    def isInCircle(self, pos):
        dist = (
            sqrt((pos[0] - self.endLineCenter[0])**2 + (pos[1] - self.endLineCenter[2])**2)
        )
        return dist < 20

    def isArrivedToEndLine(self, posX, posZ):
        return self.isInCircle([posX, posZ]) and np.sign(self.computeDistance(posX,posZ))!= np.sign(self.computeDistance(self.startCarPosition[0], self.startCarPosition[2]))