from cmath import sqrt
import random
from time import sleep
from deap import base, creator, tools
import flask
from rallyrobopilot.remote import Remote
import numpy as np

class GaDataGeneration():
    def __init__(self, controls,startLine, endLine, pop_size=10, ngen=20, mutpb=0.02):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))  
        creator.create("Individual", list, fitness=creator.FitnessMax)
        self.controls = controls
        self.startLine= startLine
        self.endLine = endLine
        self.pop_size = pop_size
        self.ngen = ngen
        self.mutpb = mutpb
        self.endLineA =  (endLine[1][1] - endLine[0][1])/(endLine[0][1] -endLine[0][0])
        self.endLineB = endLine[0][1] - (self.endLineA*endLine[0][0])
        self.positionX = 0.0
        self.positionY = 0.0
            
        
        self.remote =  Remote("http://127.0.0.1", 5000, lambda x: x)
        self.setup_deap()
    
    def setup_deap(self): 
        self.toolbox = base.Toolbox()
        
        self.toolbox.register("attr_controls",  lambda: [random.randint(0, 1) for _ in range(4)])
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_controls, n=100)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        self.toolbox.register("evaluate", self.fitness_fonction) #evaluate allow to create a fitness fonction 
        self.toolbox.register("mate", tools.cxTwoPoint) #allow to choose a method for crossover
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=self.mutpb) # allow the mutation step 
        self.toolbox.register("select", tools.selTournament, tournsize=3) # selectioon for the new population
    
    def computeDistance(self, posX , posY):
        return ((self.endLineA * posX) - (posY + self.endLineB))/(sqrt(pow(self.endLineA,2)+1))
        
    def fitness_fonction(self, individual):
        positionX = 0.0
        positionY = 0.0
        controls = []
        currControlIndex = 0
        notFinished = True
        startDistance = 0
        fitness_value = 0
        def gotNewData(x):
            nonlocal positionX, positionY,controls, currControlIndex, startDistance, notFinished,fitness_value
            currControl = individual[currControlIndex]
            controls = Remote.getControlsFromData(x)
            positionX = x['car_position x']
            positionY = x['car_position z']
            if currControlIndex == 0 : 
                startDistance = self.computeDistance(positionX,positionY)
            self.remote.sendControl(currControl)
            currControlIndex += 1
            if np.sign(startDistance)!= np.sign(self.computeDistance(positionX,positionY)) or currControlIndex== len(controls) :
                self.remote.stopSensing()
                if np.sign(startDistance)!= np.sign(self.computeDistance(positionX,positionY)): 
                    fitness_value = len(controls)
                else: 
                    fitness_value = -1 
                print(fitness_value)
                notFinished = False
        self.remote.startSensing()
        self.remote.cb = gotNewData
        while notFinished:
            sleep(0.5)
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
            print("here")
            individuals =  sorted(population, key=len)
            index_best_individual = len(individuals)
            for i in range(1, len(individuals)):
                if fits[i] != fits[i - 1]:
                    index_best_individual = i
                    break
            best_individuals =  individuals[:index_best_individual]
            #best_guess = ''.join(best_individuals)
            #new pop
            print(best_individuals)
            offspring = list(map(self.toolbox.clone,self.toolbox.select(best_individuals,k=len(population))))
            #crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(child1,child2)
            #mutation
            for individual in offspring:
                self.toolbox.mutate(individual)       
            population[:]=offspring
            fits = list(map(self.toolbox.evaluate, population))
                     

        
test = GaDataGeneration([[1,0,0,0] for n in range(20)], [(-141,-29),(-150,-290)],[(-82,-80),(-82,60)])
test.run_ga()