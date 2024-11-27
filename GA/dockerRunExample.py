from time import sleep
import docker



client = docker.from_env()

image_name = "app"  
try:
    client.images.get(image_name)
except docker.errors.ImageNotFound:
    print(f"Image {image_name} not found locally, pulling from Docker Hub...")
    client.images.pull(image_name)

container1 = client.containers.run(
    image_name,       
    detach=True,     
    ports={'5000/tcp': 5005},  
)

container2 = client.containers.run(
    image_name,       
    detach=True,     
    ports={'5000/tcp': 5002},  
)

print(f"Container {container1.name} is running")


container1.stop()

container1.remove()

container2.stop()

container2.remove()