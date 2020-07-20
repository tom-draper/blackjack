import random
from itertools import count


class Hand():
    def __init__(self, available_cards):
        self.cards = []
        self.hand_value = (0,)  # Tuple containing possible values of this hand
    
    def add_to_hand_value(self, card):
        """Add the value of the input card to the current hand value."""
        card_value = self.card_value(card)
        
        new_hand_value = []
        if type(card_value) is tuple:  # If more than one card value (drawn Ace)
            # Add each card value to each current hand value
            # E.g. hand value can be 6 or 16 due to holding an Ace
            #      new card value could be 1 or 10 (an Ace)
            #      new hand value would be 7, 16, 17 or 26
            for hand_value in self.hand_value:
                for value in card_value:
                    new_hand_value.append(hand_value + value)
        else:
            for hand_value in self.hand_value:
                new_hand_value.append(hand_value + card_value)
        
        self.hand_value = tuple(new_hand_value)  # Save result as tuple
    
    def calc_hand_value(self):
        """Calculate the value of the entire hand from scratch."""
        self.hand_value = (0,)
        for card in self.cards:
            self.add_to_hand_value(card)
    
    # def calc_hand_value(self):
    #     for card in self.cards:
    #         card_value = self.card_value(card)
            
    #         new_hand_value = []
    #         if type(card_value) is tuple:  # If more than one card value (drawn Ace)
    #             # Add each card value to each current hand value
    #             # E.g. hand value can be 6 or 16 due to holding an Ace
    #             #      new card value could be 1 or 10 (an Ace)
    #             #      new hand value would be 7, 16, 17 or 26
    #             for hand_value in self.hand_value:
    #                 for value in card_value:
    #                     new_hand_value.append(hand_value + value)
    #         else:
    #             for hand_value in self.hand_value:
    #                 new_hand_value.append(hand_value + card_value)
            
    #         self.hand_value = tuple(new_hand_value)  # Save result as tuple
    
    def card_value(self, card):
        card_values = {
            **dict.fromkeys(['2C', '2D', '2H', '2S'], 2), 
            **dict.fromkeys(['3C', '3D', '3H', '3S'], 3),
            **dict.fromkeys(['4C', '4D', '4H', '4S'], 4),
            **dict.fromkeys(['5C', '5D', '5H', '5S'], 5),
            **dict.fromkeys(['6C', '6D', '6H', '6S'], 6),
            **dict.fromkeys(['7C', '7D', '7H', '7S'], 7),
            **dict.fromkeys(['8C', '8D', '8H', '8S'], 8),
            **dict.fromkeys(['9C', '9D', '9H', '9S'], 9),
            **dict.fromkeys(['10C', '10D', '3H', '10S',
                             'JC', 'JD', 'JH', 'JS',
                             'KC', 'KD', 'KH', 'KS',
                             'QC', 'QD', 'QH', 'QS'], 10),
        }
        
        if card in ['AC', 'AD', 'AH', 'AS']:
            return (1, 11)
        else:
            return card_values[card]
    
    def __str__(self):
        string = ''
        
        # Add each card in hand to string
        for card in self.cards:
            string += '{} '.format(card)
        
        # Create sequence of hand values separates by spaces
        hand_value = ''
        for i, value in enumerate(self.hand_value):
            hand_value += '{}'.format(value)
            if i < len(self.hand_value) - 1:
                hand_value += ' or '
        # Add the current hand total to string
        string += '  ({})'.format(hand_value)
            
        return string


class Player():
    _ids = count(-1)
    
    def __init__(self, available_cards):
        self.id = next(self._ids)
        self.hand = Hand(available_cards)
    
    def draw(self, available_cards):
        card = random.choice(available_cards)
        self.hand.cards.append(card)
        self.hand.add_to_hand_value(card)
    
    def __str__(self):
        return 'Hand: {}'.format(self.hand)
    

