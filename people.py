from hand import Hand, Card
import numpy as np
from itertools import count


class Person:
    def __init__(self):
        self.hand = Hand()
    
    def draw(self, deck, side=None):
        """Draws a random cardand adds it to the hand."""

        card = deck.draw()
        
        # Add new card to person's hand
        if self.hand.split:
            if side == 'left':
                self.hand.cards[0].append(card)
            elif side == 'right':
                self.hand.cards[1].append(card)
            else:
                raise ValueError('If hand has been split, provide a side to draw to.')
        else:
            self.hand.cards.append(card)  # Add card to hand
            
        self.hand.addToHandValue(card, side)  # Update hand total
        self.tidyHandValue()
        
        return card
    
    def tidyHandValue(self):
        """Remove any excess hand values over 21."""
        # Remove any bust hand values if more than one hand value option exists
  
        if self.hand.split:
            new_hand_value = []
            if len(self.hand.hand_value[0]) > 1:
                for hand_value in self.hand.hand_value[0]:
                    if hand_value == 21:
                        new_hand_value = [21]  # Overwrite hand value, only keep 21
                        break
                    elif hand_value <= 21:
                        new_hand_value.append(hand_value)
            
            if len(self.hand.hand_value[1]) > 1:
                for hand_value in self.hand.hand_value[1]:
                    if hand_value == 21:
                        new_hand_value = [21]  # Overwrite hand value, only keep 21
                        break
                    elif hand_value <= 21:
                        new_hand_value.append(hand_value)

            if len(self.hand.hand_value[0]) > 1 or len(self.hand.hand_value[1]) > 1:
                # Update player's hand value
                self.hand.hand_value = tuple(new_hand_value)
        else:
            if len(self.hand.hand_value) > 1:
                new_hand_value = []
                for hand_value in self.hand.hand_value:
                    if hand_value == 21:
                        new_hand_value = [21]  # Overwrite hand value, only keep 21
                        break
                    elif hand_value <= 21:
                        new_hand_value.append(hand_value)
                        
                # Update player's hand value
                self.hand.hand_value = tuple(new_hand_value)
    
    def reset(self):
        self.hand = Hand()
    
    def __str__(self):
        return f'Hand: {self.hand}'


class Player(Person):
    _ids = count(0)
    
    def __init__(self, bank):
        super().__init__()
        
        self.id = next(self._ids)
        self.bank = bank

    def placeBet(self, bet):
        if self.bank - bet < 0:
            print('Insufficient funds')
        else:
            self.hand.bet += bet
            self.bank -= bet
    
    def __str__(self):
        return f'Player {self.id + 1} -> ' + super().__str__() + f', Bank: {self.bank}'


class Dealer(Person):
    def __init(self):
        super().__init__()
    
    def __str__(self):
        return 'Dealer -> ' + super().__str__()