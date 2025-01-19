from random import shuffle
from typing import Optional

from sqlalchemy import false
from being import Being
from card_base import CardBase
from status import Berserk, Poison



class BasicAttack(CardBase):
    def __init__(self):
        super().__init__("Basic Attack", 1, "Deal 5 damage to an enemy.")

    async def on_play(self, state, being, target):
        await state.deal_damage(source=being, target=target, amount=5)

class BasicBlock(CardBase):
    def __init__(self):
        super().__init__("Basic Block", 1, "Gain 5 block.", requires_target=False)

    async def on_play(self, game_state, being, target ):
        being.block += 5

class BasicHeal(CardBase):
    def __init__(self):
        super().__init__("Basic Heal", 1, "Heal 3 health.", requires_target=False)

    async def on_play(self, game_state, player, target ):
        await game_state.heal(player, 3)

class BasicDraw(CardBase):
    def __init__(self):
        super().__init__("Basic Draw", 1, "Draw 1 card.", requires_target=False)

    async def on_play(self, game_state, player, target ):
        await player.draw(1)

class PoisonFlask(CardBase):
    def __init__(self):
        super().__init__("Poison Flask", 1, "Deal 3 damage to an enemy, and apply 1 poison.")

    async def on_play(self, game_state, player, target ):
        await game_state.deal_damage(source=player, target=target, amount=3)
        target.statuses.append(Poison(amount=1, remaining_turns=1))

class BerserkerPotion(CardBase):
    def __init__(self):
        super().__init__("Berserker Potion", 1, "Gain Berserk for 3 turns.")

    async def on_play(self, game_state, player, target ):
        player.statuses.append(Berserk(remaining_turns=3))




def default_deck():
    deck = []
    for _ in range(5):
        deck.append(BasicAttack())
    for _ in range(4):
        deck.append(BasicBlock())
    for _ in range(2):
        deck.append(BasicHeal())
        deck.append(BasicDraw())

    shuffle(deck)
    return deck