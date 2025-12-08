import random
import numpy as np
from deap import base, creator, tools, algorithms
from population import init_population 
from utils_ae import save_generated_images, visualize_results
import tools

#INITIALIZATION:
creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()

w0 = init_population.get_nth_init_population(0)

pertubation + 0.1
init_individual(w0, pertubation)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", fitness.fitness_function)
toolbox.register("mate", tools.csBlend, alpha = 0.2)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selNSGA2)

def main():
    N = 250
    MU = 100
    CX_PROB = 0.9
    MUTATION_PROB = 0.1 

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    pop = toolbox.population(n=MU)
    pareto_front = tools.ParetoFront()

    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    
    pop = toolbox.select(pop, len(pop))
    
    pareto_front.update(pop)
    for gen in range(1, NGEN):
        # Select and clone
        offspring = tools.selTournamentDCD(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]
        
        # Crossover
        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)
                del ind1.fitness.values, ind2.fitness.values
        
        # Mutation 
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        
        # Evaluate
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        # Select next generation 
        pop = toolbox.select(pop + offspring, MU)
        pareto_front.update(pop)
    
    return pop, logbook, pareto_front

if __name__ == "__main__":
    pop, logbook, pareto_front = main(seed=42)
    
    utils_ae.visualize_results(pareto_front, logbook)

    utils_ae.save_generated_images(pareto_front, stylegan)
    
    import pickle
    with open('results/final_results.pkl', 'wb') as f:
        pickle.dump({
            'population': pop,
            'logbook': logbook,
            'pareto_front': pareto_front
        }, f)
    