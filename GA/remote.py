import threading
from time import time
import requests


class Remote:

    @staticmethod
    def convertFromMessageToTrainingData(data):
        x = data["picture"]

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

    def __init__(self, host, port, cb, getPicture=False):
        self.lastSended = [0, 0, 0, 0]
        self.host = host
        self.port = port
        self.cb = cb
        self.sensing = False
        self.timer = None
        self.getPicture = getPicture
        self.inferCount = 0
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

    def _evalPerf(self):
        if not self.sensing:
            return
        print("Current frq: ", self.inferCount / 5, " infer/s")
        self.inferCount = 0
        threading.Timer(5, self._evalPerf).start()

    def _getSensingData(self):
        response = requests.get(f"{self.host}:{self.port}/sensing")
        self.inferCount += 1
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} | with error : {response.json()['error']}"
            )
            return None
        currData = response.json()
        if self.getPicture:
            response = requests.get(f"{self.host}:{self.port}/picture")
            if response.status_code != 200:
                print(
                    f"Received error response: {response.status_code} | with error : {response.json()['error']}"
                )
                return None
            currData["picture"] = response.json()["image"]
        self.cb(currData)

    def _sensingLoop(self):
        if self.sensing:
            self.timer = threading.Timer(0.1, self._sensingLoop)
            self.timer.start()
            self._getSensingData()

    def getDataForSolution(
        self,
        controlList: list[list[int]],
        startPosition: tuple[float, float, float],
        startAngle: float,
        speed: float,
    ) -> list[list[float]]:
        response = requests.post(
            f"{self.host}:{self.port}/GASolution",
            json={
                "controlList": controlList,
                "startPosition": startPosition,
                "startAngle": startAngle,
                "startSpeed": speed,
            },
        )
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} with status {response.json()['error']}"
            )
            return False
        return response.json()["result"]

    def startSensing(self):
        if not self.sensing:
            self.sensing = True
            self._evalPerf()
            self._sensingLoop()

    def stopSensing(self):
        if self.sensing:
            self.sensing = False
            if self.timer:
                self.timer.cancel()
                self.timer = None


def gotNewFData(newData):
    pass


#remote = Remote("http://127.0.0.1", 5000, gotNewFData, True)

controls_list = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [1, 0, 1, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 1, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 1, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 1, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 0],
]
