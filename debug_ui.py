"""
Debug script to test the UI components.
"""
import pygame
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.ui.effects import BloodTitle, HauntedSkyline

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("UI Debug")

# Create test elements
skyline = HauntedSkyline(800, 600)
title = BloodTitle(400, 200, "TEST TITLE", multiline=True)

# Main loop
clock = pygame.time.Clock()
running = True

print("Debug UI started. Press ESC to exit.")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Update elements
    skyline.update()
    title.update()
    
    # Draw elements
    screen.fill((5, 5, 15))  # Midnight color
    skyline.draw(screen)
    title.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Debug UI closed.")
