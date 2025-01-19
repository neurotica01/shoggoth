from __future__ import annotations

import asyncio
from functools import reduce
import random
import sys
from typing import Dict
from agents import Agents
from being import Being, Enemy, Player
from card import default_deck
from card_base import CardBase

BEFORE_GRAVEYARD = 0
AFTER_GRAVEYARD = 1

class State:
    def __init__(self, log_callback, user_select):
        self.log = log_callback
        self.user_select = user_select

        self.player = Player( "Player", 20, deck=default_deck(), log_hook=self.log)
        self.enemy = Enemy("Enemy", 20, deck=default_deck(), log_hook=self.log)

        self.beings = [self.enemy, self.player]
        # random.shuffle(self.beings)
        
        self.turn = 0
        self.theme = []

        self.agents = Agents()
        hardcoded_theme = ("Luminous Sporewatch", "A sprawling, bioluminescent fungal forest where towering mushrooms pulse with eerie light, and the air hums with the whispers of sentient spores. Strange, insectoid creatures with too many eyes scuttle between the stalks, while gelatinous, translucent beings ooze through the undergrowth, absorbing anything they touch. The vibe is unsettling yet mesmerizing, as if the forest itself is alive and watching.")
        self.theme.append(hardcoded_theme)
        # self.theme.append(self.agents.create_theme())



    async def loop(self):
        await self.player.draw(4)
        await self.enemy.draw(4)

        while True:
            await self.log("\n--------------------------------\n")
            self.check_win_condition()
            self.turn += 1
            he_who_plays = self.beings[self.turn % 2]

            if he_who_plays == self.player:
                await self.player_turn()
            else:
                await self.enemy_turn()


            self.check_win_condition()
            for status in self.enemy.statuses:
                status.on_game_loop(self, self.enemy)
                self.check_win_condition()
            
            for status in self.player.statuses:
                status.on_game_loop(self, self.player)
                self.check_win_condition()
            await asyncio.sleep(.5)


    async def player_turn(self):
        await self.log("Player turn start")
        await self.player.draw(1)
        self.player.resources["energy"] += 2
        self.player.resources["energy"] = min(self.player.resources["energy"], 10)
        while True:
            card = await self.user_select(self.card_selector(self.player.hand), required=False)
            if not card:
                await self.log("You have no cards to play or opted to skip.")
                break
            elif card.cost > self.player.resources["energy"]:
                await self.log("You don't have enough energy to play that card.")
                self.player.hand.append(card)
                continue
            if card and card.cost <= self.player.resources["energy"]:
                if card.requires_target:
                    target = await self.user_select(self.target_selector(), required=True)
                else:
                    target = None
                await card.on_play(self, self.player, target)
                self.player.resources["energy"] -= card.cost
                self.check_win_condition()
        await self.log("Player turn over\n\n")


    async def enemy_turn(self):
        await self.log("Enemy turn start\n")
        await self.enemy.draw(1)
        self.enemy.resources["energy"] += 2
        self.enemy.resources["energy"] = min(self.enemy.resources["energy"], 10)
        while True:
            viable = [card for card in self.enemy.hand if card.cost <= self.enemy.resources["energy"]]
            if not viable:
                await self.log("Enemy has no cards to play.")
                return
            card = random.choice(viable)
            self.enemy.hand.remove(card)
            # This is from the perspective of the enemy
            if self.agents.target(card) == "enemy":
                target = self.player
            else:
                target = self.enemy
            await card.on_play(self, self.enemy, target)
            self.enemy.resources["energy"] -= card.cost
            self.check_win_condition()

    def check_win_condition(self):
        if self.player.hp <= 0:
            self.on_lose()
        if self.enemy.hp <= 0:
            self.on_win()

    def on_win(self):
        self.log("You win!")
        sys.exit()

    def on_lose(self):
        self.log("You lose!")
        sys.exit()


    async def deal_damage(self, source: Being, target: Being, amount: int):
        await self.log("\n\t>damage calc")
        await self.log(f"{source.name} deals {amount} base damage to {target.name}")
        with_source_mods = reduce(lambda x, y: y.on_deal_damage(self, source, target, x), source.statuses, amount)
        await self.log(f"{source.name} would deal {with_source_mods} damage to {target.name} with mods")
        with_target_mods = reduce(lambda x, y: y.on_take_damage(self, source, target, x), target.statuses, with_source_mods)
        await self.log(f"But {source.name} actually deals {with_target_mods} damage to {target.name} with target's mods")
        target.hp -= with_target_mods
        await self.log("\t>damage calc end\n")
        self.check_win_condition()

    async def heal(self, target: Being, amount: int):
        await self.log("\n\t>heal calc")
        await self.log(f"{target.name} heals {amount} HP")
        with_target_mods = reduce(lambda x, y: y.on_heal(self, target, x), target.statuses, amount)
        await self.log(f"{target.name} actuallys heals {with_target_mods} HP with mods")
        target.hp += with_target_mods
        await self.log("\t>heal calc end\n")
        self.check_win_condition()

    def card_selector(self, cards: list[CardBase]) -> Dict[str, CardBase]:
        return { "{}|\t{}|\t{}".format(card.name, card.cost, card.description):card for card in cards }
    
    def target_selector(self) -> Dict[str, Being]:
        return { "{} ({} HP)".format(target.name, target.hp):target for target in self.beings }