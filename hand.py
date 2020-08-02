
class Card():
    def __init__(self, card_code):
        self.card_code = card_code
        self.path = f'resources/{card_code}.png'
        self.card_value = self.get_card_value()
    
    def get_card_value(self):
        """Takes a card and returns it's numerical value."""
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
        }
        
        if self.card_code in ['AC', 'AD', 'AH', 'AS']:
            return (1, 11)  # Possible values for an Ace
        else:
            return card_values[self.card_code]
    
    def __str__(self):
        return self.card_code


class Hand:
    def __init__(self):
        self.bet = 0
        self.cards = []  # List of card objects
        self.hand_value = (0,)  # Tuple containing possible values of this hand
        self.bust = False
        self.split = False
    
    def placeBet(self, bet):
        self.bet = bet
    
    def add_to_hand_value(self, card, side=None):
        """Add the value of the input card to the current hand value."""
        card_value = card.card_value
        
        hand_values = None
        if self.split and side != None:
            if side == 'left':
                hand_values = self.hand_value[0]
            elif side == 'right':
                hand_values = self.hand_value[1]
        else:
            hand_values = self.hand_value
        
        if hand_values is not None:
            new_hand_value = set()  # Collect unique hand values
            if type(card_value) is tuple:  # If more than one card value (drawn Ace)
                # Add each card value to each current hand value
                # E.g. hand value can be 6 or 16 due to holding an Ace
                #      new card value could be 1 or 10 (an Ace)
                #      new hand value would be 7, 16, 17 or 26
                for hand_value in hand_values:
                    for value in card_value:
                        new_hand_value.add(hand_value + value)
            else:
                for hand_value in hand_values:
                    new_hand_value.add(hand_value + card_value)
                    
            # Save result as tuple
            if self.split and side != None:
                if side == 'left':
                    self.hand_value = tuple((tuple(new_hand_value), self.hand_value[1]))
                elif side == 'right':
                    self.hand_value = tuple((self.hand_value[0], tuple(new_hand_value)))
            else:
                self.hand_value = tuple(new_hand_value) 
    
    def calc_hand_value(self):
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
            for i in range(2):
                # Add each card in hand to string
                if len(self.cards[i]) == 0:
                    string += 'None '
                else:
                    for card in self.cards[i]:
                        string += f'{card} '
                
                # Add hand value(s) separates by spaces
                hand_value = ''
                for idx, value in enumerate(self.hand_value[i]):
                    hand_value += f'{value}'
                    if idx < len(self.hand_value[i]) - 1:
                        hand_value += ' or '
                # Add the current hand total to string
                string += f'({hand_value})'
                if i == 0:
                    string += ' -//- '
        else:
            # Add each card in hand to string
            if len(self.cards) == 0:
                string += 'None '
            else:
                for card in self.cards:
                    string += f'{card} '
            
            # Add hand value(s) separates by spaces
            hand_value = ''
            for i, value in enumerate(self.hand_value):
                hand_value += f'{value}'
                if i < len(self.hand_value) - 1:
                    hand_value += ' or '
            # Add the current hand total to string
            string += f'({hand_value})'
            
        return string