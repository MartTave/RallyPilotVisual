from time import sleep
import docker

from rallyrobopilot.remote import Remote

class Master : 
    def __init__(self, startPoint, angle, speed):
        self.startPoint = startPoint
        self.angle = angle 
        self.speed = speed
        
        self.ports = {key: True for key in range(5000, 5101)}
        
        self.client = docker.from_env()
        self.image_name = "app"  
        try:
            self.client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            print(f"Image {self.image_name} not found locally, pulling from Docker Hub...")
        self.client.images.pull(self.image_name)
    
    def checkFreePorts(self): 
        while True:
            for key, value in self.ports.items():
                if value  == True: 
                    return key
            print("all ports are taken ...")
            sleep(3)
        

    def runSimulation(self,individual):
        port = self.checkFreePorts()
        self.ports[port] = False
        container = self.client.containers.run(
        self.image_name,       
        detach=True,     
        ports={'5000/tcp': port},  
        )
        sleep(5)
        remote =  Remote("http://127.0.0.1", port, lambda x: x)
        positions = remote.getDataForSolution(individual,self.startPoint,self.angle,self.speed)
        print(f"Stopping container {container.name}...")
        container.stop()
        container.remove()
        sleep(1)
        self.ports[port] = True
        return positions
        
    