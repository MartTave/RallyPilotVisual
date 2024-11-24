from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from math import sqrt
from multiprocessing import Pool
import random
from time import sleep
from GA.computeGAMaths import GaMaths
from GA.master import Master
from deap import base, creator, tools
import flask
from rallyrobopilot.remote import Remote
import numpy as np
import csv
def getx(x):
    return x
def get_first_control(controls):
    return controls[0]

class GaDataGeneration():
    def __init__(self, controls,startPoint, endLine, angle, speed, pop_size=20, ngen=6):
        print(endLine)
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))  
        creator.create("Individual", list, fitness=creator.FitnessMax)
        self.computeMaths = GaMaths(endLine,startPoint)
        self.controls = controls
        self.startPoint = startPoint
        self.endLine = endLine
                
        self.pop_size = pop_size
        self.angle= angle
        self.speed = speed
        self.ngen = ngen
        self.endLineA =  self.computeMaths.endLineA
        self.endLineB = self.computeMaths.endLineB
        self.exampleInd = []    
        self.master = Master(self.startPoint, self.angle, self.speed)  
        self.setup_deap()
    def getInd(self):
        return self.toolbox.clone(self.exampleInd)

    def setup_deap(self): 
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_controls",  get_first_control, controls )
        self.toolbox.register("individual", tools.initRepeat, creator.Individual,  self.toolbox.attr_controls, n=len(self.controls))
        self.exampleInd = self.toolbox.individual()
        for i, c in enumerate(self.controls):
            self.exampleInd[i] = c
       

        self.toolbox.register("population", tools.initRepeat, list, self.getInd)
        
        self.toolbox.register("evaluate", self.fitness_fonction) #evaluate allow to create a fitness fonction 
        self.toolbox.register("mate", tools.cxTwoPoint) #allow to choose a method for crossover
        self.toolbox.register("mutate", self.custom_mutate) # allow the mutation step 
        self.toolbox.register("select", tools.selTournament, tournsize=3) # selectioon for the new population
    def custom_mutate(self,individual, num_flips=1):
        if random.randint(0, 3) != 0:
            return (individual, )
        indices_to_mutate = random.sample(range(len(individual)), min(num_flips, len(individual)))
        for i in indices_to_mutate:
            j = random.randint(0, 3)
            individual[i][j] = 1 if individual[i][j] == 0 else 0
        return (individual,)  
        
    def fitness_fonction(self, individual):
        positions = self.master.runSimulation(individual)
        fitness_value = -1
        for i, p in enumerate(positions):
            if self.computeMaths.isArrivedToEndLine(p[0], p[2]):
                fitness_value = i
                break
        print("Finished in ", fitness_value)
        return (fitness_value,)

    def run_ga(self):
        population = self.toolbox.population(n=self.pop_size)
        offspring = []
        offspring[:] = population
        for individual in offspring:
            self.toolbox.mutate(individual)
        population[:] = offspring
        for generation in range(self.ngen):
            # Calculate fitness values
            print("Length now is : ", len(population))
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.toolbox.evaluate, individual) for individual in population]
        
        # Wait for all futures to finish and gather results
                fits = [future.result() for future in futures]
            for fit, ind in zip(fits, population):
                ind.fitness.values = fit  # Assign fitness values to individuals

            # Zip and sort by fitness values
            paired = list(zip(fits, population))
            paired_sorted = filter(lambda x:x[0][0] != -1, sorted(paired, key=lambda x: x[0][0]))  # Sort by fitness value
            fitness_values_sorted, individuals_sorted = zip(*paired_sorted)
            print(fitness_values_sorted)

            TARGET = 5

            # Getting the length of the third best solution - best equilibrium between genocide and exploration
            targetLength = fitness_values_sorted[TARGET - 1][0]
            genocidResult = []
            for i, ind in enumerate(individuals_sorted):
                individual = creator.Individual(ind[:targetLength])
                individual.fitness.values = ind.fitness.values
                genocidResult.append(individual)
            # Select the best individuals
            best_individuals = genocidResult[:TARGET]
            print(f"For generation : {generation}")
            for b in best_individuals:
                print(f"Best ind got length = {len(b)} and fit : {b.fitness.values[0]}")
            # Create new population
            offspring = list(map(self.toolbox.clone, self.toolbox.select(best_individuals, k=len(population))))
            print("pop len", len(offspring))
            # Apply crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(child1, child2)

            # Apply mutation
            for individual in offspring:
                self.toolbox.mutate(individual)

            population = []
            population = offspring

            # Recalculate fitness
            #fits = list(map(self.toolbox.evaluate, population))

        return population


controls = [[1,0,0,0] for _ in range(250)]              
#ga = GaDataGeneration(controls,(0.0, 0.0, 0.0),[(-166.49599104143704,0.0,74.12973000725437),(-185.91828508160984,0.0,78.90199301520657)],-90.0,0)
#p = ga.run_ga()
