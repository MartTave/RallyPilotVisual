from rallyrobopilot import prepare_game_app, RemoteController
from flask import Flask, request, jsonify
from threading import Thread
from pygame.time import Clock

import logging

logging.getLogger("werkzeug").disabled = True

FRAMERATE = 50

# Setup Flask
flask_app = Flask(__name__)
flask_app.logger.disabled = True
flask_thread = Thread(target=flask_app.run, kwargs={'host': "0.0.0.0", 'port': 5000})
print("Flask server running on port 5000")
flask_thread.start()


app, car = prepare_game_app()
remote_controller = RemoteController(car = car, flask_app=flask_app)
while True:
    app.step()
    Clock().tick(FRAMERATE)
