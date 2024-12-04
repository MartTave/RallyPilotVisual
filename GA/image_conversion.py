import os
import json
from data_tools.getDistance import getDistancesSingle
import numpy as np
from GA.computeGAMaths import GaMaths
from GA.conversions import Convertion
from rallyrobopilot.convert_to_bw import convertToBwSingle
from rallyrobopilot.normalize_distances import normalize_distances
from rallyrobopilot.remote import Remote
class ImageConversion: 
    def __init__(self, numbersGA):
        self.numbersGA= numbersGA
        self.remote = Remote("http://127.0.0.1", 4999, lambda x:"")
        self.simulateGA()
        pass
    def simulateGA(self):
        CURRENT_COLOR = np.array([255, 0, 0])
        for i in self.numbersGA:
            file = Convertion(f"ga_{i}")
            startData = file.readJson()
            currMath = GaMaths([
                (startData["endLine"]["point1"]["x"],
                 startData["endLine"]["point1"]["y"],
                 startData["endLine"]["point1"]["z"]),
                (
                    startData["endLine"]["point2"]["x"],
                    startData["endLine"]["point2"]["y"],
                    startData["endLine"]["point2"]["z"]
                    )
            ],
            (startData["startPoint"]["x"],
                 startData["startPoint"]["y"],
                 startData["startPoint"]["z"])
            )
            results = file.readResults()
            currControls = list(results.values())[0]
            data = self.remote.getDataForSolution(
                currControls,
                (
                    startData["startPoint"]["x"],
                    startData["startPoint"]["y"],
                    startData["startPoint"]["z"],
                ),
                startData["startAngle"],
                startData["startVelocity"],
                True,
            )
            frames = []
            controls = []
            lastPic = None
            distances_normalized = []
            full_path = "./data/train/record_GA"
            try:
                assert len(data["pictures"]) == len(data["result"])
            except:
                print("Skipping GA : ", i)
                continue
            for j, (pic, pos) in enumerate(zip(data["pictures"], data["result"])):
                if currMath.isArrivedToEndLine(pos[0], pos[2]):
                    break
                bw_pic = convertToBwSingle(np.array(pic, dtype=np.uint8))
                if lastPic is not None:
                    distances = getDistancesSingle(np.array(pic), CURRENT_COLOR)
                    distances_normalized.append(normalize_distances(distances))
                    frames.append(np.stack((lastPic, bw_pic), axis=0))
                    controls.append(currControls[j - 1])
                lastPic = bw_pic
            assert len(frames) == len(controls) == len(distances_normalized)
            np.savez(
                f"{full_path}{i}.npz",
                images=frames,
                controls=controls,
                distances=distances_normalized,
            )
            print("Saved file : ", f"{full_path}{i}.npz")


ImageConversion(range(80, 147))
