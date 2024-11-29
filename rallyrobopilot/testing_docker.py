from rallyrobopilot.remote import Remote
from GA.conversions import Convertion
import matplotlib.pyplot as plt


jsonFile = Convertion("ga_4").readJson()


def newData(data):
    pass

remote = Remote("http://127.0.0.1", 5000, newData, False)

TRIES = 20

target = len(jsonFile["baseControls"]) - 1


results = []

for i in range(TRIES):
    res = remote.getDataForSolution(
        jsonFile["baseControls"],
        (jsonFile["startPoint"]["x"], jsonFile["startPoint"]["y"], jsonFile["startPoint"]["z"]),
        jsonFile["startAngle"],
    
        jsonFile["startVelocity"],
    )
    results.append(res[target])

x = [i[0] for i in results]
z = [i[2] for i in results]


plt.figure()
plt.plot(x)
plt.savefig("x.png")
plt.figure()
plt.plot(z)
plt.savefig("z.png")