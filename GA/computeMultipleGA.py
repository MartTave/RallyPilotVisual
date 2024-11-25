import csv
from time import sleep

from GA.algo_Ga import GaDataGeneration
from GA.conversions import Convertion
from GA.master import Master
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
            ga = GaDataGeneration(jsonData, m, pop_size=20, ngen=1)
            res = ga.run_ga()
            conv.writeJsonFile(res)

if __name__ == '__main__':

    masters = [
        Master(range(5000, 5004))
    ]
    
    test = computeMultipleGA(masters, ["ga_0"])
    test.runSimulations()