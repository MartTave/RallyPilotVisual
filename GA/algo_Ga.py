import random
from deap import base, creator, tools
import flask

class GaDataGeneration():
    def __init__(self, controls,startLine, endLine, pop_size=20, ngen=20, mutpb=0.02):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))  
        creator.create("Individual", list, fitness=creator.FitnessMax)
        self.controls = controls
        self.startLine= startLine
        self.endLine = endLine
        self.pop_size = pop_size
        self.ngen = ngen
        self.mutpb = mutpb
        self.setup_deap()
    
    def setup_deap(self): 
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_controls", lambda: random.sample(self.controls, len(self.controls)))
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_controls, n=self.ngen)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        self.toolbox.register("evaluate", self.fitness_fonction) #evaluate allow to create a fitness fonction 
        self.toolbox.register("mate", tools.cxTwoPoint) #allow to choose a method for crossover
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=self.mutpb) # allow the mutation step 
        self.toolbox.register("select", tools.selTournament, tournsize=3) # selectioon for the new population
        
    def fitness_fonction(self, individual):
        return (20,)

    def run_ga(self):
        population = self.toolbox.population(n=self.pop_size)
        
        for generation in range (self.ngen): 
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
            best_individuals =  individuals[:index_best_individual]
            #best_guess = ''.join(best_individuals)
            #new pop
            offspring = list(map(self.toolbox.clone,self.toolbox.select(best_individuals,k=len(population))))
            #crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(child1,child2)
            #mutation
            for individual in offspring:
                self.toolbox.mutate(individual)       
            population[:]=offspring
            fits = list(map(self.toolbox.evaluate, population))
            print(population)
                     

        
test = GaDataGeneration([[0,0,0,1], [0,0,0,0],[1,0,0,0]], [(0,0),(0,20)],[(1,30),(1,60)])
test.run_ga()