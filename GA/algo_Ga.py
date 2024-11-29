from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from math import sqrt
from multiprocessing import Pool
import random
from computeGAMaths import GaMaths
from master import Master
from deap import base, creator, tools
import flask
from rallyrobopilot.remote import Remote
import numpy as np
import csv
def getx(x):
    return x
def get_first_control(controls):
    return controls[0]


def log(*args):
    print("[GA] ", *args)

class GaDataGeneration():
    def __init__(self, jsonData, master: Master, pop_size=20, ngen=6, patience=15):        
        self.fitness_values = []

        self.parseJsonData(jsonData)
        self.patience = patience        
        self.pop_size = pop_size
        self.ngen = ngen
        self.exampleInd = []
        self.master = master
        self.master.free = False
        self.setup_deap()

    def parseJsonData(self, jsonData):
        self.controls = jsonData["baseControls"]
        self.startPoint = (
            jsonData["startPoint"]["x"],
            jsonData["startPoint"]["y"],
            jsonData["startPoint"]["z"],
        )
        self.endLine = [
            (
                jsonData["endLine"][x]['x'],
                jsonData["endLine"][x]['y'],
                jsonData["endLine"][x]['z'],
            )
            for x in ["point1", "point2"]
        ]
        self.computeMaths = GaMaths(self.endLine,self.startPoint)
        self.angle = jsonData["startAngle"]
        self.speed = jsonData["startVelocity"]

    def getInd(self):
        return self.toolbox.clone(self.exampleInd)

    def setup_deap(self): 
        self.toolbox = base.Toolbox()
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self.toolbox.register("attr_controls",  get_first_control, controls )
        self.toolbox.register("individual", tools.initRepeat, creator.Individual,  self.toolbox.attr_controls, n=len(self.controls))
        self.exampleInd = self.toolbox.individual()
        for i, c in enumerate(self.controls):
            self.exampleInd[i] = c

        self.toolbox.register("takeBest", tools.selBest)
        self.toolbox.register("population", tools.initRepeat, list, self.getInd)

        self.toolbox.register("evaluate", self.fitness_fonction) #evaluate allow to create a fitness fonction 
        self.toolbox.register("mate", tools.cxTwoPoint) #allow to choose a method for crossover
        self.toolbox.register("mutate", self.custom_mutate) # allow the mutation step 
        self.toolbox.register("select", tools.selTournament, tournsize=3) # selectioon for the new population
    def custom_mutate(self,individual, num_flips=random.randint(2, 5)):
        if random.randint(0, 1) == 0:
            return (individual,)
        indices_to_mutate = random.sample(range(len(individual)), min(num_flips, len(individual)))
        for i in indices_to_mutate:
            j = random.randint(0, 3)
            individual[i][j] = 1 if individual[i][j] == 0 else 0
        return (individual,)  

    def fitness_fonction(self, individual):
        positions = self.master.runSimulation(individual, self.startPoint, self.angle, self.speed)
        fitness_value = -1
        for i, p in enumerate(positions):
            if self.computeMaths.isArrivedToEndLine(p[0], p[2]):
                fitness_value = i
                break
        return (fitness_value,)

    def run_ga(self):
        population = self.toolbox.population(n=self.pop_size)
        offspring = []
        offspring[:] = population
        for individual in offspring:
            self.toolbox.mutate(individual)
        population[:] = offspring
        currBestScore = -1
        currPatience = 0
        for generation in range(self.ngen):
            # Calculate fitness values
            pool = 0 
            if self.master.isLocal : 
                pool = 1 
            else: 
                pool = self.master.availableSimuMax
            with ThreadPoolExecutor(max_workers= pool) as executor:
                futures = [executor.submit(self.toolbox.evaluate, individual) for individual in population]
                # Wait for all futures to finish and gather results
                fits = [future.result() for future in futures]
            for fit, ind in zip(fits, population):
                ind.fitness.values = fit  # Assign fitness values to individuals

            # Save fitness values for plotting
            self.fitness_values.append([x[0] for x in fits])

            # Sort by fitness values
            pop_filtered = filter(lambda x:x[1][0] != -1, zip(population, fits))  # Sort by fitness value

            pop_filtered_fitness = []

            for t in pop_filtered:
                ind = creator.Individual(t[0])
                ind.fitness.values = t[1]
                pop_filtered_fitness.append(ind)

            ELITE_SIZE = 5

            elites = self.toolbox.takeBest(pop_filtered_fitness, k=ELITE_SIZE)

            # Don't crossover/mutate if it's the last gen !
            if generation == self.ngen -1:
                continue

            # Create new population with tournament selection
            offspring = list(map(self.toolbox.clone, self.toolbox.select(pop_filtered_fitness, k=len(population) - ELITE_SIZE)))
            # Apply crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(child1, child2)

            # Apply mutation
            for individual in offspring:
                self.toolbox.mutate(individual)

            # Truncating all population to longest one of them
            max_length = max([len(ind) for ind in offspring])
            max_score = min([ind.fitness.values[0] for ind in elites])
            if currBestScore == -1:
                currBestScore = max_score
            if max_score == currBestScore:
                currPatience += 1
            if max_score < currBestScore:
                currBestScore = max_score
                currPatience = 0
            if max_score > currBestScore:
                log("Best score increased ! ", currBestScore, " -> ", max_score)
                currBestScore = max_score
            if currPatience == self.patience:
                log("Early stopping at generation ", generation)
                break
            # Getting the length of the third best solution - best equilibrium between genocide and exploration
            population = [x for x in elites]
            for ind in offspring:
                individual = creator.Individual(ind[:max_length])
                population.append(individual)
            log("")
            log("=====================================")
            log("Generation : ", generation + 1, "/", self.ngen)
            log("Best score is : ", max_score, " from ", len(self.controls))
            log("Current patience is : ", currPatience, "/", self.patience)
            log("DNF count : ", self.pop_size - len(pop_filtered_fitness))
            log("Fitness values for elites : ", [x.fitness.values[0] for x in elites])
            log("=====================================")
            log("")

        best_individuals = sorted(population, key=lambda x: x.fitness.values[0], reverse=True)
        return best_individuals, self.fitness_values


controls = [[1,0,0,0] for _ in range(250)]              
# ga = GaDataGeneration(controls,(0.0, 0.0, 0.0),[(-166.49599104143704,0.0,74.12973000725437),(-185.91828508160984,0.0,78.90199301520657)],-90.0,0)
# p = ga.run_ga()
