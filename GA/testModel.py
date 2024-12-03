from time import sleep
from rallyrobopilot.remote import Remote
from conversions import Convertion


FOLDERS = range(8, 9)

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
    print("Simulating example for ", f)
    simulate(jsonFile["baseControls"], jsonFile)
    try:
        controls = file.readResults()
        print("Simulating results for ", f)
        simulate(controls["0"], jsonFile)
    except:
        pass
    print("Done")
    remote.sendControl([0, 0, 0, 0])
    sleep(2)
