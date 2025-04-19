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
        self.gold_pos = None
        self.wumpus_pos = None
        self.pits = []
        self.breezes = []
        self.stenches = []
        self.visited = set()
        self.safe_cells = set([(0, 0)])
        self.kb = KnowledgeBase()
        self.place_elements()
        self.generate_percepts()

    def place_elements(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if (i, j) != (0, 0)]
        random.shuffle(empty_cells)

        # Place pits
        for _ in range(self.pit_count):
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

        for pit in self.pits:
            for neighbor in self.neighbors(*pit):
                if neighbor not in self.pits:
                    self.breezes.append(neighbor)

        for neighbor in self.neighbors(*self.wumpus_pos):
            if neighbor != self.wumpus_pos:
                self.stenches.append(neighbor)

    def neighbors(self, x, y):
        return [
            (x + dx, y + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= x + dx < self.size and 0 <= y + dy < self.size
        ]

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

    def update_kb(self, x, y):
        percepts = []
        if (x, y) in self.breezes:
            percepts.append("breeze")
        if (x, y) in self.stenches:
            percepts.append("stench")
        if (x, y) == self.gold_pos:
            percepts.append("glitter")

        print(f"Percepts at ({x}, {y}): {', '.join(percepts) if percepts else 'None'}")

        if "breeze" in percepts:
            clause = f"Pit near ({x}, {y})"
            self.kb.add_clause([clause])
        if "stench" in percepts:
            clause = f"Wumpus near ({x}, {y})"
            self.kb.add_clause([clause])

        print("Updated Knowledge Base:")
        for clause in self.kb.clauses:
            print(f"  - {clause}")

    def infer_safe_cells(self):
        for x, y in self.visited:
            if (x, y) not in self.breezes and (x, y) not in self.stenches:
                for nx, ny in self.neighbors(x, y):
                    if (nx, ny) not in self.visited and (nx, ny) not in self.safe_cells:
                        print(f"Inferred safe cell: ({nx}, {ny})")
                        self.safe_cells.add((nx, ny))

    def assess_risks(self):
        risks = {}
        for x, y in self.visited:
            if (x, y) in self.breezes or (x, y) in self.stenches:
                for nx, ny in self.neighbors(x, y):
                    if (nx, ny) not in self.visited and (nx, ny) not in self.safe_cells:
                        risks[(nx, ny)] = risks.get((nx, ny), 0) + 1

        sorted_risks = sorted(risks.items(), key=lambda item: item[1])
        return [cell for cell, risk in sorted_risks]

    def move_agent_logic(self):
        x, y = self.agent_pos
        print(f"Agent is at ({x}, {y})")

        if (x, y) == self.gold_pos:
            print("Gold found! Agent wins!")
            return True

        self.safe_cells.add((x, y))
        self.visited.add((x, y))

        for nx, ny in self.neighbors(x, y):
            if (nx, ny) not in self.visited:
                if (nx, ny) not in self.safe_cells:
                    self.update_kb(nx, ny)

        self.infer_safe_cells()

        for nx, ny in self.safe_cells:
            if (nx, ny) not in self.visited:
                self.agent_pos = (nx, ny)
                return False

        uncertain_cells = self.assess_risks()
        if uncertain_cells:
            next_cell = uncertain_cells[0]
            print(f"Exploring uncertain cell: {next_cell} cautiously")
            self.agent_pos = next_cell
            return False

        print("No more safe moves available. Agent is stuck!")
        return True

class KnowledgeBase:
    def __init__(self):
        self.clauses = []

    def add_clause(self, clause):
        if clause not in self.clauses:
            self.clauses.append(clause)

    def pl_resolution(self, query):
        clauses = self.clauses + [negate_clause(query)]
        new = set()

        while True:
            pairs = combinations(clauses, 2)
            for (ci, cj) in pairs:
                resolvent = resolve(ci, cj)
                if not resolvent:
                    continue
                if resolvent == []:
                    return True
                new.add(tuple(sorted(resolvent)))

            if new.issubset(set(map(tuple, clauses))):
                return False
            clauses += list(map(list, new))

def negate_clause(clause):
    return [[-lit for lit in literals] for literals in clause]

def resolve(c1, c2):
    for lit in c1:
        if -lit in c2:
            temp1 = [x for x in c1 if x != lit]
            temp2 = [x for x in c2 if x != -lit]
            return temp1 + temp2
    return None
