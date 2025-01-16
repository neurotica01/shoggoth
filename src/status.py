import math
import random
# from state import BEFORE_GRAVEYARD, AFTER_GRAVEYARD
from state import Player, State
from being import Being
from card import user_select_card_in_hand, user_select_target

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
    
class MindRot(Status):
    def __init__(self, remaining_turns: int):
        super().__init__("Mind Rot", "Hand destruction", remaining_turns)

    def on_game_loop(self, state: State, being: Being):
        if (isinstance(being, Player)):
            card = user_select_card_in_hand(being.hand)
        else:
            card = random.choice(being.hand)
            being.hand.remove(card)

# TODO: environment statuses probably need to be a different class
# class AcidFog(Status):
#     def __init__(self, remaining_turns: int):
#         super().__init__("Acid Fog", "Deal damage to all", remaining_turns)

#     def on_game_loop(self, state: State, being: Being):
#         for other in state.beings:
#             if other != being:
#                 other.hp -= 1
