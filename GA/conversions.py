import csv, json
import os
class Convertion():
    def __init__(self):
        self.filePathPos ='positions.csv'
        self.filePathJson = './GA/ga_data'
        with open(self.filePathPos, newline='') as csvfile:
            reader = csv.reader(csvfile)
            lines = list(reader)
            csvfile.close()
        lines[1:] = [[float(float(value)) for value in row] for row in lines[1:]]
        self.positions = lines
    def generateJsons(self):
        c = 0
        for i in range(1, len(self.positions)-1,2):
            group = self.positions[i:i+2]
            data = {
                "startPoint": {
                    "x": group[0][0],
                    "z": group[0][1],
                    "y": group[0][2]
                },
                "endLine": {
                    "point1": {
                        "x": group[1][3],
                        "z": group[1][4],
                        "y": group[1][5]
                    },
                    "point2": {
                        "x": group[1][6],
                        "z": group[1][7],
                        "y": group[1][8]
                    }
                },
                "startAngle": group[0][9],
                "startVelocity": group[0][10],
                "baseControls": []
                }
            folder_path = os.path.join(self.filePathJson, f"ga_{c}")

            os.makedirs(folder_path, exist_ok=True)

            json_file_path = os.path.join(folder_path, "metadata.json")
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            c+=1

    
    def readJsons(self):
        jsonData = []
        json_directory = self.filePathJson

        for folder_name in os.listdir(json_directory):
            folder_path = os.path.join(json_directory, folder_name)

            if os.path.isdir(folder_path) and folder_name.startswith("ga_"):
                metadata_file_path = os.path.join(folder_path, "metadata.json")

            if os.path.exists(metadata_file_path):
                with open(metadata_file_path, 'r') as json_file:
                    data = json.load(json_file)
                    print(f"Data from {metadata_file_path}:")
                    jsonData.append(data)
            else:
                print(f"{metadata_file_path} does not exist.")
        print(jsonData)
        return jsonData
    
