import random

class WumpusWorld:
    def __init__(self, size=4, pit_percentage=0.2):
        self.size = size
        self.pit_percentage = pit_percentage
        self.reset()

    def reset(self):
        self.pit_count = int(self.size * self.size * self.pit_percentage)
        self.grid = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.agent_pos = (0, 0)
        self.agent_dir = 'right'  # Agent starts facing right
        self.arrow_count = 1
        self.place_elements()

    def place_elements(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if (i, j) != (0, 0)]
        random.shuffle(empty_cells)

        # Place pits
        for _ in range(self.pit_count):
            x, y = empty_cells.pop()
            self.grid[x][y] += 'P'

        # Place Wumpus
        x, y = empty_cells.pop()
        self.grid[x][y] += 'W'

        # Place Gold
        x, y = empty_cells.pop()
        self.grid[x][y] += 'G'

    def get_percepts(self, x, y):
        percepts = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                cell = self.grid[nx][ny]
                if 'P' in cell: percepts.append('breeze')
                if 'W' in cell: percepts.append('stench')
        if 'G' in self.grid[x][y]: percepts.append('glitter')
        return percepts

    def move_agent(self, action):
        x, y = self.agent_pos
        if action == 'MoveForward':
            if self.agent_dir == 'right' and y < self.size - 1: y += 1
            elif self.agent_dir == 'left' and y > 0: y -= 1
            elif self.agent_dir == 'up' and x > 0: x -= 1
            elif self.agent_dir == 'down' and x < self.size - 1: x += 1
        elif action == 'TurnLeft':
            if self.agent_dir == 'right': self.agent_dir = 'up'
            elif self.agent_dir == 'left': self.agent_dir = 'down'
            elif self.agent_dir == 'up': self.agent_dir = 'left'
            elif self.agent_dir == 'down': self.agent_dir = 'right'
        elif action == 'TurnRight':
            if self.agent_dir == 'right': self.agent_dir = 'down'
            elif self.agent_dir == 'left': self.agent_dir = 'up'
            elif self.agent_dir == 'up': self.agent_dir = 'right'
            elif self.agent_dir == 'down': self.agent_dir = 'left'
        elif action == 'Shoot' and self.arrow_count > 0:
            self.arrow_count -= 1
            # Implement shooting logic here
        elif action == 'Grab':
            if 'G' in self.grid[x][y]:
                self.grid[x][y] = self.grid[x][y].replace('G', '')
                return 'gold'
        self.agent_pos = (x, y)
        return None
