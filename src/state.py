import random
import sys
from agents import Agents
from card import default_deck, user_select_card_in_hand, user_select_target

BEFORE_GRAVEYARD = 0
AFTER_GRAVEYARD = 1

class Being:
    def __init__(self, name, hp, deck):
        self.name = name
        self.hp = hp
        self.deck = deck
        self.block = 0
        self.hand = []
        self.graveyard = []
        self.resources = {}
        self.buffs = {}
        self.debuffs = {}

    def draw(self, amount: int):
        for _ in range(amount):
            if not self.deck and not self.graveyard:
                print(f"{self.name} has no cards to draw.")
                return
            if len(self.deck) == 0:
                self.deck = self.graveyard
                self.graveyard = []
                self.deck.shuffle()
            self.hand.append(self.deck.pop(0))

    def discard(self, card):
        self.hand.remove(card)
        self.graveyard.append(card)

class Player(Being):
    def __init__(self, name, hp, deck):
        super().__init__(name, hp, deck)
        self.trinkets = []

class Enemy(Being):
    def __init__(self, name, hp, deck):
        super().__init__(name, hp, deck)
        self.personality = ""
        self.backstory = ""

class State:
    def __init__(self, player, enemy):
        self.player = Player( "Player", 20, deck=default_deck)
        self.enemy = Enemy("Enemy", 20, deck=default_deck)

        self.player.draw(5)
        self.enemy.draw(5)

        self.beings = random.shuffle([player, enemy])
        self.turn = 0
        self.theme = []

        self.agents = Agents()
        self.theme.append(self.agents.create_theme())





    def loop(self):
        if self.player.hp <= 0:
            self.on_lose()

            
        if self.enemy.hp <= 0:
            self.on_win()

        self.turn += 1
        he_who_plays = self.beings[self.turn % 2]
        print(f"It's {he_who_plays.name}'s turn.")
        print(f"Player HP: {self.player.hp}")
        print(f"Enemy HP: {self.enemy.hp}")



        if he_who_plays == self.player:
            self.player_turn()
        else:
            self.enemy_turn()



        # check win con. apply debuffs, buffs, status effects
        # ???
        pass

    def player_turn(self):
        self.player.draw(1)
        self.player.resources["energy"] += 2
        self.player.resources["energy"] = min(self.player.resources["energy"], 10)
        card = user_select_card_in_hand(self.player.hand)
        while True:
            if not card:
                print("You have no cards to play or opted to skip.")
                return
            elif card.cost > self.player.resources["energy"]:
                print("You don't have enough energy to play that card.")
            if card and card.cost <= self.player.resources["energy"]:
                if card.requires_target:
                    target = user_select_target(self)
                else:
                    target = None
                card.on_play(self, self.player, target)
                self.player.resources["energy"] -= card.cost

    def enemy_turn(self):
        self.enemy.draw(1)
        self.enemy.resources["energy"] += 2
        self.enemy.resources["energy"] = min(self.enemy.resources["energy"], 10)
        while True:
            viable = self.enemy.hand.filter(lambda card: card.cost <= self.enemy.resources["energy"])
            if not viable:
                print("Enemy has no cards to play.")
                return
            card = random.choice(viable)
            self.enemy.hand.remove(card)
            ## Ai.target() # self or enemy?
            card.on_play(self, self.enemy, None)
            self.enemy.resources["energy"] -= card.cost

            



    def on_win(self):
        print("You win!")
        sys.exit()

    def on_lose(self):
        print("You lose!")
        sys.exit()

# '''
# class Being
# - hand: [Card]
# - deck: [Card]
# - health: int
# - resources: {resource type: str, resource value: int}
# - buffs: {buff type: str, buff value: int} 
# - debuffs: {debuff type: str, debuff value: int}

# class Player(Being): # might have addl things
# - trinkets: [Trinket] # DAY 2 LOL

# class Enemy(Being): # might have addl things like
# - personality # these can be used for their own card generation
# - backstory
