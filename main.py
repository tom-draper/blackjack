import pygame

pygame.init()  # Initialise pygame

# Pick size of window
WIDTH, HEIGHT = 1200, 1000  # All caps = constant
win = pygame.display.set_mode((WIDTH, HEIGHT))  # Set resolution with tuple
pygame.display.set_caption("Blackjack")  # Title along the window bar


# Colours
GREEN_BG = (53, 101, 77)  # Poker green


def draw():
    win.fill(GREEN_BG)  # Background colour
    
    
    pygame.display.update()  # Update the display

def main():
    FPS = 60  # Max frames per second
    # Create a clock obeject to make sure our game runs at this FPS
    clock = pygame.time.Clock()
    
    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Window close button pressed
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()  # x,y pos of mouse
                print(m_x, m_y)

        draw()


main()
pygame.quit()