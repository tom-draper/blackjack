import random


class Hand():
    def __init__(self, available_cards):
        self.cards = []
        self.draw(available_cards)
        self.draw(available_cards)

    
    def __str__(self):
        return str(self.cards)


class Player():
    def __init__(self, available_cards):
        self.hand = Hand(available_cards)
    
    def draw(self, available_cards):
        self.hand.cards.append(random.choice(available_cards))


class Game():
    def __init__(self, no_players=1):
        self.cards = self.refill()
        self.no_players = no_players
        
        self.players = {}
        self.players['dealer'] = Player(self.cards)
        for i in range(self.no_players):
            self.players['player{}'.format(i)] = Player(self.cards)
    
    def refill(self):
        return ['2C', '2D', '2H', '2S', '3C', '3D', '3H', '3S'
                '4C', '4D', '4H', '4S', '5C', '5D', '5H', '5S']
    
    def playGame(self):
        pass
    
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