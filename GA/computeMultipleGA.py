import csv

from GA.algo_Ga import GaDataGeneration
class computeMultipleGA():
    def __init__(self, filePathPos, filePathControls):
        self.filePathPos = filePathPos
        self.filePathControls = filePathControls
    def readCSV(self, path): 
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            lines = list(reader)
            csvfile.close()
        return lines
    def getControls(self): 
        controls = self.readCSV(self.filePathControls)
        for i in range(0,len(controls)):
            controls[i] = [int(value) for value in controls[i]]
        return controls
                
    def runSimulations(self):
        pop = []
        positions = self.readCSV(self.filePathPos)
        controls = self.getControls()
        positions[1:] = [[float(float(value)) for value in row] for row in positions[1:]]
        for i in range(1, len(positions)-1,2):
            group = positions[i:i+2]
            print(group)
            ga = GaDataGeneration(controls,[(group[0][3],group[0][4],group[0][5]),(group[0][6],group[0][7],group[0][8])],[(group[1][3],group[1][4],group[1][5]),(group[1][6],group[1][7],group[1][8])],group[0][9],group[0][10])
            pop = ga.run_ga()
        return pop
        


test = computeMultipleGA( 'positions.csv', './gaData/controls1.csv')
test.runSimulations()