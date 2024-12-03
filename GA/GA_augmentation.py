import math
import random
from time import sleep
from rallyrobopilot.remote import Remote
from conversions import Convertion
from computeGAMaths import GaMaths

FOLDERS_NUMBER = range(7, 9)

FOLDERS = [f"ga_{i}" for i in FOLDERS_NUMBER]

remote = Remote("http://127.0.0.1", 5000, lambda x: x)


def log(*args):
    print("[GA_AUGM] ", *args)


def simulate(controls, data):
    return remote.getDataForSolution(
        controls,
        (
            data["startPoint"]["x"],
            data["startPoint"]["y"],
            data["startPoint"]["z"],
        ),
        data["startAngle"],
        data["startVelocity"],
    )


def hasCrossedLine(positions, endLine):
    if len(positions) == 0:
        return False
    computeMaths = GaMaths(
        [
            (endLine["point1"]["x"], endLine["point1"]["y"], endLine["point1"]["z"]),
            (endLine["point2"]["x"], endLine["point2"]["y"], endLine["point2"]["z"]),
        ],
        positions[0],
    )
    endLineReached = False
    for p in positions:
        if computeMaths.isArrivedToEndLine(p[0], p[2]):
            endLineReached = True
            break
    return endLineReached


def getRandomDist(limits=(-1, -0.5, 0.5, 1)):
    range_choice = random.choice(["negative", "positive"])

    if range_choice == "negative":
        return random.uniform(limits[0], limits[1])
    else:
        return random.uniform(limits[2], limits[3])


def getStartingPoints(folder_name, number=10, distance=5):

    file = Convertion(folder_name)
    data = file.readJson()

    testing = simulate(data["baseControls"], data)

    if not hasCrossedLine(testing, data["endLine"]):
        log("The base controls do not cross the line !")
        return

    xChange = math.cos(data["startAngle"] * math.pi / 180)
    zChange = math.sin(data["startAngle"] * math.pi / 180)
    startPoints = []
    while len(startPoints) < number:
        xCurrChange = getRandomDist() * distance * xChange
        zCurrChange = getRandomDist() * distance * zChange
        newStartPoint = (
            data["startPoint"]["x"] + xCurrChange,
            data["startPoint"]["y"],
            data["startPoint"]["z"] + zCurrChange,
        )
        result = simulate(
            data["baseControls"],
            {
                "startPoint": {
                    "x": newStartPoint[0],
                    "y": newStartPoint[1],
                    "z": newStartPoint[2],
                },
                "startAngle": data["startAngle"],
                "startVelocity": data["startVelocity"],
            },
        )
        if hasCrossedLine(result, data["endLine"]):
            startPoints.append(newStartPoint)
            log("New start point found ! Found ", len(startPoints), " / ", number)
        else:
            log("Tried a new start point, failed...")
        remote.sendControl([0, 0, 0, 0])
        sleep(0.1)
    return startPoints


for f in FOLDERS:
    newPoints = getStartingPoints(f, number=15, distance=5)
    for p in newPoints:
        baseData = Convertion(f).readJson()
        baseData["augmented"] = True
        baseData["startPoint"] = {
            "x": p[0],
            "y": p[1],
            "z": p[2],
        }
        Convertion.dumpJson(baseData)
