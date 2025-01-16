import random


class Being:
    def __init__(self, name, hp, deck):
        self.name = name
        self.hp = hp
        self.deck = deck
        self.hand = []
        self.graveyard = []
        self.resources = {}
        self.buffs = {}
        self.debuffs = {}

class State:
    def __init__(self, player, enemy):
        self.beings = random.shuffle([player, enemy])
        self.turn = 0
        self.theme = 


'''
class Being
- hand: [Card]
- deck: [Card]
- health: int
- resources: {resource type: str, resource value: int}
- buffs: {buff type: str, buff value: int} 
- debuffs: {debuff type: str, debuff value: int}

class Player(Being): # might have addl things
- trinkets: [Trinket] # DAY 2 LOL

class Enemy(Being): # might have addl things like
- personality # these can be used for their own card generation
- backstory
