from rallyrobopilot.remote import Remote
from conversions import Convertion


FOLDERS = [6, 7]

remote = Remote("http://127.0.0.1", 5000, lambda x: x)

def simulate(controls, data):
    p = remote.getDataForSolution(
        controls,
        (
            data["startPoint"]["x"],
            data["startPoint"]["y"],
            data["startPoint"]["z"],
        ),
        data["startAngle"],
        data["startVelocity"],
    )

for f in [f"ga_{i}" for i in FOLDERS]:
    file = Convertion(f)

    jsonFile = file.readJson()
    print("Simulating example !")
    simulate(jsonFile["baseControls"], jsonFile)
    try:
        controls = file.readResults()
        simulate(controls["0"], jsonFile)
    except:
        print("No results found for this folder ", f)
