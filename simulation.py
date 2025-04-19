from environment import WumpusWorld
from genetic_algorithm import GeneticAlgorithm

def run_simulation():
    world = WumpusWorld(size=4)
    ga = GeneticAlgorithm(world)
    ga.evolve(generations=50)

    best = max(ga.population, key=ga.fitness)
    print("Best Action Sequence:", best.actions)
