from time import sleep
from ursina import *
import socket
import select
import numpy as np

from flask import Flask, request, jsonify

from rallyrobopilot.car import Car


from .sensing_message import SensingSnapshot, SensingSnapshotManager
from .remote_commands import RemoteCommandParser


GRACE_TIME_GA = 5

REMOTE_CONTROLLER_VERBOSE = False
PERIOD_REMOTE_SENSING = 0.1

def printv(str):
    if REMOTE_CONTROLLER_VERBOSE:
        print(str)

class RemoteController(Entity):

    def __init__(self, car: Car = None, connection_port=7654, flask_app=None):
        super().__init__()

        self.ip_address = "127.0.0.1"
        self.port = connection_port
        self.car = car

        self.listen_socket = None
        self.connected_client = None

        self.client_commands = RemoteCommandParser()

        self.reset_location = (0,0,0)
        self.reset_speed = (0,0,0)
        self.reset_rotation = 0

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

            try:
                self.client_commands.add(command_data['command'].encode())
                return jsonify({"status": "Command received"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @flask_app.route("/picture", methods=["GET"])
        def get_picture_route():
            data = self.lastScreenshot
            image = data.reshape(self.texYSize, self.texXSize, 3)
            image = image[::-1, :, :]
            image = image.transpose((2, 0, 1))
            return jsonify({"image": image.tolist()}), 200

        @flask_app.route("/sensing")
        def get_sensing_route():
            return jsonify(self.get_sensing_data()), 200

        @flask_app.route("/GASolution", methods=["POST"])
        def testGaSolution():
            data = request.json
            if not data:
                return jsonify({"error": "Invalid command data"}), 400
            if self.simulating:
                return jsonify({"error": "Already simulating"}), 400
            self.controlList = data["controlList"]
            startPosition = data["startPosition"]
            startAngle = data["startAngle"]
            startSpeed = data["startSpeed"]
            self.car.reset_position = startPosition
            self.car.reset_orientation = (0, startAngle, 0)
            self.car.reset_speed = startSpeed
            self.car.reset_car()
            self.simulating = True
            # Sync of last sensing
            self.last_sensing = time.time()
            self.simuIndex = 0
            self.simuResult = []
            while self.simulating:
                sleep(0.25)
            return jsonify({"result": self.simuResult}), 200

    def simulateGA(
        self,
    ):
        if time.time() - self.last_sensing >= self.sensing_period:
            # Here we need to run next control and save position
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
            pass

    def update(self):
        if self.simulating:
            self.simulateGA()
        else:
            # self.update_network()
            self.process_remote_commands()
            self.updateScrenshot()

    def updateScrenshot(self):
        if self.car is None:
            return
        if time.time() - self.last_sensing >= self.sensing_period:
            tex = base.win.getDisplayRegion(0).getScreenshot()
            self.texYSize = tex.getYSize()
            self.texXSize = tex.getXSize()
            arr = tex.getRamImageAs("RGB")
            data = np.frombuffer(arr, np.uint8)
            self.lastScreenshot = data
            self.last_sensing = time.time()

    def get_sensing_data(self):
        current_controls = (held_keys['w'] or held_keys["up arrow"],
                            held_keys['s'] or held_keys["down arrow"],
                            held_keys['a'] or held_keys["left arrow"],
                            held_keys['d'] or held_keys["right arrow"])
        car_position = self.car.world_position
        car_speed = self.car.speed
        car_angle = self.car.rotation_y
        raycast_distances = self.car.multiray_sensor.collect_sensor_values()
        return {'up': current_controls[0],
                'down': current_controls[1],
                'left': current_controls[2], 
                'right': current_controls[3],
                'car_position x': car_position[0],
                'car_position y': car_position[1],
                'car_position z': car_position[2],
                'car_speed': car_speed,
                'car_angle': car_angle,
                'raycast_distances 0': raycast_distances[0],
                'raycast_distances 1': raycast_distances[1],
                'raycast_distances 2': raycast_distances[2],
                'raycast_distances 3': raycast_distances[3],
                'raycast_distances 4': raycast_distances[4],
                'raycast_distances 5': raycast_distances[5],
                'raycast_distances 6': raycast_distances[6],
                'raycast_distances 7': raycast_distances[7],
                'raycast_distances 8': raycast_distances[8],
                'raycast_distances 9': raycast_distances[9],
                'raycast_distances 10': raycast_distances[10],
                'raycast_distances 11': raycast_distances[11],
                'raycast_distances 12': raycast_distances[12],
                'raycast_distances 13': raycast_distances[13],
                'raycast_distances 14': raycast_distances[14]
                }

    def process_remote_commands(self):
        if self.car is None:
            return

        while len(self.client_commands) > 0:
            try:
                commands = self.client_commands.parse_next_command()
                print("Processing command", commands)
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
                    print("received release all command")
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
                self.connected_client.close()
                self.connected_client = None

    def update_network(self):
        if self.connected_client is not None:
            data = []
            try:
                while True:
                    recv_data = self.connected_client.recv(1024)

                    # received nothing
                    if len(recv_data) == 0:
                        break
                    self.client_commands.add(recv_data)

            except Exception as e:
                printv(e)

        #   No controller connected
        else:
            if self.listen_socket is None:
                self.open_connection_socket()
            try:
                inc_client, address = self.listen_socket.accept()
                print("Controller connecting from " + str(address))
                self.connected_client = inc_client
                # self.connected_client.setblocking(False)
                self.connected_client.settimeout(0.01)

                #   Close listen socket
                self.listen_socket.close()
                self.listen_socket = None
            except Exception as e:
                printv(e)

    def open_connection_socket(self):
        print("Waiting for connections")
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind((self.ip_address, self.port))
        # self.listen_socket.setblocking(False)
        self.listen_socket.settimeout(0.01)
        self.listen_socket.listen()
