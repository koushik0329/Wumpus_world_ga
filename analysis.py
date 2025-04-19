import matplotlib.pyplot as plt
import numpy as np
from environment import WumpusWorld  # Import the WumpusWorld class
from genetic_algorithm import GeneticAlgorithm  # Import the GeneticAlgorithm class

def plot_fitness(fitness_scores):
    plt.plot(fitness_scores)
    plt.xlabel('Generation')
    plt.ylabel('Fitness Score')
    plt.title('Fitness Score Over Generations')
    plt.show()

def plot_success_rate(success_rates):
    plt.plot(success_rates)
    plt.xlabel('Generation')
    plt.ylabel('Success Rate')
    plt.title('Success Rate Over Generations')
    plt.show()

def plot_statistical_summaries(summaries):
    generations = range(len(summaries['best_fitness']))
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 3, 1)
    plt.plot(generations, summaries['best_fitness'], label='Best Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Best Fitness')
    plt.title('Best Fitness Over Generations')
    plt.legend()

    plt.subplot(1, 3, 2)
    plt.plot(generations, summaries['avg_fitness'], label='Average Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Average Fitness')
    plt.title('Average Fitness Over Generations')
    plt.legend()

    plt.subplot(1, 3, 3)
    plt.plot(generations, summaries['std_fitness'], label='Standard Deviation of Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Standard Deviation of Fitness')
    plt.title('Standard Deviation of Fitness Over Generations')
    plt.legend()

    plt.tight_layout()
    plt.show()

def visualize_agent_path(env, actions):
    path = []
    env.reset()
    for action in actions:
        env.move_agent(action)
        path.append(env.agent_pos)

    plt.figure(figsize=(6, 6))
    for i in range(env.size):
        for j in range(env.size):
            cell = env.grid[i][j]
            if 'P' in cell:
                plt.plot(j, i, 'rs')  # Pit
            if 'W' in cell:
                plt.plot(j, i, 'ko')  # Wumpus
            if 'G' in cell:
                plt.plot(j, i, 'y*')  # Gold

    path_x, path_y = zip(*path)
    plt.plot(path_x, path_y, 'b-o')  # Agent path
    plt.xlim(-1, env.size)
    plt.ylim(-1, env.size)
    plt.gca().invert_yaxis()
    plt.title('Agent Path in Wumpus World')
    plt.show()

def analyze_performance(ga, generations=50):
    ga.evolve(generations=generations)
    summaries = ga.get_statistical_summaries()
    plot_statistical_summaries(summaries)

    best_chromosome = max(ga.population, key=ga.fitness)
    visualize_agent_path(ga.env, best_chromosome.actions)

def parameter_optimization_experiments(grid_sizes, pop_sizes, mutation_rates, selection_strategies):
    results = []
    for size in grid_sizes:
        for pop_size in pop_sizes:
            for mutation_rate in mutation_rates:
                for strategy in selection_strategies:
                    world = WumpusWorld(size=size)
                    ga = GeneticAlgorithm(world, pop_size=pop_size, mutation_rate=mutation_rate, selection_strategy=strategy)
                    ga.evolve(generations=50)
                    summaries = ga.get_statistical_summaries()
                    results.append({
                        'grid_size': size,
                        'pop_size': pop_size,
                        'mutation_rate': mutation_rate,
                        'selection_strategy': strategy,
                        'best_fitness': summaries['best_fitness'][-1],
                        'avg_fitness': summaries['avg_fitness'][-1],
                        'std_fitness': summaries['std_fitness'][-1]
                    })
    return results

def plot_parameter_optimization_results(results):
    for key in ['best_fitness', 'avg_fitness', 'std_fitness']:
        plt.figure(figsize=(12, 6))
        for strategy in set(result['selection_strategy'] for result in results):
            strategy_results = [result for result in results if result['selection_strategy'] == strategy]
            plt.plot([result['grid_size'] for result in strategy_results],
                     [result[key] for result in strategy_results],
                     label=f'{strategy}')
        plt.xlabel('Grid Size')
        plt.ylabel(key.replace('_', ' ').title())
        plt.title(f'{key.replace("_", " ").title()} Over Different Grid Sizes')
        plt.legend()
        plt.show()
