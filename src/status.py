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

    def parent_on_game_loop(self, state: State, being: Being):
        self.on_game_loop(state, being)
        if not self.remaining_turns:
            return
        self.remaining_turns -= 1
        if self.remaining_turns == 0:
            being.statuses.remove(self)
        pass

    def on_game_loop(self, state: State, being: Being):
        pass

    def __add__(self, other):
        return self.remaining_turns + other.remaining_turns
    
    def __str__(self):
        return f"{self.name} ({self.remaining_turns} turn" + ("s" if self.remaining_turns != 1 else "") + ")"

    
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
    
class Confusion(Status):
    def __init__(self, remaining_turns: int):
        super().__init__("Confusion", 
                        "Damage dealt and taken becomes increasingly random", 
                        remaining_turns)
        self.instability = 0
    
    def on_deal_damage(self, state: State, source: Being, target: Being, amount: int) -> int:
        variance = random.uniform(-self.instability, self.instability)
        self.instability += 1
        return math.floor(amount * (1 + variance))
    
    def on_take_damage(self, state: State, source: Being, target: Being, amount: int) -> int:
        variance = random.uniform(-self.instability, self.instability)
        self.instability += 1
        return math.floor(amount * (1 + variance))

    def __add__(self, other):
        self.instability += other.instability
        self.remaining_turns = max(self.remaining_turns, other.remaining_turns)
        return self

class Frenzy(Status):
    def __init__(self, power_boost, remaining_turns):
        super().__init__("Frenzy", "Deal extra damage but suffer recoil.", remaining_turns)
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

