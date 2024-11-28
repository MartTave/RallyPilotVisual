from rallyrobopilot.remote import Remote
from conversions import Convertion


remote = Remote("http://127.0.0.1", 5000, lambda x: x)

file = Convertion("ga_1")

jsonFile = file.readJson()
controls= file.readResults()
p = remote.getDataForSolution(
    # jsonFile["baseControls"]
    controls["2"],
    (jsonFile["startPoint"]["x"], jsonFile["startPoint"]["y"], jsonFile["startPoint"]["z"]),
    jsonFile["startAngle"],
 
    jsonFile["startVelocity"],
)
