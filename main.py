from environment import WumpusWorld
from genetic_algorithm import GeneticAlgorithm
from wumpus_visualizer import visualize_solution
import matplotlib.pyplot as plt

def main():
    # Configuration
    world = WumpusWorld(size=4, pit_percentage=0.2)
    ga = GeneticAlgorithm(world, pop_size=50, mutation_rate=0.05)
    
    # Run evolution
    ga.evolve(generations=50)
    
    # Get best solution
    best_chromosome = max(ga.population, key=lambda x: ga.fitness(x))
    
    # Visualize
    print("\nBest solution found:")
    print("Actions:", best_chromosome.actions)
    print("Fitness:", ga.fitness(best_chromosome))
    
    # Reset world for visualization
    world.reset()
    visualize_solution(world, best_chromosome)
    
    # Plot fitness progression
    plt.plot(ga.best_fitness_history, label='Best Fitness')
    plt.plot(ga.avg_fitness_history, label='Average Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness Progression')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()