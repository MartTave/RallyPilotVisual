from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Lock, Pool
import threading
from time import sleep
import docker
from rallyrobopilot.remote import Remote

def getx(x): 
    return x

def log(*args):
    print("[MASTER] ", *args)

class Master:
    def __init__(self, portsRange, isLocal):  
        self.isLocal = isLocal      
        self.ports = {key: True for key in portsRange}
        self.containers = []
        self.remotes = []
        self.free = True

        self.availableSimuMax = len(self.ports)
        if not self.isLocal:
            self.client = docker.from_env()
            self.image_name = "polypode/hes:latest"
            log(f"Pulling {self.image_name} from docker hub")
            self.client.images.pull(self.image_name)
        self.startContainers()
        if not self.isLocal:
            sleep(20)
        self.createRemotes()

    def createRemotes(self):
        for p in self.ports:
            remote = Remote("http://127.0.0.1", p, lambda :'')
            self.remotes.append({
                'remote': remote,
                'free': True
            })

    def startContainers(self):
        if self.isLocal:
            log("Running in local - Not starting any container")
            return
        def startContainer(port):
            env_var = {"TRACK": "SimpleTrack", "FPS": 30}

            container = self.client.containers.run(
                self.image_name,
                detach=True,
                ports={"5000": port},
                environment=env_var,
            )
            sleep(8)
            return container

        log(f"Starting {len(self.ports)} containers")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(startContainer, port) for port in self.ports]
            # Wait for all futures to finish and gather results
            self.containers = [future.result() for future in futures]
        allRunning = False
        while not allRunning:
            allRunning = True
            for c in self.containers:
                if self.client.containers.get(c.attrs["Id"]).attrs["State"]["Running"] == False:
                    allRunning = False
                    log("All container are not started, waiting...")
                    sleep(1)
                    break
        log("Started !")
    def stopContainers(self):
        if self.isLocal:
            return
        def stopContainer(c):
            c.stop()
            c.remove()
            sleep(10)
        log(f"Stopping {len(self.containers)} containers")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(stopContainer, c) for c in self.containers]
            # Wait for all futures to finish and gather results
            [future.result() for future in futures]

    def getFreeRemote(self): 
        while True:
            for remoteObj in self.remotes:
                if remoteObj["free"] == True:
                    remoteObj["free"] = False
                    return remoteObj
            sleep(1)

    def runSimulation(self, individual, startPoint, angle, speed):
        remoteObj = self.getFreeRemote()
        positions = remoteObj["remote"].getDataForSolution(individual, startPoint, angle, speed)
        remoteObj["free"] = True
        return positions

    def checkFreePorts(self): 
        with self.lock:  # Ensure thread-safe access
            free_ports = sum(1 for value in self.ports.values() if value)
        return free_ports
