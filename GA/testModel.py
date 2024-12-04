from time import sleep
from GA.computeGAMaths import GaMaths
from rallyrobopilot.remote import Remote
from conversions import Convertion


FOLDERS = range(82, 83)

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
    return p

for f in [f"ga_{i}" for i in FOLDERS]:
    file = Convertion(f)

    jsonFile = file.readJson()
    print("Length base controls : ", len(jsonFile["baseControls"]))
    print("Simulating example for ", f)
    simulate(jsonFile["baseControls"], jsonFile)
    try:
        endLine = [(jsonFile['endLine']['point1']['x'], jsonFile['endLine']['point1']['y'],jsonFile['endLine']['point1']['z']),(jsonFile['endLine']['point2']['x'],jsonFile['endLine']['point2']['y'],jsonFile['endLine']['point2']['z'])]
        pos  = [jsonFile['startPoint']['x'],jsonFile['startPoint']['y'], jsonFile['startPoint']['z']]
        computeMaths = GaMaths(endLine,pos)
        controls = file.readResults()
        print("Simulating results for ", f)
        for c in controls.values():
            positions = simulate(c, jsonFile)
            import ipdb;ipdb.set_trace()
            for i, p in enumerate(positions):
                if computeMaths.isArrivedToEndLine(p[0], p[2]):
                    endLineReached = True
                    print("Length solution : ", i + 1)
                    break
        
    except:
        pass
    print("Done")
    remote.sendControl([0, 0, 0, 0])
    sleep(2)
