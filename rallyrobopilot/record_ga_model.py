import json
import math
import os
from time import sleep
from rallyrobopilot.remote import Remote


GA_LENGTH = 80
OVERLAP = 20
BASE_FOLDER = "./GA/ga_data/"
DISTANCE = 5

remote = Remote("http://127.0.0.1", 5000, lambda: None)


print("Press enter to start the recording")
input()
sleep(1)
remote.startRecording()
print("Recording started")
print("Press enter to stop the recording")
input()
data = remote.stopRecording()
print("Recording stopped")


currI = 0
# Splitting the positions in slice of 80 controls (8 seconds)
# But we're taking an overlap of 2 seconds (20 controls)
for i in range(0, len(data), GA_LENGTH - OVERLAP):
    endIndex = min(len(data) - 1, i + GA_LENGTH - 1)
    if endIndex - i < OVERLAP:
        break
    startPoint = {
        "x": data[i]["car_position x"],
        "y": data[i]["car_position y"],
        "z": data[i]["car_position z"],
    }
    xChange = math.cos(data[endIndex]["car_angle"] * math.pi / 180) * DISTANCE
    zChange = math.sin(data[endIndex]["car_angle"] * math.pi / 180) * DISTANCE
    x1 = data[endIndex]["car_position x"] + xChange
    x2 = data[endIndex]["car_position x"] - xChange
    z1 = data[endIndex]["car_position z"] + zChange
    z2 = data[endIndex]["car_position z"] - zChange
    endLine = {
        "point1": {
            "x": x1,
            "y": data[endIndex]["car_position y"],
            "z": z1,
        },
        "point2": {
            "x": x2,
            "y": data[endIndex]["car_position y"],
            "z": z2,
        },
    }
    startAngle = data[i]["car_angle"]
    startVelocity = data[i]["car_speed"]
    baseControls = []
    import ipdb

    ipdb.set_trace()
    for d in data[i : endIndex + 1]:
        baseControls.append(
            [
                1 if d["up"] else 0,
                1 if d["down"] else 0,
                1 if d["left"] else 0,
                1 if d["right"] else 0,
            ]
        )
    assert len(baseControls) == endIndex - i + 1
    fileName = f"{BASE_FOLDER}ga_{currI}"
    while os.path.exists(fileName):
        currI += 1
        fileName = f"{BASE_FOLDER}ga_{currI}"
    os.makedirs(fileName, exist_ok=True)
    with open(os.path.join(fileName, "metadata.json"), "w") as jsonFile:
        json.dump(
            {
                "startPoint": startPoint,
                "endLine": endLine,
                "startAngle": startAngle,
                "startVelocity": startVelocity,
                "baseControls": baseControls,
            },
            jsonFile,
            indent=4,
        )

    print(
        f"Saved GA of length {endIndex - i + 1} to file {fileName} - Index from {i} to {endIndex}"
    )
