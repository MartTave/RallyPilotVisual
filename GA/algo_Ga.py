from math import sqrt
import random
from time import sleep
from deap import base, creator, tools
import flask
from rallyrobopilot.remote import Remote
import numpy as np

class GaDataGeneration():
    def __init__(self, controls,startPoint, endLine, angle, speed, pop_size=10, ngen=20):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))  
        creator.create("Individual", list, fitness=creator.FitnessMax)
        self.controls = controls
        self.startPoint = startPoint
        self.endLine = endLine
        self.pop_size = pop_size
        self.angle= angle
        self.speed = speed
        self.ngen = ngen
        self.endLineA =  (endLine[1][2] - endLine[0][2])/(endLine[1][2] -endLine[0][0])
        self.endLineB = endLine[0][2] - (self.endLineA*endLine[0][0])
                
        self.remote =  Remote("http://127.0.0.1", 5000, lambda x: x)
        self.setup_deap()
    
    def setup_deap(self): 
        self.toolbox = base.Toolbox()
        
        self.toolbox.register("attr_controls",  lambda: [1, 0, 0 ,0])
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_controls, n=len(self.controls))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        self.toolbox.register("evaluate", self.fitness_fonction) #evaluate allow to create a fitness fonction 
        self.toolbox.register("mate", tools.cxTwoPoint) #allow to choose a method for crossover
        self.toolbox.register("mutate", self.custom_mutate) # allow the mutation step 
        self.toolbox.register("select", tools.selTournament, tournsize=3) # selectioon for the new population
    def custom_mutate(self,individual, num_flips=3):
        indices_to_mutate = random.sample(range(len(individual)), min(num_flips, len(individual)))
    
        for i in indices_to_mutate:
            j = random.randint(0, 3)
            individual[i][j] = 1 if individual[i][j] == 0 else 0
        print(individual)
        return (individual,)  
    
    def computeDistance(self, posX , posY):
        A = self.endLineA
        B = -1
        C = self.endLineB
        return A * posX + B * posY + C / sqrt(A**2 + B**2)
        
    def fitness_fonction(self, individual):
        positions = self.remote.getDataForSolution(individual, self.startPoint, self.angle, self.speed)
        initialDistance = self.computeDistance(self.startPoint[0], self.startPoint[2])
        fitness_value = -1

        for p in range(0, len(positions)):
            if np.sign(self.computeDistance(positions[p][0],positions[p][2]))!= np.sign(initialDistance): 
                fitness_value = len(individual)
                break 
        print(fitness_value)
        return (fitness_value,)

    def run_ga(self):
        population = self.toolbox.population(n=self.pop_size)
        for generation in range (self.ngen):
            print(population) 
            # calculate fitness value
            fits = list(map(self.toolbox.evaluate, population))
            for fit, ind in zip(fits, population):
                ind.fitness.values = fit
            # select the best individual according with fitness value
            individuals =  sorted(population, key=len)
            index_best_individual = len(individuals)
            for i in range(1, len(individuals)):
                if fits[i] != fits[i - 1]:
                    index_best_individual = i
                    break
            print("best ind")
            best_individuals =  individuals[:index_best_individual]
            #new pop
            offspring = list(map(self.toolbox.clone,self.toolbox.select(best_individuals,k=len(population))))
            #crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(child1,child2)
            #mutation
            for individual in offspring:
                self.toolbox.mutate(individual)
            print(individual)
            population[:]=offspring
            fits = list(map(self.toolbox.evaluate, population))
        return population
                     

        
test = GaDataGeneration([[1,0,0,0] for n in range(50)],(10, 0, 0),[(70,0,-10),(70,0,11)],90,15)
pop = test.run_ga()