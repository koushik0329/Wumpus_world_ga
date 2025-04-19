import matplotlib.pyplot as plt
import numpy as np
from environment import WumpusWorld
from genetic_algorithm import GeneticAlgorithm
from visualize import visualize_agent_path  # Import the visualization function

def plot_fitness(fitness_scores):
    """Plot fitness scores over generations.
    
    Args:
        fitness_scores: A list of fitness scores.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(fitness_scores)
    plt.xlabel('Generation')
    plt.ylabel('Fitness Score')
    plt.title('Fitness Score Over Generations')
    plt.grid(True)
    plt.savefig('fitness_scores.png')
    plt.show()

def plot_success_rate(success_rates):
    """Plot success rates over generations.
    
    Args:
        success_rates: A list of success rates.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(success_rates)
    plt.xlabel('Generation')
    plt.ylabel('Success Rate')
    plt.title('Success Rate Over Generations')
    plt.grid(True)
    plt.savefig('success_rates.png')
    plt.show()

def plot_statistical_summaries(summaries):
    """Plot statistical summaries of the evolution process.
    
    Args:
        summaries: A dictionary containing the fitness history statistics.
    """
    generations = range(len(summaries['best_fitness']))
    
    plt.figure(figsize=(16, 8))

    plt.subplot(2, 2, 1)
    plt.plot(generations, summaries['best_fitness'], label='Best Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Best Fitness')
    plt.title('Best Fitness Over Generations')
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.plot(generations, summaries['avg_fitness'], label='Average Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Average Fitness')
    plt.title('Average Fitness Over Generations')
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.plot(generations, summaries['std_fitness'], label='Standard Deviation of Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Standard Deviation')
    plt.title('Standard Deviation of Fitness Over Generations')
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(generations, summaries['success_rate'], label='Success Rate')
    plt.xlabel('Generation')
    plt.ylabel('Success Rate')
    plt.title('Success Rate Over Generations')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.savefig('evolution_statistics.png')
    plt.show()