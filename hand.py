import collections
import numpy as np


Card = collections.namedtuple('Card', ['rank', 'suit', 'value'])

class Deck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = ['spades', 'diamonds', 'clubs', 'hearts']
    card_values = {
        **dict.fromkeys(['2C', '2D', '2H', '2S'], 2), 
        **dict.fromkeys(['3C', '3D', '3H', '3S'], 3),
        **dict.fromkeys(['4C', '4D', '4H', '4S'], 4),
        **dict.fromkeys(['5C', '5D', '5H', '5S'], 5),
        **dict.fromkeys(['6C', '6D', '6H', '6S'], 6),
        **dict.fromkeys(['7C', '7D', '7H', '7S'], 7),
        **dict.fromkeys(['8C', '8D', '8H', '8S'], 8),
        **dict.fromkeys(['9C', '9D', '9H', '9S'], 9),
        **dict.fromkeys(['10C', '10D', '10H', '10S',
                         'JC', 'JD', 'JH', 'JS',
                         'KC', 'KD', 'KH', 'KS',
                         'QC', 'QD', 'QH', 'QS'], 10),
        **dict.fromkeys(['AC', 'AD', 'AH', 'AS'], (1, 11))
    }
        
    def __init__(self):
        self.refillDeck()
    
    def __len__(self):
        return len(self._cards)
    
    def __getitem__(self, position):
        return self._cards[position]
    
    def __str__(self):
        result = ''
        for card in self.cards:
            result += card.rank + card.suit[0].upper() + '\n'
    
    def getCardValue(self, card):
        """Takes a card and returns it's numerical value."""
        card_code = card.rank + card.suit[0].toupper()
        return self.card_values[card_code]
    
    def getCardValue(self, rank, suit):
        """Takes a card and returns it's numerical value."""
        card_code = rank + suit[0].upper()
        return self.card_values[card_code]

    def refillDeck(self):
        self._cards = [Card(rank, suit, self.getCardValue(rank, suit)) 
                       for rank in self.ranks for suit in self.suits]
    
    def draw(self):
        idx = np.random.choice(len(self._cards))
        card = self._cards[idx]
        self._cards.remove(card)
        return card


class Hand:
    def __init__(self):
        self.bet = 0
        self.cards = []  # List of card objects
        self.hand_value = (0,)  # Tuple containing possible values of this hand
        self.bust = False
        self.split = False
    
    def placeBet(self, bet):
        self.bet = bet
    
    def addToHandValue(self, card, side=None):
        """Add the value of the input card to the current hand value."""
        
        # Get current hand value(s) to update
        hand_values = None
        if self.split and side != None:
            if side == 'left':
                hand_values = self.hand_value[0]
            elif side == 'right':
                hand_values = self.hand_value[1]
        else:
            hand_values = self.hand_value
        
        # Recalulate the new hand value(s)
        if hand_values is not None:
            new_hand_value = set()  # Collect unique hand values
            if type(card.value) is tuple:  # If more than one card value (drawn Ace)
                # Add each card value to each current hand value
                # E.g. hand value can be 6 or 16 due to holding an Ace
                #      new card value could be 1 or 10 (an Ace)
                #      new hand value would be 7, 16, 17 or 26
                for hand_value in hand_values:
                    for value in card.value:
                        new_hand_value.add(hand_value + value)
            else:
                for hand_value in hand_values:
                    new_hand_value.add(hand_value + card.value)
                    
            # Save result as tuple
            if self.split and side != None:
                if side == 'left':
                    self.hand_value = tuple((tuple(new_hand_value), self.hand_value[1]))
                elif side == 'right':
                    self.hand_value = tuple((self.hand_value[0], tuple(new_hand_value)))
            else:
                self.hand_value = tuple(new_hand_value) 
    
    def calcHandValue(self):
        """Calculate the value of the entire hand from scratch."""
        if self.split:
            self.hand_value = ((0,), (0,))
            for card in self.cards[0]:
                self.add_to_hand_value(card, side='left')
            for card in self.cards[1]:
                self.add_to_hand_value(card, side='right')
        else:
            self.hand_value = (0,)
            for card in self.cards:
                self.add_to_hand_value(card)
    
    def __str__(self):
        string = ''
        
        if self.split:
            no_hands = 2
            cards = self.cards
            hand_value = self.hand_value
        else:
            no_hands = 1
            # Put cards in list of length 1 to allow generalised code below
            # If hands are split, they are already in a tuple
            cards = [self.cards]
            hand_value = [self.hand_value]
        
        for i in range(no_hands):
            # Add each card in hand to string
            if len(cards) == 0:
                string += 'None '
            else:
                for card in cards[i]:
                    string += card.rank + card.suit[0].upper() + ' '
            
            # Format and add hand value(s) separates by spaces
            hand_value_str = ''
            for idx, value in enumerate(hand_value[i]):
                hand_value_str += str(value)
                if idx < len(hand_value[i]) - 1:
                    hand_value_str += ' or '
            # Add the current hand total to string
            string += f'(={hand_value_str})'
            
            # Add a separator between hands if split
            if no_hands == 2 and i == 0:
                string += ' -//- '
            
        return string