from multiprocessing import Lock
import threading
from time import sleep
import docker

from rallyrobopilot.remote import Remote

def getx(x): 
    return x

class Master:
    def __init__(self, startPoint, angle, speed):
        self.startPoint = startPoint
        self.angle = angle
        self.speed = speed
        
        self.ports = {key: True for key in range(5001, 5101)}
        self.lock = threading.Lock()  # Initialize the lock
        
        self.client = docker.from_env()
        print(self.client)
        self.image_name = "app"  
        try:
            self.client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            print(f"Image {self.image_name} not found locally, pulling from Docker Hub...")
            self.client.images.pull(self.image_name)
    
    def getFreePort(self): 
        while True:
            with self.lock:  # Ensure only one thread modifies `self.ports` at a time
                for key, value in self.ports.items():
                    if value:  # Check if the port is free
                        self.ports[key] = False  # Mark the port as taken
                        return key
            print("All ports are taken...")
            sleep(3)
      
    def runSimulation(self, individual):
        port = self.getFreePort()  
        container = self.client.containers.run(
            self.image_name,
            detach=True,
            ports={'5000': port},  
        )
        print(f"Starting container {container.name} on port {port}...")
        sleep(5)
        remote = Remote("http://127.0.0.1", port, getx)
        positions = remote.getDataForSolution(individual, self.startPoint, self.angle, self.speed)
        print(f"Stopping container {container.name} on port {port}...")
        container.stop()
        container.remove()
        sleep(0.5)
        with self.lock:  
            self.ports[port] = True
        return positions
    
    def checkFreePorts(self): 
        with self.lock:  # Ensure thread-safe access
            free_ports = sum(1 for value in self.ports.values() if value)
        return free_ports
        pass