class Game():
    def __init__(self, no_players=1):
        self.cards = self.refill()
        self.no_players = no_players
        
        self.players = {}
        # Add the dealer
        self.players['dealer'] = Player(self.cards)
        # Add each player
        for i in range(self.no_players):
            self.players['player{}'.format(i)] = Player(self.cards)
    
    def refill(self):
        return ['2C', '2D', '2H', '2S', '3C', '3D', '3H', '3S',
                '4C', '4D', '4H', '4S', '5C', '5D', '5H', '5S',
                '6C', '6D', '6H', '6S', '7C', '7D', '7H', '7S',
                '8C', '8D', '8H', '8S', '9C', '9D', '9H', '9S',
                '10C', '10D', '3H', '10S', 'AC', 'AD', 'AH', 'AS',
                'JC', 'JD', 'JH', 'JS', 'KC', 'KD', 'KH', 'KS', 
                'QC', 'QD', 'QH', 'QS']
    
    def bust(self, player):
        # Check if there is a possible hand value under 21
        for hand_value in player.hand.hand_value:
            if hand_value <= 21:
                return False
                
        return True

    def dealerContinue(self):
        """Checks if any possible hand values is still under 17"""
        for hand_value in self.players['dealer'].hand.hand_value:
            if hand_value == 21:  # If hand value reached 21, stop drawing
                return False
        
        # Check if any possible hand values are under 17
        for hand_value in self.players['dealer'].hand.hand_value:
            if hand_value < 17:
                return True
        
        return False
        

    def tidyHandValue(self, dealer=False, player_id=1):
        """Remove any hand values over 21."""
        if dealer:
            player = self.players['dealer']
        else:
            player = self.players['player{}'.format(player_id)]
        
        new_hand_value = []
        for hand_value in player.hand.hand_value:
            if hand_value == 21:
                new_hand_value = [21]  # Overwrite hand value, only keep 21
                break
            elif hand_value <= 21:
                new_hand_value.append(hand_value)
                
        # Update player's hand value
        player.hand.hand_value = tuple(new_hand_value)
    
    def playerDraws(self, dealer=False, player_id=1, times=1):
        if dealer:
            player = self.players['dealer']
            print('Dealer draws', end='')
        else:
            player = self.players['player{}'.format(player_id)]
            print('Player {} draws'.format(player_id+1), end='')
        
        # If drawing multiple times display multiple
        if times > 1:
            print(' X{}'.format(times))
        else:
            print('\n')
            
        for _ in range(times):
            player.draw(self.cards)
        print(player, '\n')  # Display plaeyr hand status
    
    def playGame(self):
        print('Game begin\n')
        
        # Dealer init
        self.playerDraws(dealer=True)
        
        for i in range(self.no_players):
            # Players init
            self.playerDraws(player_id=i, times=2)
            
            # Players play
            active = True
            while active:
                choice = input("Hit or stand: ")
                
                if choice.lower() == "hit" or choice.lower() == "h":  # Draw
                    print('Player {} draws'.format(i+1))
                    self.players['player{}'.format(i)].draw(self.cards)
                    print(self.players['player{}'.format(i)], '\n')
                    
                    if self.bust(self.players['player{}'.format(i)]):
                        print("Bust!")
                        active = False
                    else:
                        self.tidyHandValue(i)
                elif choice.lower() == "stand" or choice.lower() == "s":
                    active = False
                else:
                    print("Please enter an option.")
        
        # Dealer draws
        while dealerContinue():
            print('Dealer draws')
            self.players['dealer'].draw(self.cards)
            print(self.players['dealer'], '\n')
    
    def __str__(self):
        # Print dealer
        string = '> Dealer - {}\n'.format(self.players['dealer'])
        # Print each player
        for i in range(self.no_players):
            string += '> Player {} - {}\n'.format(i+1, self.players['player{}'.format(i)])
        # Print list of cards remaining
        string += '> Cards remaining: {}'.format(self.cards)
        
        return string

game = Game()
game.playGame()