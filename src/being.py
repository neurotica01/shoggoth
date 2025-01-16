from random import shuffle
from collections import Counter

from card_base import CardBase

class Being:
    def __init__(self, name, hp, deck):
        self.name = name
        self.hp = hp
        self.deck = deck
        self.block = 0
        self.hand = []
        self.graveyard: list[CardBase] = []
        self.resources: Counter[str] = Counter()
        self.statuses: list['Status'] = [] # type: ignore

    def draw(self, amount: int):
        for _ in range(amount):
            if not self.deck and not self.graveyard:
                print(f"{self.name} has no cards to draw.")
                return
            if len(self.deck) == 0:
                self.deck = self.graveyard
                self.graveyard = []
                shuffle(self.deck)
            self.hand.append(self.deck.pop(0))
        print(f"{self.name} drew {amount} card" + ("s" if amount > 1 else ""))

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
