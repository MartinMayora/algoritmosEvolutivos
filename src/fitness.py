from deap import creator, base

def init_fitness():
    creator.create("FitnessMulti", base.Fitness, wieghts=(-1.0,1.0))


def fitness_function(population):
    