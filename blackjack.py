import pygame
import math
from collections import namedtuple
from cli_blackjack import Blackjack

pygame.init()


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
    GREEN = (0, 255, 0)  # Win message
    GREEN_BG = (53, 101, 77)  # Poker green backgroud
    BROWN = (180, 180, 180)  # 1 chip
    RED = (255, 0, 0)  # 5 chip and lose message
    BLUE = (0, 0, 255)  # 10 chip
    YELLOW = (150, 150, 0)  # 50 chip and draw message
    CHIP_BLACK = (220, 220, 220)  # 100 chip
    GREY = (84, 84, 84)  # Inactive button

    # Fonts
    GIGANTIC = pygame.font.SysFont('hack', 150)
    HUGE = pygame.font.SysFont('hack', 80)
    TITLE = pygame.font.SysFont('hack', 50)
    LARGER = pygame.font.SysFont('hack', 40)
    NORMAL = pygame.font.SysFont('hack', 20)
    
    GameStatus = namedtuple('GameStatus', 'round_over draw player_won winnings')

    def __init__(self, player_bank=1000):
        super().__init__(player_bank=1000)

        self.win = pygame.display.set_mode((self.WIDTH, self.HEIGHT))  # Set resolution with tuple
        pygame.display.set_caption("Blackjack")  # Title along the window bar
        
        # Restricted to one player game when using GUI
        self.player = self.people['player0']
        
        self.default_game_status = self.GameStatus(round_over=False, draw=None, player_won=None, winnings=0)
        self.game_status = None

        self.card_scale_factor = 0.2
        # Get typical card image size (for displaying cards centrally)
        self.card_size = self.getCardSize('2D')
        self.quit = False
        self.stand = False

        # Buttons
        self.buttons = {}  # Dict {name : (x,y)}
        self.action_btns_active = True
        self.bet_btns_active = True
        self.action_btns = ['Hit', 'Stand']
        self.bet_btns = ['1', '5', '10', '50', '100']
        
        # Gap between displayed card hands when player has chosen split
        self.split_gap = self.card_size[0]


    # ------------ GAME TOOLS ---------------

    def getCardSize(self, card):
        """Returns the pixel size of the card image scaled by the class scale factor.

        Args:
            card ("Card" namedtuple): the card to determine which image to use.

        Returns:
            tuple (int, int): size of the scaled card image. 
        """
        image = pygame.image.load(f'resources/{card}.png')
        # Return the actual card image dimensions multipled by the scale factor 
        # used during game to display
        return tuple(map(lambda x: x*self.card_scale_factor, image.get_size()))

    def scaleImg(self, image, scale_factor):
        """Scales an image uniformly by a scale factor.

        Args:
            image (pygame surface): the image to scale.
            scale_factor (float): the scale factor to scale the image by.

        Returns:
            pygame surface: scaled image.
        """
        width, height = image.get_size()
        return pygame.transform.scale(image, (int(width*scale_factor), 
                                              int(height*scale_factor)))
    
    def pauseGame(self, time):
        """Pauses game actions for a input time while still handling pygame events 
           (mouse click, window move etc.).

        Args:
            time (float): length of time to pause.
        """
        last = pygame.time.get_ticks()
        while True and not self.quit:
            now = pygame.time.get_ticks()
            if now - last >= time:
                break
            self.handleEvents()
            self.display()

    def enableAllButtons(self):
        self.action_btns_active = True
        self.bet_btns_active = True
    
    def disableAllButtons(self):
        self.action_btns_active = False
        self.bet_btns_active = False


    # ----------DISPLAY FUNCTIONS--------------

    def cardPileWidth(self, no_cards, scale_factor):
        """Get width of a given number of cards when spread in a pile.
           Each subsequent card lies half overlapping the previous card.
           Top card is displayed fully.
           1 card -> width 1 card wide
           2 cards -> width 1.5 cards wide
           3 cards -> width = 2 cards wide.
        """
        return ((no_cards + 1)/2) * ((self.card_size[0]))
    
    def displayActionButtons(self):
        """Draws each action button on the window. Action buttons are used to 
           take take an action on your hand (hit, split, stand)."""
        for i, btn in enumerate(self.action_btns):
            # Draw a circle
            # Iterate through positions left to right along the middle of the screen
            # Width = centre - (half the length of all buttons and gaps in between)
            #                + (gap between centre of two buttons)*(button number)
            
            # Draw button active or inactive
            if self.action_btns_active:
                btn_colour = self.BLACK
            else:
                btn_colour = self.GREY
            
            # Draw circle
            centre_pos = (int(self.WIDTH/2 
                              - ((self.RADIUS*2 + self.BTN_GAP) * (len(self.action_btns)-1)/2)
                              + (self.RADIUS*2 + self.BTN_GAP) * i),
                          int(self.HEIGHT/2))
            pygame.draw.circle(self.win, btn_colour, centre_pos, self.RADIUS, 3)
            
            # Draw text in centre of button
            text = self.NORMAL.render(self.action_btns[i], 1, btn_colour)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                 int(centre_pos[1] - text.get_height()/2)))
            
            # Add buttons centre positions to class dictionary
            self.buttons[btn] = centre_pos
    
    def displayBetButtons(self):
        """Draws each bet button on the window. Buttons are used to place bets 
           before round begins."""
        btn_colours = [self.BROWN, self.RED, self.BLUE, self.YELLOW, self.BLACK]
        
        for i, btn in enumerate(self.bet_btns):
            if self.bet_btns_active:
                btn_colour = btn_colours[i]
                text_colour = self.BLACK
            else:
                btn_colour = self.GREY
                text_colour = self.GREY
            
            # Draw circle
            btn_range = (self.BTN_GAP*(len(self.bet_btns)-1))/2 - ((self.RADIUS*len(self.bet_btns))/2)
            # Iterate through positions top to bottom down the right side of the window
            centre_pos = (int(self.WIDTH - 100),
                          int(self.HEIGHT/2 
                              - ((self.RADIUS*2 + self.BTN_GAP) * (len(self.bet_btns)-1)/2)
                              + (self.RADIUS*2 + self.BTN_GAP) * i))
            pygame.draw.circle(self.win, btn_colour, centre_pos, self.RADIUS, 3)
            
            # Draw text in centre of button
            text = self.NORMAL.render(btn, 1, text_colour)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                 int(centre_pos[1] - text.get_height()/2)))
            
            # Add buttons centre positions to class dictionary
            self.buttons[btn] = centre_pos

    def displayButtons(self):
        """Calls the functions to draw out all game buttons."""
        self.displayActionButtons()
        self.displayBetButtons()

    def buildHandValueString(self, dealer=False, player_id=0):
        """Build a string representing a person's hand value to display in game.
           Hand values are internally stored as a tuple containing all possible
           values a hand could take (as Aces can take two values).

        Args:
            dealer (bool, optional): Whether to use the dealers hand value instead 
                                     of a players. If
                                     true, player_id argument irrelevant. Defaults 
                                     to False.
            player_id (int, optional): The ID of the player whose hand value should
                                       be used. If dealer argument is false, 
                                       player_id is used. Defaults to 0.

        Returns:
            String: string representation of the person's hand value.
        """
        no_hands = 1  # Assume single pile of cards (no split)
        if dealer:
            hand_value = self.people['dealer'].hand.hand_value
        else:
            hand_value = self.people[f'player{player_id}'].hand.hand_value
            if self.people[f'player{player_id}'].hand.split:
                no_hands = 2
        
        # If no split, add single hand value to list for generalised loop below
        if no_hands == 1:
            hand_value = [hand_value]
        
        # Build hand value strings
        strings = []
        for i in range(no_hands):
            string = ''
            for idx, value in enumerate(hand_value[i]):
                string += str(value)
                if idx >= len(hand_value[i]) - 1:
                    string += ' '
                else:
                    string += ' or '
            strings.append(string)
        
        # If split, return hand value for both hands
        if not dealer and self.people[f'player{player_id}'].hand.split:
            return strings[0], strings[1] 
        # Return hand value for a single card
        return strings[0]
    
    def displayCardPile(self, cards, centre_pos):
        """Draws a pile of overlapping cards on the window.

        Args:
            cards (list of "Card" namedtuples): List of cards to display.
            centre_pos (tuple (x,y)): Centre position of the entire card pile 
                                      (coordinates on the window).
        """
        # Convert centre position to top left corner position of card pile
        pos = (centre_pos[0] - self.cardPileWidth(len(cards), self.card_scale_factor)/2,
               centre_pos[1] - self.card_size[1]/2)
        

        shift = 0  # Shift each subsequent card along to get spread effect
        for card in cards:
            card_code = card.rank + card.suit[0].upper()
            image = pygame.image.load(f'resources/{card_code}.png')
            image = self.scaleImg(image, self.card_scale_factor)
            self.win.blit(image, (int(pos[0] + shift), int(pos[1])))
            shift += (self.card_size[0])/2
    
    def displayCards(self, centre_pos, dealer=False, player_id=0):
        """Gets cards list of the correct person using arguments.
           Displays one card pile in the given position, or two piles if player 
           has split.

        Args:
            centre_pos ([type]): [description]
            dealer (bool, optional): [description]. Defaults to False.
            player_id (int, optional): [description]. Defaults to 0.
        """
        if dealer:
            cards = self.people['dealer'].hand.cards
        else:
            cards = self.people[f'player{player_id}'].hand.cards

        if len(cards) > 0:
            # If split, cards = [[cards1], [cards2]] rather than [cards]
            if type(cards[0]) is list:  # If split
                # Display both piles
                left_centre_pos = (centre_pos[0] - self.card_size[0], centre_pos[1])
                self.displayCardPile(cards[0], left_centre_pos)
                right_centre_pos = (centre_pos[0] + self.card_size[0], centre_pos[1])
                self.displayCardPile(cards[1], right_centre_pos)
            else:  # Normal, single-pile hand
                self.displayCardPile(cards, centre_pos)
    
    def displayDealer(self):
        """Displays dealers cards, current hand value and whether they've bust."""
        # Display cards
        centre_pos = (self.WIDTH/2, 250)
        self.displayCards(centre_pos, dealer=True)
        
        # Display bust
        if self.people['dealer'].hand.bust:
            text = self.HUGE.render('BUST', 1, self.RED)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2),
                                 int(centre_pos[1] - text.get_height()/2)))
            
        # Display hand value
        hand_value_str = self.buildHandValueString(dealer=True)
        text = self.NORMAL.render(hand_value_str, 1, self.BLACK)
        self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), int(centre_pos[1] + (self.card_size[1])/2 + 20)))
    
    def displayPlayer(self, player_id=0):
        """Display players cards, current hand value, whether they've bust.

        Args:
            player_id (int, optional): The ID of the player to be displayed. 
                                       Defaults to 0.
        """
        player = self.people[f'player{player_id}']
        
        # Display cards
        centre_pos = (self.WIDTH/2, 800)
        self.displayCards(centre_pos)
        
        # TODO: REVIEW
        # Display "bust" over the player's bust card pile
        if player.hand.split:
            # Left hand shifted to left by split gap, right hand shifted to right by split gap
            x_pos_change = [-self.split_gap, self.split_gap]
            # Check left hand then right hand
            for i in range(2):
                if player.hand.bust[i]:
                    text = self.HUGE.render('BUST', 1, self.RED)
                    self.win.blit(text, (int(centre_pos[0] - text.get_width()/2 + x_pos_change[i]), 
                                        int(centre_pos[1] - text.get_height()/2)))
        else:
            if player.hand.bust:
                text = self.HUGE.render('BUST', 1, self.RED)
                self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                    int(centre_pos[1] - text.get_height()/2)))
            
        # Display players bank value
        bank_value = player.bank
        text = self.LARGER.render(f'£{bank_value}', 1, self.BLACK)
        self.win.blit(text, (int(100 - text.get_width()/2), 
                             int(self.HEIGHT - 100)))
        
        # Display any winnings from the last round next to player's bank value 
        if self.game_status.round_over:
            if self.game_status.winnings > 0:
                winnings_text = self.NORMAL.render(f'+{self.game_status.winnings}', 1, self.BLACK)
                self.win.blit(winnings_text, (int(100 - text.get_width()/2 + 130), 
                                              int(self.HEIGHT + winnings_text.get_height()/2 - 100)))
                
        # Display hand value below player's cards
        if player.hand.split:
            left_hand_value_str, right_hand_value_str = self.buildHandValueString()
            left_text = self.NORMAL.render(left_hand_value_str, 1, self.BLACK)
            right_text = self.NORMAL.render(right_hand_value_str, 1, self.BLACK)
            self.win.blit(left_text, (int(centre_pos[0] - left_text.get_width()/2 - self.split_gap), 
                                      int(centre_pos[1] + (self.card_size[1])/2 + 20)))
            self.win.blit(right_text, (int(centre_pos[0] - right_text.get_width()/2 + self.split_gap), 
                                       int(centre_pos[1] + (self.card_size[1])/2 + 20)))
        else:
            hand_value_str = self.buildHandValueString()
            text = self.NORMAL.render(hand_value_str, 1, self.BLACK)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                 int(centre_pos[1] + (self.card_size[1])/2 + 20)))
        
        # Display bet value
        bet_value = player.hand.bet
        if bet_value != 0:
            text = self.NORMAL.render(f'£{bet_value}', 1, self.BLACK)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2 + 200), 
                                 int(centre_pos[1])))
    
    def displayRoundOutcome(self):
        """Using the game status modified by the recordWinners function, display whether """
        if self.game_status.round_over:
            centre_pos = (int(self.WIDTH/2), int(self.HEIGHT/2))
            if self.game_status.draw:
                text = self.GIGANTIC.render('DRAW', 1, self.YELLOW)
            elif self.game_status.player_won:
                text = self.GIGANTIC.render('YOU WIN', 1, self.GREEN)
            else:
                text = self.GIGANTIC.render('YOU LOSE', 1, self.RED)
            self.win.blit(text, (int(centre_pos[0] - text.get_width()/2), 
                                 int(centre_pos[1] - text.get_height()/2)))
    
    def display(self):
        """Displays the current blackjack game state to the window."""
        self.win.fill(self.GREEN_BG)

        # Title at top of screen
        text = self.TITLE.render('Blackjack', 1, self.BLACK)
        self.win.blit(text, (int(self.WIDTH/2 - text.get_width()/2), 20))

        self.displayButtons()
        self.displayDealer()
        self.displayPlayer()
        # Display "you win", "draw" or "you lose"
        self.displayRoundOutcome()

        pygame.display.update()  # Update the display


    # ------------ GAME FUNCITONS -----------------
    
    def recordWinners(self):
        """Checks player result and alters the game status to indicate their
           win, loss or draw during the next execution of the display function."""
           
        win_game_status = self.GameStatus(round_over=True, draw=False, player_won=True, winnings=winnings)
        draw_game_status = self.GameStatus(round_over=True, draw=True, player_won=None, winnings=winnings)
        lose_game_status = self.GameStatus(round_over=True, draw=False, player_won=False, winnings=0)
        
        # TODO : REVIEW
        if self.player.hand.split:
            hand_results = []
            total_winnings = 0
            # Get result for both hand
            for i in range(2):
                # Check left hand for win
                if (self.player.hand.hand_value[i] > self.people['dealer'].hand.hand_value or \
                            self.people['dealer'].hand.bust) and not self.player.hand.bust[i]:
                    # Record win
                    hand_results.append('win')
                    total_winnings += self.player.hand.bet*2
                elif self.player.hand.hand_value[i] == self.people['dealer'].hand.hand_value or \
                            self.player.hand.bust and self.people['dealer'].hand.bust:
                    # Record draw
                    hand_results.append('draw')
                    total_winnings += self.player.hand.bet
                else:
                    # Player lose
                    hand_results.append('lose')
                
            # Calculate overall results and set game status for end screen
            # Based on combination of results for both hands
            if results[0] == 'win' or results[1] == 'win':  # One hand wins
                self.game_status = win_game_status
                self.collectWinnings(player_id=0, override_winnings=winnings)  
            elif results[0] == 'draw' or results[1] == 'draw':  # If two draws, or one draw and a loss 
                self.game_status = draw_game_status
                self.collectWinnings(player_id=0, draw=True, override_winnings=winnings)
            else:  # Both lose
                self.game_status = lose_game_status

        else:
            if (self.player.hand.hand_value > self.people['dealer'].hand.hand_value or \
                        self.people['dealer'].hand.bust) and not self.player.hand.bust:
                # Player win
                self.game_status = win_game_status
                self.collectWinnings(player_id=0)
            elif self.player.hand.hand_value == self.people['dealer'].hand.hand_value or \
                        self.player.hand.bust and self.people['dealer'].hand.bust:
                # Draw
                self.game_status = draw_game_status
                self.addWinnings(player_id=0, draw=True)
            else:
                # Player lose
                self.game_status = lose_game_status

    def handleEvents(self):
        handled = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Window close button pressed
                self.quit = True
                handled = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()  # x,y pos of mouse
                for btn, pos in self.buttons.items():
                    d = math.sqrt((pos[0] - m_x)**2 + (pos[1] - m_y)**2)
                    if d < self.RADIUS:  # If click inside this button
                        # No longer possible to split after first action taken
                        if btn in self.action_btns and self.action_btns_active:
                            if 'Split' in self.action_btns:
                                self.action_btns.remove('Split')
                        if btn == 'Hit' and self.action_btns_active:
                            self.personDraws(side=self.current_side)
                            # Player no longer able to bet
                            self.bet_btns_active = False
                            break  # No other button needs to be checked
                        elif btn == 'Stand' and self.action_btns_active:
                            # If already split and now played stand on left hand
                            if self.player.hand.split and self.current_side == 'left':
                                # Future actions now affect right hand
                                self.current_side = 'right'
                            else:
                                self.stand = True
                                # Turn off all buttons while dealer plays
                                self.action_btns_active = False
                            self.bet_btns_active = False
                            break
                        elif btn == 'Split' and self.action_btns_active:
                            self.split()
                            break
                        elif btn.isdigit() and self.bet_btns_active:
                            self.player.placeBet(int(btn))
                            break
                handled = True
        return handled

    def main(self):
        """One player GUI Blackjack game.
           Overrides the parent class playGame (command line version) method."""
        FPS = 60  # Max frames per second
        # Create a clock obeject to make sure our game runs at this FPS
        clock = pygame.time.Clock()
        game_count = 0
        
        while not self.quit:
            clock.tick(FPS)
            self.game_status = self.default_game_status
            
            # Disable all buttons while set up game
            self.disableAllButtons()
            self.display()
            
            # Dealer initialise
            self.personDraws(dealer=True)
            self.display()
            self.pauseGame(1000)
            
            # Players initialise
            self.personDraws()
            self.pauseGame(1000)
            self.personDraws()
            # Check if split is an option
            if self.canSplit():
                self.action_btns.append('Split')  # Add split button
            self.display()
            
            # Ensure all buttons active before play
            self.enableAllButtons()
            
            # PLAYER GAME LOOP
            self.stand = False
            while not self.stand and not self.quit:
                self.handleEvents()  # Update stand (if stand action selected)
                self.display()
                if self.calcBust():  # Update players hand bust status
                    self.action_btns_active = False  # Grey out action buttons if bust
                    self.pauseGame(1000)
                    break
            
            # DEALER GAME LOOP
            if not self.allBust() and not self.quit:
                print('Dealer begins drawing...\n{}\n'.format(self.people['dealer']))

                # Dealer draws
                wait_before_draw = 1500
                last = pygame.time.get_ticks()
                while self.dealerContinueDraw():
                    now = pygame.time.get_ticks()
                    if now - last >= wait_before_draw:
                        self.personDraws(dealer=True)
                        self.display()
                        last = now
                    self.handleEvents()
                
                # Update dealer bust status
                self.calcBust(dealer=True)
                self.pauseGame(2000)  # Pause to view the result
            
            if not self.quit:
                # Set a new game status for a finished round
                self.recordWinners()
                self.display()
                self.pauseGame(2000)  # Pause to view the result
                
                self.reset()  # Redraw new hands
                self.action_btns_active = True
                self.bet_btns_active = True
                game_count += 1



if __name__ == "__main__":
    game = GUIBlackjack()
    game.main()
    pygame.quit()
