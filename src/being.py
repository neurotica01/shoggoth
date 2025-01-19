from random import shuffle
from collections import Counter

from card_base import CardBase

class Being:
    def __init__(self, name, hp, deck, log_hook):
        self.name = name
        self.hp = hp
        self.deck = deck
        self.log = log_hook

        self.block = 0
        self.hand = []
        self.graveyard: list[CardBase] = []
        self.resources: Counter[str] = Counter()
        self.statuses: list['Status'] = [] # type: ignore

    async def draw(self, amount: int) -> int:
        n_drawn = 0
        for _ in range(amount):
            if not self.deck and not self.graveyard:
                # await self.log(f"{self.name} has no cards to draw.", user_ack=True)
                return n_drawn
            if len(self.deck) == 0:
                self.deck = self.graveyard
                self.graveyard = []
                shuffle(self.deck)
            self.hand.append(self.deck.pop(0))
            n_drawn += 1
        # await self.log(f"{self.name} drew {n_drawn} card" + ("s" if n_drawn > 1 else ""), user_ack=True)
        return n_drawn

    def discard(self, card):
        self.hand.remove(card)
        self.graveyard.append(card)

    def __str__(self):
        return f"{self.name} ({self.hp} HP)" + (f" (block {self.block})" if self.block else "") + (f" (statuses: {self.statuses})" if self.statuses else "")

class Player(Being):
    def __init__(self, name, hp, deck, log_hook):
        super().__init__(name, hp, deck, log_hook)
        self.trinkets = []

class Enemy(Being):
    def __init__(self, name, hp, deck, log_hook):
        super().__init__(name, hp, deck, log_hook)
        self.personality = ""
        self.backstory = ""