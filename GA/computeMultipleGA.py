import csv

from GA.algo_Ga import GaDataGeneration
from GA.conversions import Convertion
class computeMultipleGA():
    def __init__(self):
        pass

    def runSimulations(self):
        pop = []
        controls = [[1,0,0,0] for _ in range(50)]
        dataGa = Convertion().readJsons()
        for i in range(len(dataGa)):
            ga = GaDataGeneration(dataGa[i]["baseControls"],(dataGa[i]['startPoint']['x'],dataGa[i]['startPoint']['z'],dataGa[i]['startPoint']['y']),[(dataGa[i]['endLine']['point1']['x'],dataGa[i]['endLine']['point1']['z'],dataGa[i]['endLine']['point1']['y']),(dataGa[i]['endLine']['point2']['x'],dataGa[i]['endLine']['point2']['z'],dataGa[i]['endLine']['point2']['y'])], dataGa[i]['startAngle'],dataGa[i]['startVelocity'])
            pop = ga.run_ga()
        return pop


test = computeMultipleGA()
test.runSimulations()