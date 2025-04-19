import pygame
import sys
import time
from environment import WumpusWorld

def visualize_agent_path(world, best_chromosome=None):
    """Visualize the agent's path in the Wumpus World.
    
    Args:
        world: The WumpusWorld environment.
        best_chromosome: Optional chromosome to visualize. If None, use the environment's
                         move_agent_logic to determine moves.
    """
    # Initialize Pygame
    pygame.init()

    # Constants
    CELL_SIZE = 100
    GRID_SIZE = world.size
    SCREEN_SIZE = GRID_SIZE * CELL_SIZE
    FPS = 1  # Slow down for visualization

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    DARK_GRAY = (100, 100, 100)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GOLD = (255, 215, 0)

    # Initialize screen
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 100))  # Extra space for status
    pygame.display.set_caption("Wumpus World Visualization")
    clock = pygame.time.Clock()

    # Load Images
    try:
        agent_img = pygame.image.load("assets/agent.png")
        wumpus_img = pygame.image.load("assets/wumpus.png")
        gold_img = pygame.image.load("assets/gold.png")
        pit_img = pygame.image.load("assets/pit.png")
        breeze_img = pygame.image.load("assets/breeze.png")
        stench_img = pygame.image.load("assets/stench.png")
        
        # Resize Images
        agent_img = pygame.transform.scale(agent_img, (CELL_SIZE - 10, CELL_SIZE - 10))
        wumpus_img = pygame.transform.scale(wumpus_img, (CELL_SIZE - 10, CELL_SIZE - 10))
        gold_img = pygame.transform.scale(gold_img, (CELL_SIZE - 10, CELL_SIZE - 10))
        pit_img = pygame.transform.scale(pit_img, (CELL_SIZE - 10, CELL_SIZE - 10))
        breeze_img = pygame.transform.scale(breeze_img, (CELL_SIZE // 2, CELL_SIZE // 2))
        stench_img = pygame.transform.scale(stench_img, (CELL_SIZE // 2, CELL_SIZE // 2))
    except pygame.error:
        # If images fail to load, use colored rectangles instead
        agent_img = wumpus_img = gold_img = pit_img = breeze_img = stench_img = None
        print("Warning: Could not load image assets. Using colored rectangles instead.")

    # Path trace for agent
    path_cells = []

    def draw_grid(world):
        # Draw the grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                # Mark visited cells with light gray
                if (x, y) in world.visited:
                    pygame.draw.rect(screen, GRAY, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                
                # Mark cells that are part of the agent's path
                if (x, y) in path_cells:
                    # Draw a small dot to indicate the path
                    pygame.draw.circle(screen, GREEN, 
                                    (y * CELL_SIZE + CELL_SIZE // 2, 
                                     x * CELL_SIZE + CELL_SIZE // 2), 
                                    5)
                
                # Draw grid lines
                pygame.draw.rect(screen, BLACK, rect, 2)

                # Draw elements
                cell_center = (y * CELL_SIZE + CELL_SIZE // 2, x * CELL_SIZE + CELL_SIZE // 2)
                
                # Draw pits
                if (x, y) in world.pits:
                    if pit_img:
                        screen.blit(pit_img, (y * CELL_SIZE + 5, x * CELL_SIZE + 5))
                    else:
                        pygame.draw.rect(screen, BLACK, (y * CELL_SIZE + 10, x * CELL_SIZE + 10, 
                                                         CELL_SIZE - 20, CELL_SIZE - 20))
                
                # Draw gold
                if world.gold_pos and (x, y) == world.gold_pos:
                    if gold_img:
                        screen.blit(gold_img, (y * CELL_SIZE + 5, x * CELL_SIZE + 5))
                    else:
                        pygame.draw.circle(screen, GOLD, cell_center, CELL_SIZE // 3)
                
                # Draw Wumpus
                if world.wumpus_alive and world.wumpus_pos and (x, y) == world.wumpus_pos:
                    if wumpus_img:
                        screen.blit(wumpus_img, (y * CELL_SIZE + 5, x * CELL_SIZE + 5))
                    else:
                        pygame.draw.polygon(screen, RED, [
                            (y * CELL_SIZE + CELL_SIZE // 2, x * CELL_SIZE + 10),
                            (y * CELL_SIZE + 10, x * CELL_SIZE + CELL_SIZE - 10),
                            (y * CELL_SIZE + CELL_SIZE - 10, x * CELL_SIZE + CELL_SIZE - 10)
                        ])
                
                # Draw percepts
                if (x, y) in world.breezes:
                    if breeze_img:
                        screen.blit(breeze_img, (y * CELL_SIZE + 10, x * CELL_SIZE + 10))
                    else:
                        pygame.draw.circle(screen, BLUE, 
                                        (y * CELL_SIZE + 20, x * CELL_SIZE + 20), 
                                        10)
                
                if (x, y) in world.stenches and world.wumpus_alive:
                    if stench_img:
                        screen.blit(stench_img, (y * CELL_SIZE + CELL_SIZE - 30, x * CELL_SIZE + 10))
                    else:
                        pygame.draw.circle(screen, (139, 69, 19),  # Brown
                                        (y * CELL_SIZE + CELL_SIZE - 20, x * CELL_SIZE + 20), 
                                        10)
        
        # Draw agent
        ax, ay = world.agent_pos
        agent_rect = pygame.Rect(ay * CELL_SIZE + 5, ax * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
        
        # Draw direction indicator
        if agent_img:
            # Rotate agent image based on direction
            rotated_img = agent_img
            if world.agent_dir == 'right':
                rotated_img = pygame.transform.rotate(agent_img, 0)
            elif world.agent_dir == 'up':
                rotated_img = pygame.transform.rotate(agent_img, 90)
            elif world.agent_dir == 'left':
                rotated_img = pygame.transform.rotate(agent_img, 180)
            elif world.agent_dir == 'down':
                rotated_img = pygame.transform.rotate(agent_img, 270)
            
            screen.blit(rotated_img, agent_rect)
        else:
            # Draw agent as triangle pointing in direction
            if world.agent_dir == 'right':
                pygame.draw.polygon(screen, GREEN, [
                    (ay * CELL_SIZE + CELL_SIZE - 20, ax * CELL_SIZE + CELL_SIZE // 2),
                    (ay * CELL_SIZE + 20, ax * CELL_SIZE + 20),
                    (ay * CELL_SIZE + 20, ax * CELL_SIZE + CELL_SIZE - 20)
                ])
            elif world.agent_dir == 'left':
                pygame.draw.polygon(screen, GREEN, [
                    (ay * CELL_SIZE + 20, ax * CELL_SIZE + CELL_SIZE // 2),
                    (ay * CELL_SIZE + CELL_SIZE - 20, ax * CELL_SIZE + 20),
                    (ay * CELL_SIZE + CELL_SIZE - 20, ax * CELL_SIZE + CELL_SIZE - 20)
                ])
            elif world.agent_dir == 'up':
                pygame.draw.polygon(screen, GREEN, [
                    (ay * CELL_SIZE + CELL_SIZE // 2, ax * CELL_SIZE + 20),
                    (ay * CELL_SIZE + 20, ax * CELL_SIZE + CELL_SIZE - 20),
                    (ay * CELL_SIZE + CELL_SIZE - 20, ax * CELL_SIZE + CELL_SIZE - 20)
                ])
            elif world.agent_dir == 'down':
                pygame.draw.polygon(screen, GREEN, [
                    (ay * CELL_SIZE + CELL_SIZE // 2, ax * CELL_SIZE + CELL_SIZE - 20),
                    (ay * CELL_SIZE + 20, ax * CELL_SIZE + 20),
                    (ay * CELL_SIZE + CELL_SIZE - 20, ax * CELL_SIZE + 20)
                ])
        
        # Draw status panel
        status_rect = pygame.Rect(0, SCREEN_SIZE, SCREEN_SIZE, 100)
        pygame.draw.rect(screen, DARK_GRAY, status_rect)
        
        # Status text
        font = pygame.font.SysFont('Arial', 16)
        status_text = [
            f"Agent Position: {world.agent_pos}",
            f"Direction: {world.agent_dir}",
            f"Gold Collected: {'Yes' if world.has_gold else 'No'}",
            f"Arrow Count: {world.arrow_count}",
            f"Score: {world.score}"
        ]
        
        for i, text in enumerate(status_text):
            surface = font.render(text, True, WHITE)
            screen.blit(surface, (20, SCREEN_SIZE + 10 + i * 20))

    # Main visualization loop
    running = True
    action_index = 0
    
    # Reset the environment
    world.reset()
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Speed up simulation when space is held
                    FPS = 5
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # Return to normal speed
                    FPS = 1
        
        # Update and draw
        screen.fill(WHITE)
        
        # Track agent path
        path_cells.append(world.agent_pos)
        
        # Draw the grid and agent
        draw_grid(world)
        
        # Update agent position based on best chromosome or environment logic
        if best_chromosome and action_index < len(best_chromosome.actions):
            # Use the best chromosome's actions
            action = best_chromosome.actions[action_index]
            result = world.move_agent(action)
            action_index += 1
            
            # Display current action
            font = pygame.font.SysFont('Arial', 24)
            action_surface = font.render(f"Action: {action}", True, WHITE)
            screen.blit(action_surface, (SCREEN_SIZE // 2 - 60, SCREEN_SIZE + 60))
            
            # Check for end conditions
            if world.game_over or action_index >= len(best_chromosome.actions):
                # Display end message
                if world.has_gold and world.agent_pos == (0, 0):
                    end_msg = "SUCCESS! Gold collected and agent exited safely!"
                elif world.has_gold:
                    end_msg = "Gold collected but agent didn't exit!"
                else:
                    end_msg = "Agent failed to collect gold!"
                
                msg_surface = font.render(end_msg, True, WHITE)
                screen.blit(msg_surface, (20, SCREEN_SIZE + 80))
                
                # Wait a bit before ending
                pygame.display.flip()
                time.sleep(3)
                running = False
        else:
            # Use the environment's built-in logic
            if world.move_agent_logic():
                # Display end message
                font = pygame.font.SysFont('Arial', 24)
                if world.has_gold and world.agent_pos == (0, 0):
                    end_msg = "SUCCESS! Gold collected and agent exited safely!"
                elif world.has_gold:
                    end_msg = "Gold collected but agent didn't exit!"
                else:
                    end_msg = "Agent failed to collect gold!"
                
                msg_surface = font.render(end_msg, True, WHITE)
                screen.blit(msg_surface, (20, SCREEN_SIZE + 80))
                
                # Wait a bit before ending
                pygame.display.flip()
                time.sleep(3)
                running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()