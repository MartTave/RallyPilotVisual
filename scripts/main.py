import os
import sys
from rallyrobopilot import prepare_game_app, RemoteController
from flask import Flask, request, jsonify
from threading import Thread
from pygame.time import Clock

import logging
from rallyrobopilot.time_manager import Time
from rallyrobopilot.args_parser import parseArgs


time: Time

if os.environ.get("FPS") is not None:
    time = Time(realTime=False, fps=int(os.environ.get("FPS")), dt=0.1)
elif len(sys.argv) > 1:
    args = parseArgs(sys.argv[1:])
    if args is None:
        sys.exit(0)
    time = Time(
        realTime=args.get("realTime", False),
        dt=args.get("time", None),
        fps=args.get("framerate", None),
    )
else:
    time = Time(realTime=False)


logging.getLogger("werkzeug").disabled = True

FRAMERATE = 50

# Setup Flask
flask_app = Flask(__name__)
flask_app.logger.disabled = True
flask_thread = Thread(target=flask_app.run, kwargs={"host": "0.0.0.0", "port": 5000})
print("Flask server running on port 5000")
flask_thread.start()


app, car = prepare_game_app(time)
remote_controller = RemoteController(car = car, flask_app=flask_app)

if time.fps > 0:
    while True:
        app.step()
        Clock().tick(time.fps)
else:
    while True:
        app.step()
