import csv
from time import sleep

from algo_Ga import GaDataGeneration
from conversions import Convertion
from master import Master
class computeMultipleGA():
    def __init__(self, masters:list[Master], folder_names:list[str]):
        self.masters = masters
        self.folder_names = folder_names
        pass

    def runSimulations(self, ngen=50, patience=15, pop_size=100):
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
    masters = [Master(range(5000, 5100), False)]

    test = computeMultipleGA(masters, [f"ga_{i}" for i in range(8, 13)])
    test.runSimulations()
