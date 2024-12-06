import os
import matplotlib
# matplotlib.use('Agg')

import matplotlib.pyplot as plt
from conversions import Convertion
import numpy as np

class StatsGA(): 
    def __init__(self, folder, track):
        finalFolder = f"{track}/{folder}"
        conv = Convertion(finalFolder)
        self.lenght_controls = len(conv.readJson()["baseControls"])
        self.fitnessValues = conv.readFitnessValues()
        print(self.fitnessValues)
        os.makedirs(f"./GA/ga_data/{finalFolder}/graphs/", exist_ok=True)
        self.baseFolder = f"./GA/ga_data/{finalFolder}/graphs/"

    def getGetNumberEndedSim(self): 
        savePath = f"{self.baseFolder}/hist"
        os.makedirs(savePath, exist_ok=True)
        for i,gen in enumerate(self.fitnessValues):
            plt.figure(figsize=(8, 5))
            plt.hist(gen, bins=range(min(gen), max(gen)+2), color='skyblue', edgecolor='black')
            plt.title(f"Histogram for gen {i}")
            filename = os.path.join(savePath, f"histogram_{i}.png")
            plt.savefig(filename)
            plt.close()

    def getNumOfNotEndedSim(self):
        savePath = f"{self.baseFolder}"
        os.makedirs(savePath, exist_ok=True)
        numNotEndedSim = [int(np.sum(gen == -1)) for gen in self.fitnessValues]
        generations = list(range(len(self.fitnessValues)))  # X-axis: generation numbers
        print(numNotEndedSim, len(generations))
        bin = np.arange(len(generations)+1)
        plt.hist(generations, bins = bin , weights=numNotEndedSim, color='skyblue', edgecolor='black')
        plt.title("Number of Not Ended Simulations Per Generation")
        plt.xlabel("Generation Number")
        plt.ylabel("Number of Not Ended Simulations")
        plt.xlim(left=0)
        filename = os.path.join(savePath, "individuals_killed.png")
        plt.savefig(filename)
        plt.close()
    def getBestScores(self): 
        savePath = f"{self.baseFolder}"
        bestScores = [self.lenght_controls]
        for gen in self.fitnessValues:
            filtered = list(filter(lambda x: x != -1, gen))
            bestScores.append(min(filtered))   
        plt.plot(bestScores)
        plt.title("Best Scores Per Generation")
        plt.xlabel("Generation Number")  
        plt.ylabel("Best Fitness Value") 
        filename = os.path.join(savePath, "fitness_evolution.png")
        plt.savefig(filename)
        plt.close()
    def getMedianScores(self): 
        savePath = f"{self.baseFolder}"
        mean = []
        min_vals = []
        max_vals = []
        bestScores = [self.lenght_controls]
        
        for gen in self.fitnessValues:
            filtered = list(filter(lambda x: x != -1, gen))
            min_vals.append(np.min(filtered))
            max_vals.append(np.max(filtered))
            mean.append(np.mean(np.array(filtered)))
            bestScores.append(min(filtered)) 
        plt.plot(mean, label='Mean')
        plt.plot(bestScores, label='Best Score')
        plt.title("Best Scores and Mean Per Generation")
        plt.xlabel("Generation Number")  
        plt.ylabel("Fitness Values")         
        plt.legend()
        filename = os.path.join(savePath, "median_evolution.png")
        plt.savefig(filename)
        plt.close()

def getDifferenceOfImprovement(minRange, maxRange): 
    savePath = f"./GA/ga_data/simple_track"
    plt.figure()
    for i in range(minRange,maxRange):

        path = f"simple_track/ga_{i}"
        conv = Convertion(path)
        fitnessValues = conv.readFitnessValues()
        start_fitness_value = len(conv.readJson()["baseControls"]) / 10
        diff = [0]
        for j,gen in enumerate(fitnessValues):
            filtered = list(filter(lambda x: x != -1, gen))
            diff.append(start_fitness_value-min(filtered) / 10)
        plt.plot(diff, label=i)
    filename = os.path.join(savePath, "ala2.png")
    plt.title("Seconds Won for each GA")
    plt.xlabel("Generation Number")  
    plt.ylabel("Seconds (s)") 
    plt.savefig(filename)
    plt.close()  
getDifferenceOfImprovement(74, 145)

for f in [f"ga_{i}" for i in range(74, 145)]:
    stat = StatsGA(f, "simple_track")
    # stat.getGetNumberEndedSim()
    # stat.getNumOfNotEndedSim()
    stat.getBestScores()
    stat.getMedianScores()
