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

class State:
    def __init__(self, log_callback, user_select, status_bar_update):
        self.log = log_callback
        self.user_select = user_select
        self.status_bar_update = status_bar_update
        
        self.turn = 0
        self.theme = []

        self.agents = Agents(self.log)
        hardcoded_theme = ("Luminous Sporewatch", "A sprawling, bioluminescent fungal forest where towering mushrooms pulse with eerie light, and the air hums with the whispers of sentient spores. Strange, insectoid creatures with too many eyes scuttle between the stalks, while gelatinous, translucent beings ooze through the undergrowth, absorbing anything they touch. The vibe is unsettling yet mesmerizing, as if the forest itself is alive and watching.")
        self.theme.append(hardcoded_theme)
        # self.theme.append(self.agents.create_theme())

        self.player = Player( "Player", 20, deck=default_deck(), log_hook=self.log)
        
        enemy_name, enemy_backstory, enemy_personality, _ = self.agents.generate_enemy(self.theme[0][1])
        self.enemy = Enemy(enemy_name, 20, deck=default_deck(), log_hook=self.log, personality=enemy_personality, backstory=enemy_backstory)

        self.beings = [self.enemy, self.player]
        random.shuffle(self.beings)


    def status(self):
        return str(self.player) + "\n" + str(self.enemy)

    async def loop(self):
        await self.player.draw(5)
        await self.enemy.draw(5)

        while True:
            self.check_win_condition()
            self.turn += 1
            he_who_plays = self.beings[self.turn % 2]
            await self.take_turn(he_who_plays)
            for status in he_who_plays.statuses:
                await self.log(f"Applying {str(status)} to {he_who_plays.name}: {status.description}", )
                status.parent_on_game_loop(self, he_who_plays)
                self.check_win_condition()

    async def take_turn(self, being):
        is_player = isinstance(being, Player)
        await self.status_bar_update()
        await self.log(f"{being.name} turn start\n")
        
        # Draw phase
        await being.draw(1)
        being.resources["energy"] += 2
        being.resources["energy"] = min(being.resources["energy"], 10)
        await self.status_bar_update()
        # Play cards phase
        while True:
            if is_player:
                card = await self.user_select("Select a card to play", self.card_selector(being.hand), required=False)
                if not card:
                    await self.log("You have no cards to play or opted to skip.")
                    break
            else:
                viable = [card for card in being.hand if card.cost <= being.resources["energy"]]
                if not viable:
                    break
                card = random.choice(viable)

            # Check energy cost
            if card.cost > being.resources["energy"]:
                if is_player:
                    await self.log("You don't have enough energy to play that card.")
                    being.hand.append(card)
                    continue
                else:
                    break

            # Handle targeting
            if card.requires_target:
                if is_player:
                    target = await self.user_select("Select a target", self.target_selector(), required=True)
                else:
                    target = self.player if await self.agents.target(card) == "enemy" else being
            else:
                target = None

            # Play the card
            await self.log(f"{being.name} plays {str(card)}", user_ack=True)
            being.resources["energy"] -= card.cost
            await card.on_play(self, being, target)
            if card in being.hand:
                being.discard(card)
            self.status_bar_update()
            self.check_win_condition()

        await self.status_bar_update()
        await self.log(f"{being.name} turn over\n\n", user_ack=is_player)


    def check_win_condition(self):
        if self.player.hp <= 0:
            self.on_lose()
        if self.enemy.hp <= 0:
            self.on_win()

    def on_win(self):
        self.log("You win!", user_ack=True)
        sys.exit()

    def on_lose(self):
        self.log("You lose!", user_ack=True)
        sys.exit()


    async def deal_damage(self, source: Being, target: Being, amount: int):
        with_source_mods = reduce(lambda x, y: y.on_deal_damage(self, source, target, x), source.statuses, amount)
        with_target_mods = reduce(lambda x, y: y.on_take_damage(self, source, target, x), target.statuses, with_source_mods)
        target.hp -= with_target_mods

        await self.log(f"{source.name} deals {with_target_mods} damage ({amount} base) to {target.name}", user_ack=True)
        self.check_win_condition()

    async def heal(self, target: Being, amount: int):
        with_target_mods = reduce(lambda x, y: y.on_heal(self, target, x), target.statuses, amount)
        target.hp += with_target_mods
        await self.log(f"{target.name} heals {with_target_mods} HP ({amount} base)", user_ack=True)
        self.check_win_condition()

    def card_selector(self, cards: list[CardBase]) -> Dict[str, CardBase]:
        return { str(card):card for card in cards }
    
    def target_selector(self) -> Dict[str, Being]:
        return { str(target):target for target in self.beings }
