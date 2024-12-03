import numpy as np 
import requests
file =  np.zeros((3, 224, 224), dtype=np.uint8)


data = {
    "picture": file.tolist(), 
    "color": [255,0,0]
}

def sendRequest():
    response = requests.post(
            "http://localhost:5000/getPrediction", json=data
        )
    if response.status_code != 200:
        print(
            f"Received error response: {response.status_code} with status"
        )
        return response.status_code
    return response.json()

print(sendRequest())