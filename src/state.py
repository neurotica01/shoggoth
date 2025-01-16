from functools import reduce
import random
import sys
from time import sleep
from agents import Agents
from being import Being, Enemy, Player
from card import default_deck, user_select_card_in_hand, user_select_target

BEFORE_GRAVEYARD = 0
AFTER_GRAVEYARD = 1

class State:
    def __init__(self):
        self.player = Player( "Player", 20, deck=default_deck())
        self.enemy = Enemy("Enemy", 20, deck=default_deck())

        self.player.draw(4)
        self.enemy.draw(4)

        self.beings = [self.player, self.enemy]
        random.shuffle(self.beings)
        
        self.turn = 0
        self.theme = []

        self.agents = Agents()
        self.theme.append(self.agents.create_theme())
        print(f"Welcome to S H O G G O T H")
        print(f"First level: {self.theme[-1][0]}")
        print(f"{self.theme[-1][1]}")
        while True:
            self.loop()


    def loop(self):
        sleep(1)
        self.check_win_condition()
        self.turn += 1
        he_who_plays = self.beings[self.turn % 2]


        if he_who_plays == self.player:
            self.player_turn()
        else:
            self.enemy_turn()


        self.check_win_condition()
        for status in self.enemy.statuses:
            status.on_game_loop(self, self.enemy)
            self.check_win_condition()
        
        for status in self.player.statuses:
            status.on_game_loop(self, self.player)
            self.check_win_condition()
        

    def player_turn(self):
        print("--------------------------------")
        print("Player turn start\n")
        self.player.draw(1)
        self.player.resources["energy"] += 2
        self.player.resources["energy"] = min(self.player.resources["energy"], 10)
        while True:
            print(f"\nPlayer HP: {self.player.hp}, Enemy HP: {self.enemy.hp}, \nPlayer energy: {self.player.resources['energy']}")
            card = user_select_card_in_hand(self, optional=True)
            if not card:
                print("You have no cards to play or opted to skip.")
                break
            elif card.cost > self.player.resources["energy"]:
                print("You don't have enough energy to play that card.")
                self.player.hand.append(card)
                continue
            if card and card.cost <= self.player.resources["energy"]:
                if card.requires_target:
                    target = user_select_target(self)
                else:
                    target = None
                card.on_play(self, self.player, target)
                self.player.resources["energy"] -= card.cost
                self.check_win_condition()
        print("Player turn over\n\n")


    def enemy_turn(self):
        print("--------------------------------")
        print("Enemy turn start\n")
        self.enemy.draw(1)
        self.enemy.resources["energy"] += 2
        self.enemy.resources["energy"] = min(self.enemy.resources["energy"], 10)
        while True:
            viable = [card for card in self.enemy.hand if card.cost <= self.enemy.resources["energy"]]
            if not viable:
                print("Enemy has no cards to play.")
                return
            card = random.choice(viable)
            self.enemy.hand.remove(card)
            # This is from the perspective of the enemy
            if self.agents.target(card) == "enemy":
                target = self.player
            else:
                target = self.enemy
            card.on_play(self, self.enemy, target)
            self.enemy.resources["energy"] -= card.cost
            self.check_win_condition()
        print("Enemy turn over\n\n")

    def check_win_condition(self):
        if self.player.hp <= 0:
            self.on_lose()
        if self.enemy.hp <= 0:
            self.on_win()

    def on_win(self):
        print("You win!")
        sys.exit()

    def on_lose(self):
        print("You lose!")
        sys.exit()


    def deal_damage(self, source: Being, target: Being, amount: int):
        print("\n damage calc")
        print(f"{source.name} deals {amount} base damage to {target.name}")
        with_source_mods = reduce(lambda x, y: y.on_deal_damage(self, source, target, x), source.statuses, amount)
        print(f"{source.name} would deal {with_source_mods} damage to {target.name} with mods")
        with_target_mods = reduce(lambda x, y: y.on_take_damage(self, source, target, x), target.statuses, with_source_mods)
        print(f"But {source.name} actually deals {with_target_mods} damage to {target.name} with target's mods")
        target.hp -= with_target_mods
        print("damage calc end\n")
        self.check_win_condition()

    def heal(self, target: Being, amount: int):
        print("\n heal calc")
        print(f"{target.name} heals {amount} HP")
        with_target_mods = reduce(lambda x, y: y.on_heal(self, target, x), target.statuses, amount)
        print(f"{target.name} actuallys heals {with_target_mods} HP with mods")
        target.hp += with_target_mods
        print("heal calc end\n")
        self.check_win_condition()

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
