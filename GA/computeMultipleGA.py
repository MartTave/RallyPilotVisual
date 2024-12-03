import csv
import sys
from time import sleep

from algo_Ga import GaDataGeneration
from conversions import Convertion
from master import Master
class computeMultipleGA():
    def __init__(self, masters:list[Master], folder_names:list[str]):
        self.masters = masters
        self.folder_names = folder_names
        pass

    def runSimulations(self, ngen=100, patience=15, pop_size=75):
        for f in self.folder_names:
            conv = Convertion(f)
            jsonData = conv.readJson()
            master = None
            while master is None:
                for m in self.masters:
                    if m.free:
                        master = m
                        break
                print("No masters available... Waiting !")
                sleep(5)

            if conv.hasResults():
                print(f"Results already computed for {f}")
                print(f"Taking result as base controls !")
                prevRes = conv.readResults()
                ga = GaDataGeneration(
                    jsonData,
                    m,
                    pop_size=len(prevRes.keys()),
                    ngen=ngen,
                    patience=patience,
                    previousResults=prevRes,
                )
            else:
                ga = GaDataGeneration(
                    jsonData,
                    m,
                    pop_size=pop_size,
                    ngen=ngen,
                    patience=patience,
                )

            res,fitness_values = ga.run_ga()
            master.free = True
            conv.writeJsonFile(res)
            conv.writeFitnessValues(fitness_values)
        for m in self.masters:
            m.stopContainers()


if __name__ == '__main__':
    portStart = 5000
    portEnd = 5075
    patience = 15
    nGen = 100
    if len(sys.argv) >= 3:
        portStart = int(sys.argv[1])
        portEnd = int(sys.argv[2])

        if len(sys.argv) >= 4:
            nGen = int(sys.argv[3])
            if len(sys.argv) >= 5:
                patience = int(sys.argv[4])

    masters = [Master(range(portStart, portEnd), False)]

    test = computeMultipleGA(masters, [f"ga_{i}" for i in range(0, 74)])
    test.runSimulations(
        pop_size=portStart - portEnd,
        patience=patience,
        ngen=nGen,
    )
