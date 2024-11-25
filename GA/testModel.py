from rallyrobopilot.remote import Remote
from GA.conversions import Convertion


remote = Remote("http://127.0.0.1", 5000, lambda x: x)

jsonFile = Convertion("ga_0").readJson()

p = remote.getDataForSolution(
    jsonFile["baseControls"],
    (jsonFile["startPoint"]["x"], jsonFile["startPoint"]["y"], jsonFile["startPoint"]["z"]),
    jsonFile["startAngle"],
    jsonFile["startVelocity"],
)
