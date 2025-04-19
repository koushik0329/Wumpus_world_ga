import random
import numpy as np
from chromosome import Chromosome  # Import the Chromosome class

class GeneticAlgorithm:
    def __init__(self, environment, pop_size=50, mutation_rate=0.05, selection_strategy='tournament'):
        self.env = environment
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.selection_strategy = selection_strategy
        self.population = [Chromosome() for _ in range(pop_size)]
        self.fitness_history = []
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.std_fitness_history = []

    def fitness(self, chromosome):
        self.env.reset()  # Reset environment for each evaluation
        score = 0
        gold_collected = False
        for action in chromosome.actions:
            result = self.env.move_agent(action)
            if result == 'gold':
                score += 1000
                gold_collected = True
            elif action == 'MoveForward':
                score += 1
            elif action == 'Shoot':
                score -= 10
            percepts = self.env.get_percepts(*self.env.agent_pos)
            if 'breeze' in percepts or 'stench' in percepts:
                score -= 5
            if 'P' in self.env.grid[self.env.agent_pos[0]][self.env.agent_pos[1]]:
                score -= 100  # Penalty for falling into a pit
            if 'W' in self.env.grid[self.env.agent_pos[0]][self.env.agent_pos[1]]:
                score -= 50  # Penalty for encountering the Wumpus
        return score

    def select(self):
        if self.selection_strategy == 'tournament':
            return [self.tournament_selection() for _ in range(2)]
        elif self.selection_strategy == 'rank':
            return self.rank_selection()
        elif self.selection_strategy == 'elitist':
            return self.elitist_selection()
        else:
            raise ValueError("Unknown selection strategy")

    def tournament_selection(self, tournament_size=3):
        tournament = random.sample(self.population, tournament_size)
        tournament.sort(key=self.fitness, reverse=True)
        return tournament[0]

    def rank_selection(self):
        ranked_population = sorted(self.population, key=self.fitness, reverse=True)
        rank_sum = sum(range(1, len(ranked_population) + 1))
        rank_probabilities = [(len(ranked_population) - i) / rank_sum for i in range(len(ranked_population))]
        selected = random.choices(ranked_population, weights=rank_probabilities, k=2)
        return selected

    def elitist_selection(self):
        sorted_population = sorted(self.population, key=self.fitness, reverse=True)
        return sorted_population[:2]

    def evolve(self, generations=100):
        for gen in range(generations):
            parents = self.select()
            new_population = parents[:]
            while len(new_population) < self.pop_size:
                c1, c2 = parents[0].crossover(parents[1])
                c1.mutate(self.mutation_rate)
                c2.mutate(self.mutation_rate)
                new_population += [c1, c2]
            self.population = new_population[:self.pop_size]

            # Collect fitness data
            fitness_scores = [self.fitness(chromosome) for chromosome in self.population]
            best_fitness = max(fitness_scores)
            avg_fitness = np.mean(fitness_scores)
            std_fitness = np.std(fitness_scores)

            self.fitness_history.append(fitness_scores)
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            self.std_fitness_history.append(std_fitness)

    def get_statistical_summaries(self):
        return {
            'best_fitness': self.best_fitness_history,
            'avg_fitness': self.avg_fitness_history,
            'std_fitness': self.std_fitness_history
        }
