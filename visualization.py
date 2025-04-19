import pygame
import sys
from environment import WumpusWorld

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 100
GRID_SIZE = 4
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
FPS = 1  # Slow down agent movement for visualization

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Wumpus World")
clock = pygame.time.Clock()

# Load Images
agent_img = pygame.image.load("assets/agent.png")
wumpus_img = pygame.image.load("assets/wumpus.png")
gold_img = pygame.image.load("assets/gold.png")
pit_img = pygame.image.load("assets/pit.png")
breeze_img = pygame.image.load("assets/breeze.png")
stench_img = pygame.image.load("assets/stench.png")

# Resize Images
agent_img = pygame.transform.scale(agent_img, (CELL_SIZE, CELL_SIZE))
wumpus_img = pygame.transform.scale(wumpus_img, (CELL_SIZE, CELL_SIZE))
gold_img = pygame.transform.scale(gold_img, (CELL_SIZE, CELL_SIZE))
pit_img = pygame.transform.scale(pit_img, (CELL_SIZE, CELL_SIZE))
breeze_img = pygame.transform.scale(breeze_img, (CELL_SIZE // 2, CELL_SIZE // 2))
stench_img = pygame.transform.scale(stench_img, (CELL_SIZE // 2, CELL_SIZE // 2))

def draw_grid(world):
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

            # Draw elements
            if (x, y) == world.agent_pos:
                screen.blit(agent_img, rect)
            elif (x, y) == world.gold_pos:
                screen.blit(gold_img, rect)
            elif (x, y) == world.wumpus_pos:
                screen.blit(wumpus_img, rect)
            elif (x, y) in world.pits:
                screen.blit(pit_img, rect)
            if (x, y) in world.breezes:
                screen.blit(breeze_img, (y * CELL_SIZE + 25, x * CELL_SIZE + 25))
            if (x, y) in world.stenches:
                screen.blit(stench_img, (y * CELL_SIZE + 25, x * CELL_SIZE + 50))

def visualize_agent_path(env, actions):
    path = []
    env.reset()
    for action in actions:
        env.move_agent(action)
        path.append(env.agent_pos)

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid(env)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
