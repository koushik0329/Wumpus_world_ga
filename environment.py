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
        self.wumpus_alive = True
        self.has_gold = False
        self.pits = []
        self.breezes = []
        self.stenches = []
        self.visited = set([(0, 0)])  # Start position is visited
        self.safe_cells = set([(0, 0)])
        self.kb = KnowledgeBase()
        self.place_elements()
        self.generate_percepts()
        self.bump = False
        self.scream = False
        self.score = 0
        self.game_over = False

    def place_elements(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if (i, j) != (0, 0)]
        random.shuffle(empty_cells)

        # Place pits
        for _ in range(self.pit_count):
            if not empty_cells:
                break
            x, y = empty_cells.pop()
            self.grid[x][y] += 'P'
            self.pits.append((x, y))

        # Place Wumpus
        if empty_cells:
            x, y = empty_cells.pop()
            self.grid[x][y] += 'W'
            self.wumpus_pos = (x, y)

        # Place Gold
        if empty_cells:
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

        if self.wumpus_alive and self.wumpus_pos:
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
        if (x, y) in self.breezes:
            percepts.append('breeze')
        if (x, y) in self.stenches and self.wumpus_alive:
            percepts.append('stench')
        if self.gold_pos == (x, y):
            percepts.append('glitter')
        if self.bump:
            percepts.append('bump')
            self.bump = False  # Reset bump after sensing
        if self.scream:
            percepts.append('scream')
            self.scream = False  # Reset scream after sensing
        return percepts

    def get_direction_coords(self):
        x, y = self.agent_pos
        if self.agent_dir == 'right':
            return (x, y + 1)
        elif self.agent_dir == 'left':
            return (x, y - 1)
        elif self.agent_dir == 'up':
            return (x - 1, y)
        elif self.agent_dir == 'down':
            return (x + 1, y)
        return None

    def move_agent(self, action):
        if self.game_over:
            return None
            
        x, y = self.agent_pos
        result = None
        
        if action == 'MoveForward':
            new_x, new_y = self.get_direction_coords()
            if 0 <= new_x < self.size and 0 <= new_y < self.size:
                self.agent_pos = (new_x, new_y)
                self.visited.add((new_x, new_y))
                # Check if agent fell into a pit or met the Wumpus
                if (new_x, new_y) in self.pits:
                    self.score -= 1000  # High penalty for falling into a pit
                    self.game_over = True
                    return 'pit'
                if self.wumpus_alive and (new_x, new_y) == self.wumpus_pos:
                    self.score -= 1000  # High penalty for encountering the Wumpus
                    self.game_over = True
                    return 'wumpus'
                self.score -= 1  # Small cost for each move
            else:
                self.bump = True
                self.score -= 5  # Penalty for bumping into a wall
        
        elif action == 'TurnLeft':
            if self.agent_dir == 'right': self.agent_dir = 'up'
            elif self.agent_dir == 'left': self.agent_dir = 'down'
            elif self.agent_dir == 'up': self.agent_dir = 'left'
            elif self.agent_dir == 'down': self.agent_dir = 'right'
            self.score -= 1  # Small cost for turning
            
        elif action == 'TurnRight':
            if self.agent_dir == 'right': self.agent_dir = 'down'
            elif self.agent_dir == 'left': self.agent_dir = 'up'
            elif self.agent_dir == 'up': self.agent_dir = 'right'
            elif self.agent_dir == 'down': self.agent_dir = 'left'
            self.score -= 1  # Small cost for turning
            
        elif action == 'Shoot' and self.arrow_count > 0:
            self.arrow_count -= 1
            self.score -= 10  # Cost for shooting the arrow
            
            # Get direction the agent is facing
            shoot_x, shoot_y = self.get_direction_coords()
            
            # Check if arrow hits the Wumpus
            if self.wumpus_alive and 0 <= shoot_x < self.size and 0 <= shoot_y < self.size:
                # Arrow travels in straight line until it hits a wall or the Wumpus
                while 0 <= shoot_x < self.size and 0 <= shoot_y < self.size:
                    if (shoot_x, shoot_y) == self.wumpus_pos:
                        self.wumpus_alive = False
                        self.scream = True
                        self.score += 500  # Reward for killing the Wumpus
                        # Remove Wumpus from grid
                        self.grid[shoot_x][shoot_y] = self.grid[shoot_x][shoot_y].replace('W', '')
                        # Remove stenches
                        self.stenches = []
                        self.generate_percepts()
                        result = 'scream'
                        break
                    
                    # Move arrow in the facing direction
                    if self.agent_dir == 'right':
                        shoot_y += 1
                    elif self.agent_dir == 'left':
                        shoot_y -= 1
                    elif self.agent_dir == 'up':
                        shoot_x -= 1
                    elif self.agent_dir == 'down':
                        shoot_x += 1
            
        elif action == 'Grab':
            if (x, y) == self.gold_pos and not self.has_gold:
                self.has_gold = True
                self.grid[x][y] = self.grid[x][y].replace('G', '')
                self.gold_pos = None
                self.score += 1000  # High reward for grabbing gold
                result = 'gold'
        
        elif action == 'Climb':
            if (x, y) == (0, 0) and self.has_gold:
                self.score += 1000  # Extra reward for exiting with gold
                self.game_over = True
                return 'win'
        
        return result

    def update_kb(self, x, y):
        percepts = self.get_percepts(x, y)
        
        if "breeze" in percepts:
            clause = f"Pit near ({x}, {y})"
            self.kb.add_clause([clause])
        if "stench" in percepts:
            clause = f"Wumpus near ({x}, {y})"
            self.kb.add_clause([clause])

    def infer_safe_cells(self):
        for x, y in self.visited:
            if (x, y) not in self.breezes and (x, y) not in self.stenches:
                for nx, ny in self.neighbors(x, y):
                    if (nx, ny) not in self.visited and (nx, ny) not in self.safe_cells:
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

        if self.has_gold and (x, y) == (0, 0):
            return True  # Agent has won

        if (x, y) == self.gold_pos:
            # Grab gold if found
            self.move_agent('Grab')
            return False

        self.safe_cells.add((x, y))
        self.visited.add((x, y))

        percepts = self.get_percepts(x, y)
        self.update_kb(x, y)
        self.infer_safe_cells()

        # If at start with gold, climb out
        if self.has_gold and (x, y) == (0, 0):
            self.move_agent('Climb')
            return True

        # Try to find safe unvisited cell
        for nx, ny in self.safe_cells:
            if (nx, ny) not in self.visited:
                # Simple navigation - not optimal but works for demo
                if nx > x:
                    if self.agent_dir != 'down':
                        if self.agent_dir == 'up': self.move_agent('TurnRight')
                        elif self.agent_dir == 'left': self.move_agent('TurnRight')
                        elif self.agent_dir == 'right': self.move_agent('TurnRight')
                    else:
                        self.move_agent('MoveForward')
                elif nx < x:
                    if self.agent_dir != 'up':
                        if self.agent_dir == 'down': self.move_agent('TurnRight')
                        elif self.agent_dir == 'right': self.move_agent('TurnLeft')
                        elif self.agent_dir == 'left': self.move_agent('TurnLeft')
                    else:
                        self.move_agent('MoveForward')
                elif ny > y:
                    if self.agent_dir != 'right':
                        if self.agent_dir == 'left': self.move_agent('TurnRight')
                        elif self.agent_dir == 'up': self.move_agent('TurnRight')
                        elif self.agent_dir == 'down': self.move_agent('TurnLeft')
                    else:
                        self.move_agent('MoveForward')
                elif ny < y:
                    if self.agent_dir != 'left':
                        if self.agent_dir == 'right': self.move_agent('TurnRight')
                        elif self.agent_dir == 'down': self.move_agent('TurnRight')
                        elif self.agent_dir == 'up': self.move_agent('TurnLeft')
                    else:
                        self.move_agent('MoveForward')
                return False

        # If we found stench, consider shooting
        if 'stench' in percepts and self.arrow_count > 0:
            self.move_agent('Shoot')
            return False

        # If no safe moves, try a risky one (if agent has no gold)
        if not self.has_gold:
            uncertain_cells = self.assess_risks()
            if uncertain_cells:
                next_cell = uncertain_cells[0]
                # Simple navigation to next cell (similar to above)
                nx, ny = next_cell
                if nx > x:
                    if self.agent_dir != 'down':
                        if self.agent_dir == 'up': self.move_agent('TurnRight')
                        elif self.agent_dir == 'left': self.move_agent('TurnRight')
                        elif self.agent_dir == 'right': self.move_agent('TurnRight')
                    else:
                        self.move_agent('MoveForward')
                elif nx < x:
                    if self.agent_dir != 'up':
                        if self.agent_dir == 'down': self.move_agent('TurnRight')
                        elif self.agent_dir == 'right': self.move_agent('TurnLeft')
                        elif self.agent_dir == 'left': self.move_agent('TurnLeft')
                    else:
                        self.move_agent('MoveForward')
                elif ny > y:
                    if self.agent_dir != 'right':
                        if self.agent_dir == 'left': self.move_agent('TurnRight')
                        elif self.agent_dir == 'up': self.move_agent('TurnRight')
                        elif self.agent_dir == 'down': self.move_agent('TurnLeft')
                    else:
                        self.move_agent('MoveForward')
                elif ny < y:
                    if self.agent_dir != 'left':
                        if self.agent_dir == 'right': self.move_agent('TurnRight')
                        elif self.agent_dir == 'down': self.move_agent('TurnRight')
                        elif self.agent_dir == 'up': self.move_agent('TurnLeft')
                    else:
                        self.move_agent('MoveForward')
                return False

        # If has gold, try to get back to (0,0)
        if self.has_gold:
            # Simple path back to start
            if x > 0:
                if self.agent_dir != 'up':
                    if self.agent_dir == 'down': self.move_agent('TurnRight')
                    elif self.agent_dir == 'right': self.move_agent('TurnLeft')
                    elif self.agent_dir == 'left': self.move_agent('TurnLeft')
                else:
                    self.move_agent('MoveForward')
            elif y > 0:
                if self.agent_dir != 'left':
                    if self.agent_dir == 'right': self.move_agent('TurnRight')
                    elif self.agent_dir == 'down': self.move_agent('TurnRight')
                    elif self.agent_dir == 'up': self.move_agent('TurnLeft')
                else:
                    self.move_agent('MoveForward')
            return False

        return True  # No more moves available

class KnowledgeBase:
    def __init__(self):
        self.clauses = []

    def add_clause(self, clause):
        if clause not in self.clauses:
            self.clauses.append(clause)

    def pl_resolution(self, query):
        # Simplified placeholder - not fully implemented
        return False