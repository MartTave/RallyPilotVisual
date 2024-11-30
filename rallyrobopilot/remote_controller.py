from time import sleep
import time
from ursina import *
import socket
import select
import numpy as np
from pygame.time import Clock


from flask import Flask, request, jsonify

from rallyrobopilot.car import Car


from .sensing_message import SensingSnapshot, SensingSnapshotManager
from .remote_commands import RemoteCommandParser


GRACE_TIME_GA = 0

REMOTE_CONTROLLER_VERBOSE = False
PERIOD_REMOTE_SENSING = 0.1

def printv(str):
    if REMOTE_CONTROLLER_VERBOSE:
        print(str)

class RemoteController(Entity):

    def __init__(self, car: Car = None, flask_app=None):
        super().__init__()

        self.clock = Clock()

        self.car = car

        if self.car.timeManager.dt != 0.1:
            print(
                "\n================================\n[REMOTE CONTROLLER] Simulating GA wihtout a dt of 0.1 will not work !!!!\n================================\n"
            )

        self.lastSensingSanity = time.time()

        self.record = []
        self.recording = False
        self.recordPictures = False

        self.listen_socket = None
        self.connected_client = None

        self.client_commands = RemoteCommandParser()

        self.lastScreenshot = None
        self.texYSize = 0
        self.texXSize = 0

        self.simuIndex = 0
        self.simulating = False
        self.simuResult = []

        #   Period for recording --> 0.1 secods = 10 times a second
        self.sensing_period = PERIOD_REMOTE_SENSING
        self.last_sensing = -1

        # Setup http route for updating.
        @flask_app.route('/command', methods=['POST'])
        def send_command_route():
            if self.car is None:
                return jsonify({"error": "No car connected"}), 400

            command_data = request.json
            if not command_data or 'command' not in command_data:
                return jsonify({"error": "Invalid command data"}), 400

            if self.simulating:
                return jsonify({"error": "Please wait until simulation is over"}), 400

            try:
                self.client_commands.add(command_data['command'].encode())
                return jsonify({"status": "Command received"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @flask_app.route("/record", methods=["POST"])
        def start_recording():
            if self.car is None:
                return jsonify({"error": "No car connected"}), 400

            if self.simulating:
                return jsonify({"error": "Please wait until simulation is over"}), 400

            if self.recording:
                return jsonify({"error": "Already recording"}), 400
            data = request.json
            if "picture" in data and data["picture"] == True:
                self.recordPictures = True
            else:
                self.recordPictures = False
            self.recording = True
            self.record = []
            return jsonify({"status": "Recording started"}), 200

        @flask_app.route("/stop_record", methods=["POST"])
        def stop_recording():
            if self.car is None:
                return jsonify({"error": "No car connected"}), 400

            if self.simulating:
                return jsonify({"error": "Please wait until simulation is over"}), 400

            if not self.recording:
                return jsonify({"error": "Not recording"}), 400

            self.recording = False
            self.recordPictures = False
            return jsonify({"status": "Recording stopped", "data": self.record}), 200

        @flask_app.route("/picture", methods=["GET"])
        def get_picture_route():
            data = self.lastScreenshot
            image = data.reshape(self.texYSize, self.texXSize, 3)
            image = image[::-1, :, :]
            image = image.transpose((2, 0, 1))
            return jsonify({"image": image.tolist()}), 200

        @flask_app.route("/sensing")
        def get_sensing_route():
            self.clock.tick(10)
            now = time.time()
            elapsed = now - self.lastSensingSanity
            picture = request.args.get("picture")
            if not elapsed > 1 and (elapsed < 0.09 or elapsed > 0.11):
                print(
                    "[GAME] Losing sync ! Last sensing was ",
                    elapsed,
                    " seconds ago",
                )
            data = self.get_sensing_data()
            if picture and picture == "True":
                self.recordPictures = True
                if self.lastScreenshot is not None:
                    arr = self.lastScreenshot
                    image = arr.reshape(self.texYSize, self.texXSize, 3)
                    image = image[::-1, :, :]
                    image = image.transpose((2, 0, 1))
                    data["picture"] = image.tolist()
            else:
                self.recordPictures = False
            self.lastSensingSanity = now
            return jsonify(data), 200

        @flask_app.route("/reset_wait_for_key", methods=["POST"])
        def recordGaModel():
            data = request.json
            if not data:
                return jsonify({"error": "Invalid command data"}), 400
            if self.simulating:
                return jsonify({"error": "Please wait until simulation is over"}), 400
            startPosition = data["startPosition"]
            startAngle = data["startAngle"]
            startSpeed = data["startSpeed"]
            self.car.waitForStart = True
            self.car.reset_position = startPosition
            self.car.reset_orientation = (0, startAngle, 0)
            self.car.reset_speed = startSpeed
            self.car.reset_car()
            return jsonify({"status": "Position set"}), 200

        @flask_app.route("/GASolution", methods=["POST"])
        def testGaSolution():
            data = request.json
            if not data:
                return jsonify({"error": "Invalid command data"}), 400
            if self.simulating:
                return jsonify({"error": "Already simulating"}), 400

            if "picture" in data and data["picture"] == True:
                self.recordPictures = True
            self.controlList = data["controlList"]
            startPosition = data["startPosition"]
            startAngle = data["startAngle"]
            startSpeed = data["startSpeed"]
            self.car.reset_position = startPosition
            self.car.reset_orientation = (0, startAngle, 0)
            self.car.reset_speed = startSpeed
            self.car.collisionHappened = False
            self.simulating = True
            # Sync of last sensing
            # For it to start playing controls back immediately
            self.simuIndex = -1
            self.simuResult = []
            while self.simulating:
                sleep(0.25)
            return jsonify({"result": self.simuResult}), 200

    def simulateGA(
        self,
    ):
        # Here we need to run next control and save position
        if self.car.collisionHappened:
            self.simuResult = []
            self.simulating = False
            self.car.collisionHappened = False
            self.car.reset_car()
            return
        if self.simuIndex == -1:
            self.car.reset_car()
            self.simuIndex += 1
        if self.simuIndex >= len(self.controlList) + GRACE_TIME_GA:
            self.simulating = False
            self.simuResult.append(
                [
                    self.car.world_position[i]
                    for i, v in enumerate(self.car.world_position)
                ]
            )
            return
        currControl: list[int]
        if self.simuIndex < len(self.controlList):
            currControl = self.controlList[self.simuIndex]
        else:
            currControl = [0, 0, 0, 0]
        mapping = {0: "w", 1: "s", 2: "a", 3: "d"}
        for i, c in enumerate(currControl):
            held_keys[mapping[i]] = c == 1
        self.simuResult.append(
            [
                self.car.world_position[i]
                for i, v in enumerate(self.car.world_position)
            ]
        )
        self.simuIndex += 1
        self.last_sensing = time.time()
        pass

    def update(self):
        if self.car is None:
            return
        if self.simulating:
            self.simulateGA()
        else:
            self.process_remote_commands()
            if self.recordPictures:
                self.updateScrenshot()
        if self.recording:
            data = self.get_sensing_data()
            if self.recordPictures:
                tex = base.win.getDisplayRegion(0).getScreenshot()
                arr = np.frombuffer(tex.getRamImageAs("rgb"), np.uint8)
                image = arr.reshape(224, 224, 3)
                image = image[::-1, :, :].transpose((2, 0, 1))
                data["picture"] = image.tolist()
            self.record.append(data)

    def updateScrenshot(self):
        if self.car is None:
            return
        now = time.time()
        period = now - self.last_sensing
        # if period >= self.sensing_period - 0.02:
        tex = base.win.getDisplayRegion(0).getScreenshot()
        self.texYSize = tex.getYSize()
        self.texXSize = tex.getXSize()
        arr = tex.getRamImageAs("rgb")
        data = np.frombuffer(arr, np.uint8)
        if period > self.sensing_period + 0.02:
            print("[GAME] Update of screenshot is late ! ", period, " s")
        self.lastScreenshot = data
        self.last_sensing = now

    def get_sensing_data(self):
        current_controls = (held_keys['w'] or held_keys["up arrow"],
                            held_keys['s'] or held_keys["down arrow"],
                            held_keys['a'] or held_keys["left arrow"],
                            held_keys['d'] or held_keys["right arrow"])
        car_position = self.car.world_position
        car_speed = self.car.speed
        car_angle = self.car.rotation_y
        return {'up': current_controls[0],
                'down': current_controls[1],
                'left': current_controls[2], 
                'right': current_controls[3],
                'car_position x': car_position[0],
                'car_position y': car_position[1],
                'car_position z': car_position[2],
                'car_speed': car_speed,
                'car_angle': car_angle
                }

    def process_remote_commands(self):
        if self.car is None:
            return

        while len(self.client_commands) > 0:
            try:
                commands = self.client_commands.parse_next_command()
                if commands[0] == b'push' or commands[0] == b'release':
                    if commands[1] == b'forward':
                        held_keys['w'] = commands[0] == b'push'
                    elif commands[1] == b'back':
                        held_keys['s'] = commands[0] == b'push'
                    elif commands[1] == b'right':
                        held_keys['d'] = commands[0] == b'push'
                    elif commands[1] == b'left':
                        held_keys['a'] = commands[0] == b'push'

                # Release all
                if commands[0] == b'release' and commands[1] == b'all':
                    held_keys['w'] = False
                    held_keys['s'] = False
                    held_keys['d'] = False
                    held_keys['a'] = False

                elif commands[0] == b'set':
                    if commands[1] == b'position':
                        self.car.reset_position = commands[2]
                    elif commands[1] == b'rotation':
                        self.car.reset_orientation = (0, commands[2], 0)
                    elif commands[1] == b'speed':
                        self.car.reset_speed = commands[2]
                        pass
                    elif commands[1] == b'ray':
                        self.car.multiray_sensor.set_enabled_rays(commands[2] == b'visible')

                elif commands[0] == b'reset':
                    self.car.reset_car()

            #   Error is thrown when commands do not fit the model --> disconnect client
            except Exception as e:
                print("Invalid command --> disconnecting : " + str(e))
                if self.connected_client is not None:
                    self.connected_client.close()
                    self.connected_client = None
