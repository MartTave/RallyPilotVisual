import io
from time import sleep

from matplotlib import pyplot as plt
import numpy as np
from GA.computeGAMaths import GaMaths
from rallyrobopilot.remote import Remote
from GA.conversions import Convertion
from PIL import Image

FOLDERS = 136

remote = Remote("http://127.0.0.1", 5000, lambda x: x)


def cutDataAtEndLine(data, math):
    images = []
    for i, p in enumerate(data["result"]):
        images.append(data["pictures"][i])
        if computeMaths.isArrivedToEndLine(p[0], p[2]):
            print("Length solution : ", i + 1)
            break
    return images


def simulate(controls, data):
    p = remote.getDataForSolution(
        controls,
        (
            data["startPoint"]["x"],
            data["startPoint"]["y"],
            data["startPoint"]["z"],
        ),
        data["startAngle"],
        data["startVelocity"],
        True,
    )
    return p


file = Convertion(f"simple_track/ga_{FOLDERS}")
jsonFile = file.readJson()


endLine = [
    (
        jsonFile["endLine"]["point1"]["x"],
        jsonFile["endLine"]["point1"]["y"],
        jsonFile["endLine"]["point1"]["z"],
    ),
    (
        jsonFile["endLine"]["point2"]["x"],
        jsonFile["endLine"]["point2"]["y"],
        jsonFile["endLine"]["point2"]["z"],
    ),
]
pos = [
    jsonFile["startPoint"]["x"],
    jsonFile["startPoint"]["y"],
    jsonFile["startPoint"]["z"],
]
computeMaths = GaMaths(endLine, pos)

print("Length base controls : ", len(jsonFile["baseControls"]))
print("Simulating example for ", FOLDERS)
exampleData = simulate(jsonFile["baseControls"], jsonFile)

exampleImages = cutDataAtEndLine(exampleData, computeMaths)
endLine = [
    (
        jsonFile["endLine"]["point1"]["x"],
        jsonFile["endLine"]["point1"]["y"],
        jsonFile["endLine"]["point1"]["z"],
    ),
    (
        jsonFile["endLine"]["point2"]["x"],
        jsonFile["endLine"]["point2"]["y"],
        jsonFile["endLine"]["point2"]["z"],
    ),
]
pos = [
    jsonFile["startPoint"]["x"],
    jsonFile["startPoint"]["y"],
    jsonFile["startPoint"]["z"],
]
computeMaths = GaMaths(endLine, pos)
controls = file.readResults()
print("Simulating results for ", FOLDERS)
resultData = simulate(list(controls.values())[0], jsonFile)

resultImages = cutDataAtEndLine(resultData, computeMaths)
print("Done")
remote.sendControl([0, 0, 0, 0])


def createImage(images):
    plt.figure()
    plt.tight_layout()

    plt.imshow(images)
    plt.xticks([])
    plt.yticks([])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf)


exampleData = np.transpose(exampleImages, (0, 2, 3, 1))
resultData = np.transpose(resultImages, (0, 2, 3, 1))

exampleFrames = [createImage(pic) for pic in exampleData]
resultFrames = [createImage(pic) for pic in resultData]

exampleFrames[0].save(
    f"test1.gif",
    save_all=True,
    append_images=exampleFrames[1:],
    duration=100,
    loop=0,
)
resultFrames[0].save(
    f"test2.gif",
    save_all=True,
    append_images=resultFrames[1:],
    duration=100,
    loop=0,
)
