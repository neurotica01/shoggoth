from random import shuffle
import random

from being import Being
from card_base import CardBase
from status import Berserk, Poison, Vulnerable



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

class VoidEmbrace(CardBase):
    def __init__(self):
        super().__init__("Void Embrace", 2, "Apply Vulnerable for 2 turns and gain Berserk for 2 turns.", requires_target=True)

    async def on_play(self, state, being, target):
        target.statuses.append(Vulnerable(remaining_turns=2))
        being.statuses.append(Berserk(remaining_turns=2))

class PurifyingLight(CardBase):
    def __init__(self):
        super().__init__("Purifying Light", 2, "Remove all status effects from target.", requires_target=True)

    async def on_play(self, state, being, target):
        target.statuses.clear()
        await state.log(f"All status effects were removed from {target.name}")

class EnergyInfusion(CardBase):
    def __init__(self):
        super().__init__("Energy Infusion", 0, "Gain 3 energy.", requires_target=False)

    async def on_play(self, state, being, target):
        being.resources["energy"] += 3
        await state.log(f"{being.name} gained 3 energy")


def default_deck():
    """
    Default deck for the player.
    """
    all_cards = [BasicAttack(), BasicBlock(), BasicHeal(), BasicDraw(),
                 PoisonFlask(), BerserkerPotion(), VoidEmbrace(), 
                 PurifyingLight(), EnergyInfusion()]
    deck = []
    for _ in range(10):
        deck.append(random.choice(all_cards))
    shuffle(deck)
    return deck