
from fonctions import convertToBwSingle, getDistancesSingle
from model import AlexNetAtHome
import torch
import numpy as np


from flask import Flask, request, jsonify


GRACE_TIME_GA = 1

REMOTE_CONTROLLER_VERBOSE = False
PERIOD_REMOTE_SENSING = 0.1
class Server():

    def __init__(self, flask_app=None):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.lastimage = None
        
        self.model_ml = AlexNetAtHome()
        print("AlexNetModel")
        self.model_ml.load_state_dict(
            torch.load(f"./model/model.pth", map_location=self.device)
        )
        print("model charged")
        self.model_ml = self.model_ml.to(self.device)

        print("model to device", self.device)

        @flask_app.route("/", methods=["GET"])
        def index():
            return "AHHHH"
        
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
flask_app.run(host="0.0.0.0", port=5000)
