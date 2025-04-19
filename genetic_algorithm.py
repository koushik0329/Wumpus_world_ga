import random
import numpy as np
from chromosome import Chromosome  # Import the Chromosome class

class GeneticAlgorithm:
    def __init__(self, environment, pop_size=50, mutation_rate=0.05, selection_strategy='tournament', chromosome_length=30):
        """Initialize the Genetic Algorithm with the given parameters.
        
        Args:
            environment: The WumpusWorld environment.
            pop_size: The population size.
            mutation_rate: The mutation rate.
            selection_strategy: The selection strategy ('tournament', 'rank', or 'elitist').
            chromosome_length: The length of each chromosome's action sequence.
        """
        self.env = environment
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.selection_strategy = selection_strategy
        self.chromosome_length = chromosome_length
        self.population = [Chromosome(length=chromosome_length) for _ in range(pop_size)]
        self.fitness_history = []
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.std_fitness_history = []
        self.success_rate_history = []

    def fitness(self, chromosome):
        """Calculate the fitness of a chromosome.
        
        The fitness function prioritizes:
        1. Gold retrieval and successful exit
        2. Agent survival
        3. Efficient path length
        4. Effective use of the arrow to kill the Wumpus
        
        Args:
            chromosome: The chromosome to evaluate.
            
        Returns:
            The fitness score.
        """
        self.env.reset()  # Reset environment for each evaluation
        score = 0
        
        # Execute each action in the chromosome
        for action in chromosome.actions:
            result = self.env.move_agent(action)
            
            # Add a small movement cost
            if action == 'MoveForward':
                score += 1  # Small reward for moving (exploring)
            
            # Check if we got gold
            if result == 'gold':
                score += 1000  # Major reward for finding gold
            
            # Add extra reward if the agent killed the Wumpus
            if result == 'scream':
                score += 200  # Good reward for killing Wumpus
            
            # Penalize heavily for death
            if result == 'pit' or result == 'wumpus':
                score -= 1000  # Huge penalty for dying
                break
                
            # Extra reward for successfully exiting with gold
            if result == 'win':
                score += 2000  # Massive reward for complete success
                break
                
            # Add penalties for being in dangerous situations
            percepts = self.env.get_percepts(*self.env.agent_pos)
            if 'breeze' in percepts or 'stench' in percepts:
                score -= 5  # Small penalty for being in danger
        
        # Add final position score based on:
        # 1. If agent has gold - reward for being close to exit (0,0)
        # 2. If agent doesn't have gold - reward for being close to gold
        if self.env.has_gold:
            # Distance to exit point (0,0) - reward for being closer
            exit_dist = abs(self.env.agent_pos[0]) + abs(self.env.agent_pos[1])
            score += 100 * (1.0 / (exit_dist + 1))  # Inversely proportional to distance
        elif self.env.gold_pos:
            # Distance to gold - reward for being closer
            gold_dist = abs(self.env.agent_pos[0] - self.env.gold_pos[0]) + abs(self.env.agent_pos[1] - self.env.gold_pos[1])
            score += 50 * (1.0 / (gold_dist + 1))  # Inversely proportional to distance
        
        # Reward for staying alive
        score += 100  # Base survival bonus
        
        # Add score from the environment
        score += self.env.score
        
        return score

    def select(self):
        """Select chromosomes for reproduction based on the selected strategy.
        
        Returns:
            A list of selected chromosomes.
        """
        if self.selection_strategy == 'tournament':
            return [self.tournament_selection() for _ in range(2)]
        elif self.selection_strategy == 'rank':
            return self.rank_selection()
        elif self.selection_strategy == 'elitist':
            return self.elitist_selection()
        else:
            raise ValueError("Unknown selection strategy")

    def tournament_selection(self, tournament_size=3):
        """Select a chromosome using tournament selection.
        
        Args:
            tournament_size: The size of the tournament.
            
        Returns:
            The selected chromosome.
        """
        tournament = random.sample(self.population, tournament_size)
        tournament.sort(key=self.fitness, reverse=True)
        return tournament[0]

    def rank_selection(self):
        """Select two chromosomes using rank-based selection.
        
        Returns:
            A list of two selected chromosomes.
        """
        ranked_population = sorted(self.population, key=self.fitness, reverse=True)
        rank_sum = sum(range(1, len(ranked_population) + 1))
        rank_probabilities = [(len(ranked_population) - i) / rank_sum for i in range(len(ranked_population))]
        selected = random.choices(ranked_population, weights=rank_probabilities, k=2)
        return selected

    def elitist_selection(self):
        """Select the two best chromosomes.
        
        Returns:
            A list of the two best chromosomes.
        """
        sorted_population = sorted(self.population, key=self.fitness, reverse=True)
        return sorted_population[:2]

    def evolve(self, generations=100):
        """Evolve the population for the given number of generations.
        
        Args:
            generations: The number of generations to evolve.
        """
        for gen in range(generations):
            # Select parents
            parents = self.select()
            
            # Create new population starting with the best parents (elitism)
            new_population = parents[:]
            
            # Fill the rest of the population with offspring
            while len(new_population) < self.pop_size:
                # Choose parents for reproduction (can be the same parents multiple times)
                p1, p2 = random.sample(parents, 2) if len(parents) > 1 else (parents[0], parents[0])
                
                # Create offspring through crossover
                c1, c2 = p1.crossover(p2)
                
                # Apply mutation
                c1.mutate(self.mutation_rate)
                c2.mutate(self.mutation_rate)
                
                # Add to new population
                new_population += [c1, c2]
            
            # Ensure population size stays constant
            self.population = new_population[:self.pop_size]

            # Collect fitness data for analysis
            fitness_scores = [self.fitness(chromosome) for chromosome in self.population]
            best_fitness = max(fitness_scores)
            avg_fitness = np.mean(fitness_scores)
            std_fitness = np.std(fitness_scores)

            # Calculate success rate (how many agents collected gold)
            success_count = 0
            for chromosome in self.population:
                self.env.reset()
                gold_collected = False
                exit_success = False
                
                for action in chromosome.actions:
                    result = self.env.move_agent(action)
                    if result == 'gold':
                        gold_collected = True
                    if result == 'win':
                        exit_success = True
                        break
                
                if gold_collected:
                    success_count += 0.5  # Half success for just finding gold
                if exit_success:
                    success_count += 0.5  # Full success for finding gold and exiting
            
            success_rate = success_count / self.pop_size
            
            # Store history
            self.fitness_history.append(fitness_scores)
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            self.std_fitness_history.append(std_fitness)
            self.success_rate_history.append(success_rate)
            
            # Optional: Print progress
            if gen % 10 == 0:
                print(f"Generation {gen}: Best Fitness = {best_fitness:.2f}, Avg Fitness = {avg_fitness:.2f}, Success Rate = {success_rate:.2%}")

    def get_statistical_summaries(self):
        """Get statistical summaries of the evolution process.
        
        Returns:
            A dictionary containing the fitness history statistics.
        """
        return {
            'best_fitness': self.best_fitness_history,
            'avg_fitness': self.avg_fitness_history,
            'std_fitness': self.std_fitness_history,
            'success_rate': self.success_rate_history
        }