import computeGAMaths

line = [
    [0, 0, -20],
    [0.1, 0,  20]
]

startPos = [
    [20, 0, 0],
    [-20, 0, 0]
]


math = computeGAMaths.GaMaths(line, startPos[0])

print(math.computeDistance(startPos[0][0], startPos[0][2]))
print(math.computeDistance(startPos[1][0], startPos[1][2]))