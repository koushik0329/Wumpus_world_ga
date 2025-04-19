import random

ACTIONS = ['MoveForward', 'TurnLeft', 'TurnRight', 'Shoot', 'Grab']

class Chromosome:
    def __init__(self, length=20):
        self.actions = [random.choice(ACTIONS) for _ in range(length)]

    def mutate(self, rate=0.05):
        for i in range(len(self.actions)):
            if random.random() < rate:
                self.actions[i] = random.choice(ACTIONS)

    def crossover(self, other):
        pivot = random.randint(1, len(self.actions) - 2)
        child1 = Chromosome()
        child2 = Chromosome()
        child1.actions = self.actions[:pivot] + other.actions[pivot:]
        child2.actions = other.actions[:pivot] + self.actions[pivot:]
        return child1, child2
