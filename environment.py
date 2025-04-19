import random
import pygame
from itertools import combinations

class WumpusWorld:
    def __init__(self, size=4, pit_percentage=0.2):
        self.size = size
        self.pit_percentage = pit_percentage
        self.reset()

    def reset(self):
        self.grid = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.agent_pos = (0, 0)
        self.agent_dir = 'right'
        self.arrow_count = 1
        self.has_gold = False
        self.wumpus_alive = True
        self.visited = set([(0, 0)])
        self.place_elements()
        self.generate_percepts()

    def place_elements(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if (i, j) != (0, 0)]
        random.shuffle(empty_cells)

        # Place pits
        self.pits = []
        pit_count = int(self.size * self.size * self.pit_percentage)
        for _ in range(pit_count):
            x, y = empty_cells.pop()
            self.grid[x][y] += 'P'
            self.pits.append((x, y))

        # Place Wumpus
        x, y = empty_cells.pop()
        self.grid[x][y] += 'W'
        self.wumpus_pos = (x, y)

        # Place Gold
        x, y = empty_cells.pop()
        self.grid[x][y] += 'G'
        self.gold_pos = (x, y)

    def generate_percepts(self):
        self.breezes = []
        self.stenches = []
        
        for x, y in self.pits:
            for nx, ny in self.get_neighbors(x, y):
                self.breezes.append((nx, ny))
                
        for nx, ny in self.get_neighbors(*self.wumpus_pos):
            self.stenches.append((nx, ny))

    def get_neighbors(self, x, y):
        return [
            (x + dx, y + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= x + dx < self.size and 0 <= y + dy < self.size
        ]

    def get_percepts(self, x, y):
        percepts = []
        if (x, y) in self.breezes:
            percepts.append('breeze')
        if (x, y) in self.stenches and self.wumpus_alive:
            percepts.append('stench')
        if (x, y) == self.gold_pos and 'G' in self.grid[x][y]:
            percepts.append('glitter')
        return percepts

    def move_agent(self, action):
        x, y = self.agent_pos
        result = None
        
        if action == 'MoveForward':
            if self.agent_dir == 'right' and y < self.size - 1:
                y += 1
            elif self.agent_dir == 'left' and y > 0:
                y -= 1
            elif self.agent_dir == 'up' and x > 0:
                x -= 1
            elif self.agent_dir == 'down' and x < self.size - 1:
                x += 1
                
            self.agent_pos = (x, y)
            self.visited.add((x, y))
            
            # Check for hazards
            if 'P' in self.grid[x][y]:
                return 'death'
            if 'W' in self.grid[x][y] and self.wumpus_alive:
                return 'death'
                
        elif action == 'TurnLeft':
            dirs = ['up', 'left', 'down', 'right']
            self.agent_dir = dirs[(dirs.index(self.agent_dir) + 1) % 4]
            
        elif action == 'TurnRight':
            dirs = ['up', 'right', 'down', 'left']
            self.agent_dir = dirs[(dirs.index(self.agent_dir) + 1) % 4]
            
        elif action == 'Shoot' and self.arrow_count > 0:
            self.arrow_count -= 1
            if self.agent_dir == 'right' and self.agent_pos[0] == self.wumpus_pos[0] and self.agent_pos[1] < self.wumpus_pos[1]:
                self.wumpus_alive = False
                return 'wumpus_killed'
            # Similar checks for other directions
            
        elif action == 'Grab':
            if (x, y) == self.gold_pos:
                self.has_gold = True
                self.grid[x][y] = self.grid[x][y].replace('G', '')
                return 'gold_collected'
                
        return result