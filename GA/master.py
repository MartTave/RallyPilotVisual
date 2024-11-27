from multiprocessing import Lock
import threading
from time import sleep
import docker

from rallyrobopilot.remote import Remote

def getx(x): 
    return x

class Master:
    def __init__(self, portsRange, isLocal):  
        self.isLocal = isLocal      
        self.ports = {key: True for key in portsRange}
        self.containers = []
        self.remotes = []
        self.free = True
        self.client = docker.from_env()
        print(self.client)
        self.image_name = "app"  
        try:
            self.client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            print(f"Image {self.image_name} not found locally, pulling from Docker Hub...")
            #self.client.images.pull(self.image_name)
        self.availableSimuMax = len(self.ports)
        self.startContainer()
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
    
    def startContainer(self):
        if self.isLocal:
            print("[MASTER] Running in local - Not starting any container")
            return
        for p in self.ports:
            container = self.client.containers.run(
                self.image_name,
                detach=True,
                ports={'5000': p},  
            )
            self.containers.append(container)
        allRunning = False
        while not allRunning:
            allRunning = True
            for c in self.containers:
                if self.client.containers.get(c.attrs["Id"]).attrs["State"]["Running"] == False:
                    allRunning = False
                    print("All container are not started, waiting...")
                    sleep(1)
                    break    
    def stopContainer(self):
        for c in self.containers:
            c.stop()
            c.remove()
    
    def getFreeRemote(self): 
        while True:
            for remoteObj in self.remotes:
                if remoteObj["free"] == True:
                    remoteObj["free"] = False
                    return remoteObj
            sleep(1)
      
    def runSimulation(self, individual, startPoint, angle, speed):
        print("Running simulation")
        remoteObj = self.getFreeRemote()
        positions = remoteObj["remote"].getDataForSolution(individual, startPoint, angle, speed)
        remoteObj["free"] = True
        return positions
    
    def checkFreePorts(self): 
        with self.lock:  # Ensure thread-safe access
            free_ports = sum(1 for value in self.ports.values() if value)
        return free_ports
