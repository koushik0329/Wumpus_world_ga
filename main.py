from simulation import run_simulation
from analysis import analyze_performance, parameter_optimization_experiments, plot_parameter_optimization_results
from environment import WumpusWorld
from genetic_algorithm import GeneticAlgorithm

if __name__ == "__main__":
    # Configuration parameters
    GRID_SIZE = 4
    PIT_PERCENTAGE = 0.2
    POPULATION_SIZE = 50
    MUTATION_RATE = 0.05
    SELECTION_STRATEGY = 'tournament'  # Options: 'tournament', 'rank', 'elitist'
    GENERATIONS = 50

    # Run the simulation with the default configuration
    world = WumpusWorld(size=GRID_SIZE, pit_percentage=PIT_PERCENTAGE)
    ga = GeneticAlgorithm(world, pop_size=POPULATION_SIZE, mutation_rate=MUTATION_RATE, selection_strategy=SELECTION_STRATEGY)
    analyze_performance(ga, generations=GENERATIONS)
    run_simulation()

    # Parameter optimization experiments
    grid_sizes = [4, 8, 16]
    pop_sizes = [50, 100, 200]
    mutation_rates = [0.01, 0.05, 0.1]
    selection_strategies = ['tournament', 'rank', 'elitist']
    results = parameter_optimization_experiments(grid_sizes, pop_sizes, mutation_rates, selection_strategies)
    plot_parameter_optimization_results(results)
