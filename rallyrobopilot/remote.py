import json
import threading
from time import sleep
import requests


class Remote:
    def __init__(self, host, port, cb):
        self.lastSended = [0, 0, 0, 0]
        self.host = host
        self.port = port
        self.cb = cb
        self.sensing = False
        self.timer = None
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
            print(f"Sending : {c}")
            self.sendCommand(c)
        return True

    def _convertControl(self, command: list[int]) -> list[str]:
        str_commands = []
        commandList = [(0, "forward"), (1, "backward"), (2, "left"), (3, "right")]
        for i, c in commandList:
            if command[i] == 1 and self.lastSended[i] == 0:
                str_commands.append(f"push {c};")
            elif command[i] == 0 and self.lastSended[i] == 1:
                str_commands.append(f"release {c};")
        self.lastSended = command
        return str_commands

    def reset(self):
        self.sendCommand("reset;")

    def setState(
        self,
        position: tuple[float, float, float],
        angle: float,
        speed: tuple[float, float, float],
    ):
        self.sendCommand(f"set position {position[0]},{position[1]},{position[2]};")
        self.sendCommand(f"set rotation {angle};")
        self.sendCommand(f"set speed {speed[0]},{speed[1]},{speed[2]};")

    def getSensingData(self):
        response = requests.get(f"{self.host}:{self.port}/sensing")
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} | with error : {response.json()['error']}"
            )
            return None
        self.cb(response.json())

    def _sensingLoop(self):
        if self.sensing:
            self.getSensingData()
            self.timer = threading.Timer(0.1, self._sensingLoop)
            self.timer.start()

    def startSensing(self):
        if not self.sensing:
            self.sensing = True
            self._sensingLoop()

    def stopSensing(self):
        if self.sensing:
            self.sensing = False
            if self.timer:
                self.timer.cancel()
                self.timer = None


remote = Remote("http://127.0.0.1", 5000, lambda x: print(x["car_speed"] % 360))

remote.sendControl([1, 0, 0, 0])
sleep(1)
remote.sendControl([1, 0, 0, 0])
sleep(1)
remote.sendControl([0, 0, 0, 0])
sleep(1)
