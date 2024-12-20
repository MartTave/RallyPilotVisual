import threading
from time import sleep, time
import requests
import numpy as np
from rallyrobopilot.convert_to_bw import convertToBwSingle

class Remote:

    @staticmethod
    def convertFromMessageToTrainingData(data):
        x = []
        if "picture" in data:
            x = convertToBwSingle(np.array(data["picture"], dtype=np.uint8))
        else:
            print("[REMOTE] No pics in data !")
        y = [
            data["up"],
            data["down"],
            data["left"],
            data["right"],
        ]
        return x, y

    @staticmethod
    def getControlsFromData(x): 
        return [x["up"], x["down"], x["left"], x["right"]]

    def __init__(self, host, port, cb, getPicture=False, sanitiyChecks=True):
        self.lastSensing = time()
        self.lastSended = [0, 0, 0, 0]
        self.host = host
        self.port = port
        self.cb = cb
        self.sensing = False
        self.getPicture = getPicture
        self.sanitiyChecks = sanitiyChecks
        self.inferCount = 0
        self.thread = None
        self.sendCommand("release all;")

    def sendCommand(self, command):
        response = requests.post(
            f"{self.host}:{self.port}/command", json={"command": command}
        )
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} with status {response.json()['error']}"
            )
            return False
        return True

    def startRecording(self):
        response = requests.post(
            f"{self.host}:{self.port}/record", json={"picture": self.getPicture}
        )
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} with status {response.json()['error']}"
            )
            return False
        return True

    def stopRecording(self):
        response = requests.post(f"{self.host}:{self.port}/stop_record")
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} with status {response.json()['error']}"
            )
            return False
        return response.json()["data"]

    def sendControl(self, command: list[int]):
        converted = self._convertControl(command)
        for c in converted:
            self.sendCommand(c)
        return True

    def _convertControl(self, command: list[int]) -> list[str]:
        str_commands = []
        commandList = [(0, "forward"), (1, "back"), (2, "left"), (3, "right")]
        for i, c in commandList:
            if command[i] == 1 and self.lastSended[i] == 0:
                str_commands.append(f"push {c};")
            elif command[i] == 0 and self.lastSended[i] == 1:
                str_commands.append(f"release {c};")
        self.lastSended = command
        return str_commands

    def reset(self):
        self.sendCommand("reset;")

    def setStartPositionGAModel(self, position: tuple[float, float, float], angle: float, speed: float)->bool:
        response = requests.post(
            f"{self.host}:{self.port}/reset_wait_for_key", json={"startPosition": position, "startAngle": angle, "startSpeed": speed}
        )
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} with status {response.json()['error']}"
            )
            return False
        return True

    def setState(
        self,
        position: tuple[float, float, float],
        angle: float,
        speed: float,
    ):
        """
        *Do not use !*
        """
        self.sendCommand(f"set position {position[0]},{position[1]},{position[2]};")
        self.sendCommand(f"set rotation {angle};")
        self.sendCommand(f"set speed {speed};")

    def _getSensingData(self):
        response = requests.get(
            f"{self.host}:{self.port}/sensing", params={"picture": self.getPicture}
        )
        # We are more tolerant if the requests are too quick as it depends more on the time we take to process things
        if self.sanitiyChecks and (
            time() - self.lastSensing > 0.11 or time() - self.lastSensing < 0.09
        ):
            print("[REMOTE] Losing sync ! Time elapsed : ", time() - self.lastSensing)
        self.lastSensing = time()
        if response.status_code != 200:
            print(response)
            print(
                f"Received error response: {response.status_code} | with error : {response.json()['error']}"
            )
            return None
        currData = response.json()
        self.cb(currData)
        return currData

    def getDataForSolution(
        self,
        controlList: list[list[int]],
        startPosition: tuple[float, float, float],
        startAngle: float,
        speed: float,
        getPics: bool = False
    ) -> list[list[float]]:
        response = requests.post(
            f"{self.host}:{self.port}/GASolution",
            json={
                "controlList": controlList,
                "startPosition": startPosition,
                "startAngle": startAngle,
                "startSpeed": speed,
                "picture": getPics
            },
        )
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} with status {response.json()['error']}"
            )
            return False
        if getPics:
            json = response.json()
            return json
        else:
            return response.json()["result"]

    def sensingLoop(self):
        while self.sensing:
            self._getSensingData()

    def startSensing(self):
        if not self.sensing:
            print("[REMOTE] Starting sensing")
            self.sensing = True
            self.thread = threading.Thread(target=self.sensingLoop)
            self.thread.start()

    def stopSensing(self):
        if self.sensing:
            print("[REMOTE] Stopping sensing")
            self.sensing = False

count = 0

def gotNewFData(newData):
    global count
    count += 1
    pass


# remote = Remote("http://127.0.0.1", 5000, gotNewFData, True)

# then = time()
# remote.startSensing()
# sleep(1)
# remote.stopSensing()
# print("Got ", count, " data in ", time() - then, " seconds")
# sleep(1)
