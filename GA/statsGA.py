import os
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from conversions import Convertion
import numpy as np

class StatsGA(): 
    def __init__(self, folder):
        conv = Convertion(folder)
        self.fitnessValues = conv.readFitnessValues()
        self.baseFolder = f"./GA/ga_data/{folder}/graphs/"

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
        bestScores = []
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


for f in [f"ga_{i}" for i in range(0, 7)]:
    stat = StatsGA(f)
    stat.getGetNumberEndedSim()
    stat.getNumOfNotEndedSim()
    stat.getBestScores()
