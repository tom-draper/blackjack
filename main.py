import pygame
import time
from game import Game

pygame.init()  # Initialise pygame

class GUIGame(Game):
    
    # Window
    WIDTH = 1200
    HEIGHT = 1000
    
    # Colours
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN_BG = (53, 101, 77)  # Poker green
    
    # Fonts
    TITLE = pygame.font.SysFont('times new roman', 40)
    
    def __init__(self):
        super().__init__()

        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))  # Set resolution with tuple
        pygame.display.set_caption("Blackjack")  # Title along the window bar
        
        # Get typical card image size (for displaying cards centrally)
        self.cardSize = getCardSize('2D')  

    def getCardSize(self, card):
        image = pygame.image.load('resources/{}.png'.format(card))
        return image.get_size()

    def displayButtons(self):
        pass

    def scaleImg(self, image, scale_factor):
        width, height = image.get_size()
        return pygame.transform.scale(image, (int(width*scale_factor), int(height*scale_factor)))
        
    def displayCards(self, pos, dealer=False, player_id=0):
        if dealer:
            cards = self.people['dealer'].hand.cards
        else:
            cards = self.people['player{}'.format(player_id)].hand.cards
            
        for card in cards:
            image = pygame.image.load('resources/{}.png'.format(card))
            image = self.scaleImg(image, 0.1)
            self.win.blit(image, pos)

    def display(self):
        # Window
        self.win.fill(self.GREEN_BG)
        
        # Title
        text = self.TITLE.render('Blackjack', 1, self.BLACK)
        self.win.blit(text, (self.WIDTH/2 - text.get_width()/2, 20))
        
        # Draw dealers cards
        self.displayCards((self.WIDTH/2, 100), dealer=True)
        
        # Draw player cards
        for i in range(self.no_players):
            self.displayCards((self.WIDTH/2, 100), dealer=True)
        
        pygame.display.update()  # Update the display

    def playGame(self):
        FPS = 60  # Max frames per second
        # Create a clock obeject to make sure our game runs at this FPS
        clock = pygame.time.Clock()
        
        self.display()
        
        run = True
        while run:
            clock.tick(FPS)
            
            # ------ PLAYGAME -------
            quit = False
            game_count = 1
            while not quit:
                print('-------- Game {} begin --------\n'.format(game_count))
                
                # Dealer init
                self.playerDraws(dealer=True)
                
                self.display()
                
                for i in range(self.no_players):
                    self.divider()  # Print a divider
                    
                    # Players init
                    self.playerDraws(player_id=i, times=2)
                    
                    # Place bet for this hand
                    bet = input('> Enter bet: ')
                    if bet == 'q':
                        quit = True
                        break
                    if bet.isdigit():
                        bet = int(bet)
                    else:
                        bet = 0
        
                    # PLace bet for this hand
                    self.people['player{}'.format(i)].placeBet(bet)
                    
                    # Players play
                    while True:
                        choice = input('> Hit or stand: ')
                        print()

                        if choice == 'q':
                            quit = True
                            break
                        
                        if choice.lower() == 'hit' or choice.lower() == 'h':  # Draw
                            self.playerDraws(player_id=i)
                            
                            if self.bust(player_id=i):
                                print('** Player {} bust! **\n'.format(i+1))
                                break
                        elif choice.lower() == "stand" or choice.lower() == "s":
                            break
                        else:
                            print("Please enter an option.")
                    if quit:
                        break
                if quit:
                    break
                
                # If every player hasn't bust, the dealer begins drawing
                if not self.allBust():
                    
                    print("Dealer\n{}\n".format(self.people['dealer']))
                    
                    # Dealer draws
                    while self.dealerContinueDraw():
                        time.sleep(1.5)
                        self.playerDraws(dealer=True)
                    
                    if self.bust(dealer=True):
                        print('** Dealer bust! **')
                
                    self.checkWinners()
                
                self.reset()
                game_count += 1
                time.sleep(2)
                
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # Window close button pressed
                        run = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        m_x, m_y = pygame.mouse.get_pos()  # x,y pos of mouse
                        print(m_x, m_y)

            self.display()


game = GUIGame()
game.playGame()

pygame.quit()