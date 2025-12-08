from deap import base, creator, tools, algorithms
import csv
import random

class load_population(): #GENERAL POPULATION CLASS, NOT THE DEAP ONE (FOR THAT IS INIT_INDVIDUAL)

    def __init__(self, n=20):
        self.population_init = get_init_population_from_csv(n)

    def get_random_population(self, n=20):
        min_value = -1.0
        max_value = 1.0 #MAY NEED TO CHANGE
        random_population = [random.uniform(min_value, max_value) for _ in range(n)]
        return random_population

    def get_nth_init_population(self, n):
        return self.population_init[n]

    def get_init_population_from_csv(self, n, path = '../data/init_population.csv'):
        with open(path, 'r') as file:
            rows = list(csv.reader(file))
        return rows

def init_individual(toolbox, n=10):
    toolbox.register()

