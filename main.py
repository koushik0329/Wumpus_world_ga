from environment import WumpusWorld
from genetic_algorithm import GeneticAlgorithm
from analysis import analyze_performance, parameter_optimization_experiments, plot_statistical_summaries
from visualize import visualize_agent_path
import os
import argparse
import matplotlib.pyplot as plt
import time

def run_simulation(grid_size=4, pit_percentage=0.2, population_size=50, 
                  mutation_rate=0.05, selection_strategy='tournament', 
                  generations=50, chromosome_length=30, visualize=True):
    """Run the Wumpus World simulation with the given parameters.
    
    Args:
        grid_size: The size of the grid.
        pit_percentage: The percentage of cells that are pits.
        population_size: The size of the population.
        mutation_rate: The mutation rate.
        selection_strategy: The selection strategy ('tournament', 'rank', or 'elitist').
        generations: The number of generations to evolve.
        chromosome_length: The length of each chromosome's action sequence.
        visualize: Whether to visualize the best solution.
    
    Returns:
        A tuple of (best_chromosome, best_fitness, genetic_algorithm)
    """
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Print configuration
    print("\n" + "="*50)
    print(f"STARTING SIMULATION WITH CONFIGURATION:")
    print(f"  Grid Size: {grid_size}x{grid_size}")
    print(f"  Pit Percentage: {pit_percentage}")
    print(f"  Population Size: {population_size}")
    print(f"  Mutation Rate: {mutation_rate}")
    print(f"  Selection Strategy: {selection_strategy}")
    print(f"  Generations: {generations}")
    print(f"  Chromosome Length: {chromosome_length}")
    print("="*50 + "\n")
    
    # Initialize environment and GA
    start_time = time.time()
    world = WumpusWorld(size=grid_size, pit_percentage=pit_percentage)
    ga = GeneticAlgorithm(world, pop_size=population_size, 
                         mutation_rate=mutation_rate, 
                         selection_strategy=selection_strategy,
                         chromosome_length=chromosome_length)
    
    # Evolve for specified generations
    print(f"Evolving for {generations} generations...")
    ga.evolve(generations=generations)
    
    # Calculate and display elapsed time
    elapsed_time = time.time() - start_time
    print(f"\nEvolution completed in {elapsed_time:.2f} seconds.")
    
    # Get the best chromosome
    best_chromosome = max(ga.population, key=ga.fitness)
    best_fitness = ga.fitness(best_chromosome)
    
    # Print results
    print("\n" + "="*50)
    print("RESULTS:")
    print(f"Best Fitness: {best_fitness}")
    print("Best Action Sequence:")
    print(" ".join(best_chromosome.actions))
    print("="*50 + "\n")
    
    # Analyze performance
    summaries = ga.get_statistical_summaries()
    plot_statistical_summaries(summaries)
    
    # Save results
    plt.figure(figsize=(10, 6))
    plt.plot(ga.best_fitness_history)
    plt.title(f"Best Fitness Over Generations\nGrid Size: {grid_size}x{grid_size}, Selection: {selection_strategy}")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.savefig(f"output/best_fitness_{grid_size}x{grid_size}_{selection_strategy}.png")
    plt.close()
    
    # Visualize best solution
    if visualize:
        print("\nVisualizing best solution...")
        world.reset()  # Reset environment
        visualize_agent_path(world, best_chromosome)
    
    # Return results
    return best_chromosome, best_fitness, ga

def run_parameter_experiments(visualize=False):
    """Run experiments with different parameter combinations.
    
    Args:
        visualize: Whether to visualize the best solution from each experiment.
    """
    # Print header
    print("\n" + "="*50)
    print("STARTING PARAMETER OPTIMIZATION EXPERIMENTS")
    print("="*50 + "\n")
    
    # Define parameter combinations
    grid_sizes = [4, 8, 16]
    pop_sizes = [50, 100, 200]
    mutation_rates = [0.01, 0.05, 0.1]
    selection_strategies = ['tournament', 'rank', 'elitist']
    
    # Initialize results storage
    results = {}
    best_params = {}
    best_fitness = -float('inf')
    
    # Run experiments for each grid size
    for grid_size in grid_sizes:
        results[grid_size] = {}
        
        # Adjust chromosome length based on grid size
        chromosome_length = 30 if grid_size == 4 else (60 if grid_size == 8 else 100)
        
        for pop_size in pop_sizes:
            for mutation_rate in mutation_rates:
                for strategy in selection_strategies:
                    config = f"Grid: {grid_size}x{grid_size}, Pop: {pop_size}, Mut: {mutation_rate}, Sel: {strategy}"
                    print(f"\nRunning experiment with {config}")
                    
                    # Run simulation with current parameters
                    best_chrom, fitness, ga = run_simulation(
                        grid_size=grid_size,
                        population_size=pop_size,
                        mutation_rate=mutation_rate,
                        selection_strategy=strategy,
                        generations=50,  # Reduced for experiments
                        chromosome_length=chromosome_length,
                        visualize=visualize
                    )
                    
                    # Store results
                    key = (pop_size, mutation_rate, strategy)
                    results[grid_size][key] = {
                        'fitness': fitness,
                        'success_rate': ga.success_rate_history[-1]
                    }
                    
                    # Update best parameters if this configuration is better
                    if fitness > best_fitness:
                        best_fitness = fitness
                        best_params = {
                            'grid_size': grid_size,
                            'pop_size': pop_size,
                            'mutation_rate': mutation_rate,
                            'selection_strategy': strategy,
                            'chromosome_length': chromosome_length
                        }
    
    # Print summary of results
    print("\n" + "="*50)
    print("PARAMETER OPTIMIZATION RESULTS")
    print("="*50)
    
    for grid_size in grid_sizes:
        print(f"\nResults for {grid_size}x{grid_size} grid:")
        for key, value in results[grid_size].items():
            pop_size, mutation_rate, strategy = key
            print(f"  Pop: {pop_size}, Mut: {mutation_rate}, Sel: {strategy}")
            print(f"    Fitness: {value['fitness']:.2f}, Success Rate: {value['success_rate']:.2%}")
    
    # Print best parameters
    print("\n" + "="*50)
    print("BEST PARAMETERS:")
    print(f"  Grid Size: {best_params['grid_size']}x{best_params['grid_size']}")
    print(f"  Population Size: {best_params['pop_size']}")
    print(f"  Mutation Rate: {best_params['mutation_rate']}")
    print(f"  Selection Strategy: {best_params['selection_strategy']}")
    print(f"  Chromosome Length: {best_params['chromosome_length']}")
    print("="*50 + "\n")
    
    # Plot results
    plot_parameter_results(results, grid_sizes, pop_sizes, mutation_rates, selection_strategies)
    
    return results, best_params

