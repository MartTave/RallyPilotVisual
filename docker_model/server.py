
from time import sleep
import time
from data_tools.getDistance import getDistancesSingle
from model import AlexNetAtHome
from rallyrobopilot.convert_to_bw import convertToBwSingle
from rallyrobopilot.remote_commands import RemoteCommandParser
from ursina import *
import torch
import numpy as np
from pygame.time import Clock


from flask import Flask, request, jsonify

from rallyrobopilot.car import Car

GRACE_TIME_GA = 1

REMOTE_CONTROLLER_VERBOSE = False
PERIOD_REMOTE_SENSING = 0.1
class Server():

    def __init__(self, flask_app=None):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        MODEL_NUMBER = 1
        self.lastimage = None
        
        self.model_ml = AlexNetAtHome()
        self.model_ml.load_state_dict(
            torch.load(f"./models/model_{MODEL_NUMBER}/model.pth", map_location=self.device)
        )

        self.model_ml = self.model_ml.to(self.device)


        
        @flask_app.route("/getPrediction", methods=["POST"])
        def getPrediction():
            data = request.json
            
            if "picture" not in data or "color" not in data:
                return
            CURRENT_COLOR = np.array(data["color"])
            data["picture"]=np.array(data["picture"])

            pic = convertToBwSingle(data["picture"])
            if self.lastimage is None : 
                self.lastimage = pic
                return jsonify({"controls": [0,0,0,0]}), 200
            else:
                x = np.concatenate((AlexNetAtHome.concatTwoPics(self.lastimage, pic), getDistancesSingle(data["picture"], CURRENT_COLOR)[np.newaxis, :, :]), axis=0)
                xTensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(self.device)
                classification = self.model_ml(xTensor)
                probs = torch.sigmoid(classification)
                probList = probs[0].tolist()
                controls = [1 if p > 0.5 else 0 for p in probList]
                self.lastimage = pic
                return jsonify({"controls": controls}), 200
            
            
flask_app = Flask(__name__)
Server(flask_app)
flask_app.run()