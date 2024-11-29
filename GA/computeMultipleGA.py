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

    def runSimulations(self):
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

            ga = GaDataGeneration(jsonData, m, pop_size=12, ngen=10)
            res,fitness_values = ga.run_ga()
            master.free = True
            conv.writeJsonFile(res)
            conv.writeFitnessValues(fitness_values)
        for m in self.masters:
            m.stopContainers()

if __name__ == '__main__':

    masters = [
        Master(range(5000, 5004), False)
    ]
    
    test = computeMultipleGA(masters, ["ga_0"])
    test.runSimulations()
