import random
import numpy as np
from chromosome import Chromosome

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
        self.env.reset()
        score = 0
        gold_collected = False
        wumpus_killed = False
        
        for action in chromosome.actions:
            result = self.env.move_agent(action)
            
            if result == 'death':
                score -= 1000
                break
            elif result == 'gold_collected':
                score += 1000
                gold_collected = True
            elif result == 'wumpus_killed':
                score += 500
                wumpus_killed = True
                
            # Small rewards/penalties
            if action == 'MoveForward':
                score += 1
            elif action == 'Shoot':
                score -= 10
                
            # Percept-based adjustments
            percepts = self.env.get_percepts(*self.env.agent_pos)
            if 'breeze' in percepts:
                score -= 5
            if 'stench' in percepts:
                score -= 5
                
        # Bonus for efficiency
        if gold_collected:
            score += 100 - len(chromosome.actions)  # Shorter paths get higher bonus
            
        return score

    def select(self):
        if self.selection_strategy == 'tournament':
            return self.tournament_selection()
        elif self.selection_strategy == 'rank':
            return self.rank_selection()
        elif self.selection_strategy == 'elitist':
            return self.elitist_selection()

    def tournament_selection(self, tournament_size=3):
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=lambda x: self.fitness(x))

    def rank_selection(self):
        ranked = sorted(self.population, key=lambda x: self.fitness(x))
        weights = [i for i in range(1, len(ranked)+1)]
        return random.choices(ranked, weights=weights, k=2)

    def elitist_selection(self):
        sorted_pop = sorted(self.population, key=lambda x: self.fitness(x), reverse=True)
        return sorted_pop[:2]

    def evolve(self, generations=100):
        for gen in range(generations):
            # Selection
            parents = self.select()
            
            # Create new population
            new_pop = parents.copy()
            while len(new_pop) < self.pop_size:
                child1, child2 = parents[0].crossover(parents[1])
                child1.mutate(self.mutation_rate)
                child2.mutate(self.mutation_rate)
                new_pop.extend([child1, child2])
                
            self.population = new_pop[:self.pop_size]
            
            # Record stats
            fitness_scores = [self.fitness(chrom) for chrom in self.population]
            self.fitness_history.append(fitness_scores)
            self.best_fitness_history.append(max(fitness_scores))
            self.avg_fitness_history.append(np.mean(fitness_scores))
            self.std_fitness_history.append(np.std(fitness_scores))
            
            print(f"Generation {gen}: Best = {max(fitness_scores)}, Avg = {np.mean(fitness_scores)}")