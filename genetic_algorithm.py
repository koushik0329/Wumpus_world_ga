from chromosome import Chromosome
import random

class GeneticAlgorithm:
    def __init__(self, environment, pop_size=50, mutation_rate=0.05):
        self.env = environment
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.population = [Chromosome() for _ in range(pop_size)]

    def fitness(self, chromosome):
        # Simulate agent behavior and return score (mocked here)
        score = 0
        gold_collected = False
        for action in chromosome.actions:
            if action == 'Grab' and not gold_collected:
                score += 100
                gold_collected = True
            elif action == 'MoveForward':
                score += 1
        return score

    def select(self):
        sorted_pop = sorted(self.population, key=self.fitness, reverse=True)
        return sorted_pop[:2]

    def evolve(self, generations=100):
        for _ in range(generations):
            parents = self.select()
            new_population = parents[:]
            while len(new_population) < self.pop_size:
                c1, c2 = parents[0].crossover(parents[1])
                c1.mutate(self.mutation_rate)
                c2.mutate(self.mutation_rate)
                new_population += [c1, c2]
            self.population = new_population[:self.pop_size]
