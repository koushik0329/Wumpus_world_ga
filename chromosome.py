import random

# Updated action list to include the 'Climb' action for exiting the cave
ACTIONS = ['MoveForward', 'TurnLeft', 'TurnRight', 'Shoot', 'Grab', 'Climb']

class Chromosome:
    def __init__(self, length=30):
        """Initialize a chromosome with a random sequence of actions.
        
        Args:
            length: The length of the action sequence.
        """
        self.actions = [random.choice(ACTIONS) for _ in range(length)]

    def mutate(self, rate=0.05):
        """Mutate the chromosome by randomly changing actions.
        
        Args:
            rate: The probability of mutation for each action.
        """
        for i in range(len(self.actions)):
            if random.random() < rate:
                self.actions[i] = random.choice(ACTIONS)

    def crossover(self, other):
        """Perform crossover between this chromosome and another.
        
        Args:
            other: The other chromosome to crossover with.
            
        Returns:
            A tuple of two new child chromosomes.
        """
        # Use two-point crossover
        if random.random() < 0.5:  # 50% chance of one-point or two-point crossover
            # One-point crossover
            pivot = random.randint(1, len(self.actions) - 2)
            child1 = Chromosome(length=len(self.actions))
            child2 = Chromosome(length=len(self.actions))
            child1.actions = self.actions[:pivot] + other.actions[pivot:]
            child2.actions = other.actions[:pivot] + self.actions[pivot:]
        else:
            # Two-point crossover
            pivot1 = random.randint(1, len(self.actions) // 2)
            pivot2 = random.randint(len(self.actions) // 2 + 1, len(self.actions) - 2)
            child1 = Chromosome(length=len(self.actions))
            child2 = Chromosome(length=len(self.actions))
            child1.actions = self.actions[:pivot1] + other.actions[pivot1:pivot2] + self.actions[pivot2:]
            child2.actions = other.actions[:pivot1] + self.actions[pivot1:pivot2] + other.actions[pivot2:]
        
        return child1, child2