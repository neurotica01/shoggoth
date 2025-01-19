from __future__ import annotations

import math
import random
# from state import BEFORE_GRAVEYARD, AFTER_GRAVEYARD


class Status:
    def __init__(self, name: str, description: str, remaining_turns: int):
        self.name: str = name
        self.description: str = description
        self.remaining_turns: int = remaining_turns
        
    def on_deal_damage(self, state: State, source: Being, target: Being, amount: int) -> int:
        return amount

    def on_take_damage(self, state: State, source: Being, target: Being, amount: int) -> int:
        return amount

    def on_heal(self, state: State, being: Being, amount: int) -> int:
        return amount

    def on_game_loop(self, state: State, being: Being):
        pass

    def __add__(self, other):
        return self.remaining_turns + other.remaining_turns

    
class Poison(Status):
    def __init__(self, amount: int, remaining_turns: int):
        super().__init__("Poison", "Damage over time", remaining_turns)
        self.amount = amount

    def on_game_loop(self, state: State, being: Being):
        being.hp -= self.amount

    def __add__(self, other):
        self.amount += other.amount
        self.remaining_turns = max(self.remaining_turns, other.remaining_turns)
        return self

class Regen(Status):
    def __init__(self, amount: int, remaining_turns: int):
        super().__init__("Regen", "Heal over time", remaining_turns)

    def on_game_loop(self, state: State, being: Being):
        state.heal(being, 1)

class Vulnerable(Status):
    def __init__(self, remaining_turns: int):
        super().__init__("Vulnerable", "Take more damage", remaining_turns)

    def on_take_damage(self, state: State, source: Being, target: Being, amount: int) -> int:
        return math.floor(amount * 1.5)
    
class Berserk(Status):
    def __init__(self, remaining_turns: int):
        super().__init__("Berserk", "Deal more damage", remaining_turns)

    def on_deal_damage(self, state: State, source: Being, target: Being, amount: int) -> int:
        return math.floor(amount * 1.25)

class Tough(Status):
    def __init__(self, remaining_turns: int):
        super().__init__("Tough", "Take less damage", remaining_turns)

    def on_take_damage(self, state: State, source: Being, target: Being, amount: int) -> int:
        return math.floor(amount * 0.75)
    
# class MindRot(Status):
#     def __init__(self, remaining_turns: int):
#         super().__init__("Mind Rot", "Hand destruction", remaining_turns)

#     def on_game_loop(self, state, being):
#         if (being.name == "Player"):
#             card = user_select_card_in_hand(being.hand)
#         else:
#             card = random.choice(being.hand)
#             being.hand.remove(card)

class EldritchHex(Status):
    def __init__(self, stacks, remaining_turns):
        super().__init__("Eldritch Hex", "A creeping curse that amplifies damage taken.", remaining_turns)
        self.stacks = stacks

    def on_take_damage(self, state, source, target, amount) -> int:
        return int(amount + self.stacks)

    def __add__(self, other):
        self.stacks += other.stacks
        self.remaining_turns = max(self.remaining_turns, other.remaining_turns)
        return self


class FrenziedBloodlust(Status):
    def __init__(self, power_boost, remaining_turns):
        super().__init__("Frenzied Bloodlust", "Deal extra damage but suffer recoil.", remaining_turns)
        self.power_boost = power_boost

    def on_deal_damage(self, state, source, target, amount) -> int:
        # Recoil hits the source
        recoil = self.power_boost // 2
        source.hp -= recoil
        return amount + self.power_boost

    def __add__(self, other):
        self.power_boost += other.power_boost
        self.remaining_turns = max(self.remaining_turns, other.remaining_turns)
        return self


class ShiftingNightmare(Status):
    def __init__(self, remaining_turns):
        super().__init__("Shifting Nightmare", 
                         "Randomly drains HP or grants a short-lived power boost each turn.", 
                         remaining_turns)

    def on_game_loop(self, state, being):
        """
        Each turn, there's a 50% chance to drain 2 HP.
        Otherwise, grants a temporary +2 attack bonus, 
        which is reset at the beginning of each new turn. 
        """
        
        # 50% chance for negative effect
        if state.random_chance(0.5):
            being.hp -= 2
        else:
            being.statuses.append(Berserk(remaining_turns=2))

    def __add__(self, other):
        self.remaining_turns = max(self.remaining_turns, other.remaining_turns)
        return self


# TODO: environment statuses probably need to be a different class
# class AcidFog(Status):
#     def __init__(self, remaining_turns: int):
#         super().__init__("Acid Fog", "Deal damage to all", remaining_turns)

#     def on_game_loop(self, state: State, being: Being):
#         for other in state.beings:
#             if other != being:
#                 other.hp -= 1
