import random

class WumpusWorld:
    def __init__(self, size=4, pit_percentage=0.2):
        self.size = size
        self.pit_count = int(size * size * pit_percentage)
        self.grid = [['' for _ in range(size)] for _ in range(size)]
        self.agent_pos = (0, 0)
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
