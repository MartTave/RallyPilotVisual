from model import pretrained
import torch

from rallyrobopilot.remote import Remote

MODEL_NUMBER = 0


BASE_PATH = "../models/"
FILENAME = "model.pth"
FULL_PATH = f"{BASE_PATH}model_{MODEL_NUMBER}/{FILENAME}"

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


pretrained.load_state_dict(torch.load(FULL_PATH), map_location=DEVICE)


def pilot(newData):

    pass


remote = Remote("127.0.0.1", 5000, pilot)
print("Press enter to quit...")
input()
