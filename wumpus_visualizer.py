import pygame
import sys
import os
from environment import WumpusWorld

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 100
SCREEN_SIZE = 4 * CELL_SIZE  # Assuming 4x4 grid
FPS = 1

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

def load_image(name, default_color):
    """Try to load image or create colored surface"""
    try:
        img = pygame.image.load(os.path.join('assets', name))
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    except:
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surf.fill(default_color)
        return surf

# Load images
agent_img = load_image('agent.png', (0, 255, 0))       # Green
wumpus_img = load_image('wumpus.png', (255, 0, 0))     # Red
gold_img = load_image('gold.png', (255, 215, 0))       # Gold
pit_img = load_image('pit.png', (0, 0, 0))             # Black
breeze_img = load_image('breeze.png', (135, 206, 250)) # Light blue
stench_img = load_image('stench.png', (139, 69, 19))   # Brown

def draw_grid(world, screen):
    screen.fill(WHITE)
    
    for x in range(world.size):
        for y in range(world.size):
            rect = pygame.Rect(y*CELL_SIZE, x*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            
            # Draw elements
            if (x, y) == world.agent_pos:
                screen.blit(agent_img, rect)
            if (x, y) == world.gold_pos and 'G' in world.grid[x][y]:
                screen.blit(gold_img, rect)
            if (x, y) == world.wumpus_pos and world.wumpus_alive:
                screen.blit(wumpus_img, rect)
            if 'P' in world.grid[x][y]:
                screen.blit(pit_img, rect)
                
            # Draw percepts
            if (x, y) in world.breezes:
                screen.blit(breeze_img, (y*CELL_SIZE+25, x*CELL_SIZE+25))
            if (x, y) in world.stenches and world.wumpus_alive:
                screen.blit(stench_img, (y*CELL_SIZE+25, x*CELL_SIZE+50))
    
    pygame.display.flip()

def visualize_solution(world, chromosome):
    """Visualize the agent's actions in the Wumpus World"""
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Wumpus World Solution")
    clock = pygame.time.Clock()
    
    running = True
    step = 0
    
    while running and step < len(chromosome.actions):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
        action = chromosome.actions[step]
        result = world.move_agent(action)
        
        draw_grid(world, screen)
        print(f"Step {step}: {action} → {result}")
        
        if result in ['death', 'gold_collected']:
            running = False
            
        step += 1
        clock.tick(FPS)
    
    pygame.quit()