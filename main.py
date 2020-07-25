import pygame
import time
from game import Blackjack

pygame.init()  # Initialise pygame


class GUIBlackjack(Blackjack):

    # Window
    WIDTH = 1200
    HEIGHT = 1000

    # Buttons
    RADIUS = 50
    BTN_GAP = 40

    # Colours
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN_BG = (53, 101, 77)  # Poker green

    # Fonts
    TITLE = pygame.font.SysFont('hack', 50)
    LARGER = pygame.font.SysFont('hack', 40)
    NORMAL = pygame.font.SysFont('hack', 20)

    def __init__(self, player_bank=1000):
        super().__init__(player_bank=1000)

        self.win = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT))  # Set resolution with tuple
        pygame.display.set_caption("Blackjack")  # Title along the window bar

        # Get typical card image size (for displaying cards centrally)
        self.cardSize = self.getCardSize('2D')
        self.buttons = {}  # Dict {name : (x,y)}
        self.quit = False

    def getCardSize(self, card):
        image = pygame.image.load('resources/{}.png'.format(card))
        return image.get_size()

    def scaleImg(self, image, scale_factor):
        width, height = image.get_size()
        return pygame.transform.scale(image, (int(width*scale_factor), int(height*scale_factor)))

    def cardPileWidth(self, no_cards, scale_factor):
        """Get width of a given number of cards when spread in a pile.
           Each subsequent card lies half overlapping the previous card.
           Top card is displayed fully.
           1 card -> width 1 card wide
           2 cards -> width 1.5 cards wide
           3 cards -> width = 2 cards wide.
        """
        return ((no_cards+1)/2) * ((self.cardSize[0]*scale_factor))

    def displayCards(self, centre_pos, scale_factor, dealer=False, player_id=0):
        if dealer:
            cards = self.people['dealer'].hand.cards
        else:
            cards = self.people['player{}'.format(player_id)].hand.cards

        # Convert centre position to top left corner position
        pos = (centre_pos[0] - self.cardPileWidth(len(cards), scale_factor)/2,
               centre_pos[1] - ((self.cardSize[1]*scale_factor)/2))

        shift = 0  # Shift each subsequent card along to get spread effect
        for card in cards:
            image = pygame.image.load('resources/{}.png'.format(card))
            image = self.scaleImg(image, scale_factor)
            self.win.blit(image, (pos[0] + shift, pos[1]))
            shift += (self.cardSize[0]*scale_factor)/2

    def displayButtons(self):
        # Central buttons
        btns = ['Hit', 'Stand']
        for i, btn in enumerate(btns):
            # Draw a circle
            # Iterate through positions left to right along the middle of the screen
            centre_pos = (int(self.WIDTH/2 - (self.BTN_GAP*(len(btns)-1))/2 -
                              ((self.RADIUS*len(btns))/2)) + ((self.RADIUS*2 + self.BTN_GAP) * i),
                          int(self.HEIGHT/2))
            pygame.draw.circle(self.win, self.BLACK,
                               centre_pos, self.RADIUS, 3)
            # Draw text in centre of button
            text = self.NORMAL.render(btns[i], 1, self.BLACK)
            self.win.blit(
                text, (centre_pos[0] - text.get_width()/2, centre_pos[1] - text.get_height()/2))

        # Bet buttons
        bet_btns = ['1', '5', '10', '50', '100']
        for i, btn in enumerate(bet_btns):
            # Draw a circle
            btn_range = (self.BTN_GAP*(len(btns)-1)) / \
                2 - ((self.RADIUS*len(btns))/2)
            # Iterate through positions top to bottom down the right side of the window
            centre_pos = (int(self.WIDTH - 100),
                          int(self.HEIGHT/2 -
                              ((self.RADIUS*2 + self.BTN_GAP) * (len(bet_btns)-1)/2) +
                              (self.RADIUS*2 + self.BTN_GAP) * i))
            pygame.draw.circle(self.win, self.BLACK,
                               centre_pos, self.RADIUS, 3)
            # Draw text in centre of button
            text = self.NORMAL.render(bet_btns[i], 1, self.BLACK)
            self.win.blit(
                text, (centre_pos[0] - text.get_width()/2, centre_pos[1] - text.get_height()/2))

    def display(self):
        # ----- Window -----
        self.win.fill(self.GREEN_BG)

        # ----- Title -----
        text = self.TITLE.render('Blackjack', 1, self.BLACK)
        self.win.blit(text, (self.WIDTH/2 - text.get_width()/2, 20))

        # ----- Buttons ------
        self.displayButtons()

        # ----- Dealer -----
        card_scale_factor = 0.2
        # Display cards
        centre_pos = (self.WIDTH/2, 250)
        self.displayCards(centre_pos, card_scale_factor, dealer=True)
        # Display hand value
        hand_value = self.people['dealer'].hand.hand_value
        text = self.NORMAL.render('£{}'.format(had_value), 1, self.BLACK)
        self.win.blit(text, (centre_pos[0] - text.get_width()/2 + 200, centre_pos[1]))

        # ----- Player ------
        player = self.people['player0']

        centre_pos = (self.WIDTH/2, 800)
        self.displayCards(centre_pos, card_scale_factor)
        # Display bank value
        bank_value = player.bank
        text = self.LARGER.render('£{}'.format(bank_value), 1, self.BLACK)
        self.win.blit(text, (100 - text.get_width()/2, self.HEIGHT-100))
        # Display bet value
        bet_value = player.hand.bet
        if bet_value != 0:
            text = self.NORMAL.render('£{}'.format(bet_value), 1, self.BLACK)
            self.win.blit(
                text, (centre_pos[0] - text.get_width()/2 + 200, centre_pos[1]))

        pygame.display.update()  # Update the display

    def handleEvents(self):
        handled = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Window close button pressed
                self.quit = True
                handled = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()  # x,y pos of mouse
                print(m_x, m_y)
                handled = True
        return handled

    def main(self):
        """One player GUI Blackjack game.
           Overrides the parent class playGame (command line version) method."""
        FPS = 60  # Max frames per second
        # Create a clock obeject to make sure our game runs at this FPS
        clock = pygame.time.Clock()

        self.display()

        run = True
        while run:
            clock.tick(FPS)

            # ------ PLAY GAME -------
            quit = False
            game_count = 1

            # Dealer init
            self.playerDraws(dealer=True)
            self.display()

            self.divider()  # Print a divider

            # Players init
            self.playerDraws(times=2)
            self.display()
            self.handleEvents()

            # Place bet for this hand
            # bet = input('> Enter bet: ')
            # if bet == 'q':
            #     quit = True
            #     break
            # if bet.isdigit():
            #     bet = int(bet)
            # else:
            #     bet = 0

            # PLace bet for this hand
            self.people['player0'].placeBet(0)
            self.display()

            # If every player hasn't bust, the dealer begins drawing
            if not self.allBust():

                print("Dealer\n{}\n".format(self.people['dealer']))

                # Dealer draws
                while self.dealerContinueDraw():
                    time.sleep(1.5)
                    self.playerDraws(dealer=True)
                    self.display()

                if self.bust(dealer=True):
                    print('** Dealer bust! **')

                self.checkWinners()

            self.reset()
            game_count += 1
            time.sleep(2)

            self.display()
            self.handleEvents()


game = GUIBlackjack()
game.main()

pygame.quit()
