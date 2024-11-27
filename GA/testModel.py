from rallyrobopilot.remote import Remote
from conversions import Convertion


remote = Remote("http://127.0.0.1", 5000, lambda x: x)

jsonFile = Convertion("ga_0").readJson()
controls= Convertion("ga_0").readResults()
p = remote.getDataForSolution(
    controls["0"],
    (jsonFile["startPoint"]["x"], jsonFile["startPoint"]["y"], jsonFile["startPoint"]["z"]),
    jsonFile["startAngle"],
 
    jsonFile["startVelocity"],
)
