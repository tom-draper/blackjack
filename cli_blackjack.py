from people import Player, Dealer
from hand import Deck
import time


class Blackjack:
    def __init__(self, no_players=1, player_bank=1000):
        self.deck = Deck()
        self.no_players = no_players
        
        # People dict holds {name : person_object}
        self.people = {}
        # Add the dealer
        self.people['dealer'] = Dealer()
        # Add each player
        for i in range(self.no_players):
            self.people[f'player{i}'] = Player(player_bank)
            
        self.current_side = None  # If split, hit on left pile then right
    
    def canSplit(self, player_id=0):
        player_cards = self.people[f'player{player_id}'].hand.cards
        
        if len(player_cards) == 2:
            # Possible to split if both cards are the same value
            return player_cards[0].value == player_cards[1].value
        return False

    def playerBust(self, bust):
        if type(bust) is tuple:
            return bust[0] == True and bust[1] == True
        else:
            return bust
    
    def split(self):
        self.player.hand.split = True
        
        # Modify cards to indicate split
        card1, card2 = self.player.hand.cards[0], self.player.hand.cards[1]
        self.player.hand.cards = [[card1], [card2]]
        
        # Modify hand value to indivate split
        hand_value1, hand_value2 = card1.value, card2.value
        # If the card is not an Ace, cast to a tuple hand value representation
        # An Ace has two possible values and is represented as a tuple by default
        if type(hand_value1) is int:
            hand_value1 = (hand_value1, )
        if type(hand_value2) is int:
            hand_value2 = (hand_value2, )
        # Create tuple pair of hand values, one for left and right card pile
        self.player.hand.hand_value = (hand_value1, hand_value2)
        
        # Modify bust to indicate split
        self.player.hand.bust = tuple((False, False))
        self.current_side = 'left'
    
    def calcBust(self, dealer=False, player_id=0):
        """Checks whether a given players hand has bust (hand value exceeded 21)."""
        if dealer:
            player = self.people['dealer']
        else:
            player = self.people[f'player{player_id}']
            
            if player.hand.split:
                # For checking if left pile has JUST bust and need to move to right pile
                original = player.hand.bust
                left_bust = True
                for hand_value in player.hand.hand_value[0]:
                    if hand_value <= 21:
                        left_bust = False
                # If calc bust has already been run after split selected and bust has been converted to tuple 
                if type(original) is tuple:
                    # Check if left pile has JUST gone bust
                    if original[0] == False and left_bust:
                        self.current_side = 'right'  # Move to right pile
                right_bust = True
                for hand_value in player.hand.hand_value[1]:
                    if hand_value <= 21:
                        right_bust = False
                player.hand.bust = tuple((left_bust, right_bust))
                # Player finished playing if right (second) pile has bust
                return right_bust  
            
        # Default, one-card-pile bust check
        bust = True
        # Check if there is a possible hand value under 21
        for hand_value in player.hand.hand_value:
            if hand_value <= 21:
                bust = False
        player.hand.bust = bust
        return bust

    def dealerContinueDraw(self):
        """Checks if any possible hand values is still under 17.
           Determines whether the dealer should continue to draw"""
        if self.calcBust(dealer=True):
            return False
        
        # Check if any possible hand values are under 17
        for hand_value in self.people['dealer'].hand.hand_value:
            if hand_value < 17:
                return True
        
        return False
    
    def personDraws(self, dealer=False, player_id=0, side=None, times=1):
        """Player draws input number of times."""
        if dealer:
            print('Dealer draws', end='')
            player = self.people['dealer']
        else:
            print(f'Player {player_id + 1} draws', end='')
            player = self.people[f'player{player_id}']
        
        # If drawing multiple times display multiple
        if times > 1:
            print(f' X{times}')
        else:
            print()
        
        for _ in range(times):
            if len(self.deck) == 0:
                self.deck.refillDeck()
            player.draw(self.deck, side)
        
        print(player, '\n')  # Display plaeyr hand status
    
    def allBust(self):
        """Checks whether every player has bust (hand value exceeds 21)."""
        # Look for player who hasn't bust
        for i in range(self.no_players):
            if self.people[f'player{i}'].hand.split:
                if self.people[f'player{i}'].hand.bust[0] == False or self.people[f'player{i}'].hand.bust[1] == False:
                    return False
            elif self.people[f'player{i}'].hand.bust == False:
                return False
        return True
    
    def divider(self):
        print('-'*25 + '\n')
    
    def collectWinnings(self, player_id=0, draw=False, override_winnings=0):
        if override_winnings != 0:
            winnings = override_winnings
        else:
            placed_bet = self.people[f'player{player_id}'].hand.bet
            
            if draw:
                winnings = placed_bet
            else:
                winnings = placed_bet * 2
            
        # Add winnings to player bank
        self.people[f'player{player_id}'].bank += winnings
    
    def checkWinners(self):
        """Checks each player and prints whether they have won or lost against
           the dealer."""
        # Loop through each player
        for i in range(self.no_players):
            player = self.people[f'player{i}']
            if player.hand.hand_value > self.people['dealer'].hand.hand_value or \
                    (self.people['dealer'].hand.bust and not player.hand.bust):
                print(f'** Player {i + 1} wins! **')
                self.collectWinnings(i)
            elif player.hand.hand_value == self.people['dealer'].hand.hand_value or \
                        player.hand.bust and self.people['dealer'].hand.bust:
                print('** Draw **')
                self.collectWinnings(i, draw=True)
            else:
                print(f'** Player {i + 1} loses **')
            print()
    
    def reset(self):
        for person in self.people.values():
            person.reset()
    
    def main(self):
        """Begins the game of command line Blackjack."""
        quit = False
        game_count = 1
        while not quit:
            print(f'\n-------- Game {game_count} begin --------\n')
            
            # Dealer init
            self.personDraws(dealer=True)
            
            for i in range(self.no_players):
                self.divider()  # Print a divider
                
                # Players init
                self.personDraws(player_id=i, times=2)
                
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
                self.people[f'player{i}'].placeBet(bet)
                
                # Players play
                while True:
                    choice = input('> Hit or stand: ')
                    print()

                    if choice == 'q':
                        quit = True
                        break
                    
                    if choice.lower() == 'hit' or choice.lower() == 'h':  # Draw
                        self.personDraws(player_id=i)
                        
                        if self.calcBust(player_id=i):
                            print(f'** Player {i + 1} bust! **\n')
                            break
                    elif choice.lower() == "stand" or choice.lower() == "s":
                        break
                    else:
                        print('Please enter an option.')
                if quit: break
            if quit: break
            
            self.divider()
            
            # If every player hasn't bust, the dealer begins drawing
            if not self.allBust():
                print('Dealer begins drawing...\n{}\n'.format(self.people['dealer']))
                
                # Dealer draws
                while self.dealerContinueDraw():
                    time.sleep(1.5)
                    self.personDraws(dealer=True)
                
                if self.calcBust(dealer=True):
                    print('** Dealer bust! **')

                self.checkWinners()
            
            self.reset()
            game_count += 1
            time.sleep(2)
    
    def __str__(self):
        string = 'GAME STATUS:\n'
        for person in self.people.values():
            string += f'{person}\n'
 
        # Print list of cards remaining
        string += f'Cards remaining: {self.deck}'
        
        return string

if __name__ == "__main__":
    game = Blackjack()
    game.main()
    pygame.quit()