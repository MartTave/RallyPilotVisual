from time import sleep
import docker



client = docker.from_env()

image_name = "app"  
try:
    client.images.get(image_name)
except docker.errors.ImageNotFound:
    print(f"Image {image_name} not found locally, pulling from Docker Hub...")
    client.images.pull(image_name)

container = client.containers.run(
    image_name,       
    detach=True,     
    ports={'5000/tcp': 5005},  
)

print(f"Container {container.name} is running")


logs = container.logs()
container.reload()
print(logs.decode("utf-8"))
container_info = container.attrs
ports = container_info.get('NetworkSettings', {}).get('Ports', {})
print(ports)
sleep(10)  

print(f"Stopping container {container.name}...")
container.stop()

container.remove()