def plot_parameter_results(results, grid_sizes, pop_sizes, mutation_rates, selection_strategies):
    """Plot the results of parameter optimization experiments.
    
    Args:
        results: The results dictionary.
        grid_sizes: The grid sizes used.
        pop_sizes: The population sizes used.
        mutation_rates: The mutation rates used.
        selection_strategies: The selection strategies used.
    """
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # For each grid size, plot fitness and success rate for different parameters
    for grid_size in grid_sizes:
        # Plot effect of population size
        plt.figure(figsize=(12, 6))
        for strategy in selection_strategies:
            for rate in mutation_rates:
                x_values = []
                y_values = []
                for pop_size in pop_sizes:
                    key = (pop_size, rate, strategy)
                    if key in results[grid_size]:
                        x_values.append(pop_size)
                        y_values.append(results[grid_size][key]['fitness'])
                plt.plot(x_values, y_values, marker='o', label=f"{strategy}, Mut={rate}")
        plt.xlabel("Population Size")
        plt.ylabel("Fitness")
        plt.title(f"Effect of Population Size on Fitness (Grid Size: {grid_size}x{grid_size})")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"output/pop_size_effect_{grid_size}x{grid_size}.png")
        plt.close()
        
        # Plot effect of mutation rate
        plt.figure(figsize=(12, 6))
        for strategy in selection_strategies:
            for pop_size in pop_sizes:
                x_values = []
                y_values = []
                for rate in mutation_rates:
                    key = (pop_size, rate, strategy)
                    if key in results[grid_size]:
                        x_values.append(rate)
                        y_values.append(results[grid_size][key]['fitness'])
                plt.plot(x_values, y_values, marker='o', label=f"{strategy}, Pop={pop_size}")
        plt.xlabel("Mutation Rate")
        plt.ylabel("Fitness")
        plt.title(f"Effect of Mutation Rate on Fitness (Grid Size: {grid_size}x{grid_size})")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"output/mutation_rate_effect_{grid_size}x{grid_size}.png")
        plt.close()
        
        # Plot effect of selection strategy
        plt.figure(figsize=(12, 6))
        for pop_size in pop_sizes:
            for rate in mutation_rates:
                x_values = []
                y_values = []
                for i, strategy in enumerate(selection_strategies):
                    key = (pop_size, rate, strategy)
                    if key in results[grid_size]:
                        x_values.append(i)
                        y_values.append(results[grid_size][key]['fitness'])
                plt.plot(x_values, y_values, marker='o', label=f"Pop={pop_size}, Mut={rate}")
        plt.xticks(range(len(selection_strategies)), selection_strategies)
        plt.xlabel("Selection Strategy")
        plt.ylabel("Fitness")
        plt.title(f"Effect of Selection Strategy on Fitness (Grid Size: {grid_size}x{grid_size})")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"output/selection_strategy_effect_{grid_size}x{grid_size}.png")
        plt.close()

def main():
    """Main function to run the simulation or experiments."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Wumpus World Genetic Algorithm')
    parser.add_argument('--grid-size', type=int, default=4,
                        help='Grid size (4, 8, or 16)')
    parser.add_argument('--pit-percentage', type=float, default=0.2,
                        help='Percentage of cells that are pits')
    parser.add_argument('--pop-size', type=int, default=50,
                        help='Population size')
    parser.add_argument('--mutation-rate', type=float, default=0.05,
                        help='Mutation rate')
    parser.add_argument('--selection', type=str, default='tournament',
                        choices=['tournament', 'rank', 'elitist'],
                        help='Selection strategy')
    parser.add_argument('--generations', type=int, default=50,
                        help='Number of generations')
    parser.add_argument('--chromosome-length', type=int, default=30,
                        help='Length of chromosome action sequence')
    parser.add_argument('--experiments', action='store_true',
                        help='Run parameter optimization experiments')
    parser.add_argument('--no-visualize', action='store_true',
                        help='Disable visualization')
    
    args = parser.parse_args()
    
    # Run experiments or single simulation
    if args.experiments:
        run_parameter_experiments(visualize=not args.no_visualize)
    else:
        run_simulation(grid_size=args.grid_size,
                      pit_percentage=args.pit_percentage,
                      population_size=args.pop_size,
                      mutation_rate=args.mutation_rate,
                      selection_strategy=args.selection,
                      generations=args.generations,
                      chromosome_length=args.chromosome_length,
                      visualize=not args.no_visualize)

if __name__ == "__main__":
    main()