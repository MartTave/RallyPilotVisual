import threading
from time import sleep, time
import requests
import numpy as np
from rallyrobopilot.convert_to_bw import convertToBwSingle

class Remote:
    def __init__(self):
        self.images = []
    def getPictures(self): 
        response = requests.post(
            f"{self.host}:{self.port}/picture", json={"picture": self.images}
        )
        if response.status_code != 200:
            print(
                f"Received error response: {response.status_code} with status {response.json()['error']}"
            )
            return False
        return True
