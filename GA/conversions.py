import csv, json
import os
import numpy as np
class Convertion():

    @staticmethod
    def getNewFolderName():
        BASE_PATH = "./GA/ga_data/"
        startIndex = 0
        currPath = os.path.join(BASE_PATH, f"ga_{startIndex}")
        while os.path.exists(currPath):
            startIndex += 1
            currPath = os.path.join(BASE_PATH, f"ga_{startIndex}")
        return currPath

    @staticmethod
    def dumpJson(newData):
        newPath = Convertion.getNewFolderName()
        os.makedirs(newPath, exist_ok=True)
        json_file_path = os.path.join(newPath, "metadata.json")
        with open(json_file_path, "w") as json_file:
            json.dump(newData, json_file, indent=4)

    @staticmethod
    def generateJsons():
        filePathPos ='positions.csv'
        with open(filePathPos, newline='') as csvfile:
            reader = csv.reader(csvfile)
            lines = list(reader)
            csvfile.close()
        lines[1:] = [[float(float(value)) for value in row] for row in lines[1:]]
        positions = lines
        for i in range(1, len(positions)-1,2):
            group = positions[i:i+2]
            data = {
                "startPoint": {
                    "x": group[0][0],
                    "y": group[0][1],
                    "z": group[0][2]
                },
                "endLine": {
                    "point1": {
                        "x": group[1][3],
                        "y": group[1][4],
                        "z": group[1][5]
                    },
                    "point2": {
                        "x": group[1][6],
                        "y": group[1][7],
                        "z": group[1][8]
                    }
                },
                "startAngle": group[0][9],
                "startVelocity": group[0][10],
                "baseControls": []
                }
            currPath = Convertion.getNewFolderName()

            os.makedirs(currPath, exist_ok=True)

            json_file_path = os.path.join(currPath, "metadata.json")
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

    def __init__(self, folder:str):
        filePathJson = './GA/ga_data'
        assert folder.startswith("ga_")
        self.fullPath = os.path.join(filePathJson, folder)
        assert os.path.isdir(self.fullPath)
        self.metadata_file_path = os.path.join(self.fullPath, "metadata.json")

    def writeControls(self, controls):
        data = {}
        with open(self.metadata_file_path, 'r') as json_file:
            data = json.load(json_file)
            data["baseControls"] = controls
        with open(self.metadata_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def readJson(self):
        jsonData = {}
        if os.path.exists(self.metadata_file_path):
            with open(self.metadata_file_path, 'r') as json_file:
                data = json.load(json_file)
                print(f"Data from {self.metadata_file_path}:")
                jsonData = data
        else:
            print(f"{self.metadata_file_path} does not exist.")
        return jsonData

    def writeJsonFile(self, data):
        json_file_path = os.path.join(self.fullPath, "results.json")
        res = {}
        for i,d in enumerate(data):
            res[i] = d
        with open(json_file_path, 'w') as json_file:
            json.dump(res, json_file, indent=4)

    def writeFitnessValues(self, fitness_value):
        npz_file_path = os.path.join(self.fullPath, "fitness_value.npz")
        np_arr = np.array(fitness_value)
        np.savez(npz_file_path,fitness_values = np_arr)

    def readFitnessValues(self):
        npz_file_path = os.path.join(self.fullPath, "fitness_value.npz")
        return np.load(npz_file_path)["fitness_values"]

    def readResults(self):
        if not self.hasResults():
            print("This GA has not result !")
            return None
        results_path = "results.json"
        fullPathResults = os.path.join(self.fullPath, results_path)
        with open(fullPathResults,"r" ) as json_file: 
            data = json.load(json_file)
            return data

    def hasResults(self):
        return os.path.exists(os.path.join(self.fullPath, "results.json"))


if __name__ == '__main__':
    Convertion.generateJsons()
