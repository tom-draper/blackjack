import random


class Hand():
    def __init__(self, available):
        self.cards = []
        self.draw(available)
        self.draw(available)
    
    def draw(self, available):
        self.cards.append(random.choice(available))
    
    def __str__(self):
        return str(self.cards)
        
class Game():
    def __init__(self, no_players=1):
        self.cards = ['2C', '2D', '2H', '2S', '3C', '3D', '3H', '3S'
                      '4C', '4D', '4H', '4S', '5C', '5D', '5H', '5S']
        self.no_players = no_players
        self.hands = {}
        self.hands['dealer_hand'] = Hand(self.cards)
        for i in range(self.no_players):
            self.hands['player{}_hand'.format(i)] = Hand(self.cards)
    
    def __str__(self):
        string = '{} players\n'.format(self.no_players)
        # Display each players hand
        for i in range(self.no_players):
            string += 'Player {} hand: '.format(i+1)
            # Print each card in players hand
            for idx, card in enumerate(self.hands['player{}_hand'.format(i)].cards):
                string += '{} '.format(card)
            if i < self.players - 1:
                string += '\n'
                
        return string

game = Game(3)
print(game)