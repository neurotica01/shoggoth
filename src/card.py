from random import shuffle
import random
from typing import Optional

from sqlalchemy import false
from being import Being
from card_base import CardBase
from status import Berserk, EldritchHex, FrenziedBloodlust, Poison, ShiftingNightmare, Vulnerable, Tough, MaddeningWhispers, TimeDilation, RealityBleed



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

class EldritchCurse(CardBase):
    def __init__(self):
        super().__init__("Eldritch Curse", 2, "Apply 2 Eldritch Hex and deal 3 damage.", requires_target=True)

    async def on_play(self, state, being, target):
        target.statuses.append(EldritchHex(stacks=2, remaining_turns=2))
        await state.deal_damage(source=being, target=target, amount=3)

class BloodRitual(CardBase):
    def __init__(self):
        super().__init__("Blood Ritual", 3, "Gain Frenzied Bloodlust with 4 power for 3 turns.", requires_target=False)

    async def on_play(self, state, being, target):
        being.statuses.append(FrenziedBloodlust(power_boost=4, remaining_turns=3))

class NightmareVisions(CardBase):
    def __init__(self):
        super().__init__("Nightmare Visions", 1, "Apply Shifting Nightmare for 3 turns and draw a card.", requires_target=True)

    async def on_play(self, state, being, target):
        target.statuses.append(ShiftingNightmare(remaining_turns=3))
        await being.draw(1)

class ToughShell(CardBase):
    def __init__(self):
        super().__init__("Tough Shell", 2, "Gain 8 block and Tough status for 2 turns.", requires_target=False)
    
    async def on_play(self, state, being, target):
        being.block += 8
        being.statuses.append(Tough(remaining_turns=2))

class WhispersOfMadness(CardBase):
    def __init__(self):
        super().__init__("Whispers of Madness", 2, "Apply Maddening Whispers for 3 turns and draw a card.", requires_target=True)

    async def on_play(self, state, being, target):
        target.statuses.append(MaddeningWhispers(remaining_turns=3))
        await being.draw(1)

class TemporalDistortion(CardBase):
    def __init__(self):
        super().__init__("Temporal Distortion", 3, "Apply Time Dilation for 2 turns and gain 10 block.", requires_target=True)

    async def on_play(self, state, being, target):
        target.statuses.append(TimeDilation(remaining_turns=2))
        being.block += 10

class RealityTear(CardBase):
    def __init__(self):
        super().__init__("Reality Tear", 2, "Deal 7 damage and apply Reality Bleed for 3 turns.", requires_target=True)

    async def on_play(self, state, being, target):
        await state.deal_damage(source=being, target=target, amount=7)
        target.statuses.append(RealityBleed(remaining_turns=3))

class ChaosEmbrace(CardBase):
    def __init__(self):
        super().__init__("Chaos Embrace", 3, "Apply Reality Bleed and Shifting Nightmare for 2 turns.", requires_target=True)

    async def on_play(self, state, being, target):
        target.statuses.append(RealityBleed(remaining_turns=2))
        target.statuses.append(ShiftingNightmare(remaining_turns=2))

class TimeLoop(CardBase):
    def __init__(self):
        super().__init__("Time Loop", 1, "Apply Time Dilation to yourself for 1 turn and draw 2 cards.", requires_target=False)

    async def on_play(self, state, being, target):
        being.statuses.append(TimeDilation(remaining_turns=1))
        await being.draw(2)

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

class StatusMirror(CardBase):
    def __init__(self):
        super().__init__("Status Mirror", 2, "Copy all status effects from target to yourself.", requires_target=True)

    async def on_play(self, state, being, target):
        for status in target.statuses:
            being.statuses.append(status.__class__(remaining_turns=status.remaining_turns))

class TimeStop(CardBase):
    def __init__(self):
        super().__init__("Time Stop", 3, "Double the duration of all your status effects.", requires_target=False)

    async def on_play(self, state, being, target):
        for status in being.statuses:
            status.remaining_turns *= 2

class StatusThief(CardBase):
    def __init__(self):
        super().__init__("Status Thief", 2, "Transfer all positive status effects from target to yourself.", requires_target=True)

    async def on_play(self, state, being, target):
        positive_statuses = [Berserk, Tough]  # List of positive status effect classes
        for status in target.statuses[:]:  # Create a copy of the list to modify during iteration
            if any(isinstance(status, pos_status) for pos_status in positive_statuses):
                being.statuses.append(status)
                target.statuses.remove(status)


def default_deck():
    """
    Default deck for the player.
    """
    all_cards = [BasicAttack(), BasicBlock(), BasicHeal(), BasicDraw(),
                 PoisonFlask(), BerserkerPotion(), VoidEmbrace(), EldritchCurse(),
                 BloodRitual(), NightmareVisions(), ToughShell(),
                 WhispersOfMadness(), TemporalDistortion(), RealityTear(),
                 ChaosEmbrace(), TimeLoop(), PurifyingLight(), EnergyInfusion(),
                 StatusMirror(), TimeStop(), StatusThief()]
    deck = []
    for _ in range(10):
        deck.append(random.choice(all_cards))
    shuffle(deck)
    return deck