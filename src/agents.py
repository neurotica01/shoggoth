import uuid
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Literal
from being import Being, Enemy
import status
from card_base import CardBase
from typing_extensions import List
import inspect
import os
import card
from random import gauss
import random
import sys


class ThemeResult(BaseModel):
    name: str
    theme: str

class ThemeGenerationContext(BaseModel):
    history: list[tuple[str, str]]

class EnemyResult(BaseModel):
    name: str
    backstory: str

class EnemyGenerationContext(BaseModel):
    level_desc: str
    personality: dict[str, float]
    arcana: str

class TargetResult(BaseModel):
    target: Literal["self", "enemy"]

class TargetContext(BaseModel):
    card: CardBase
    
    model_config = {'arbitrary_types_allowed': True}


class Agents:
    def __init__(self, log):
        self.log = log
        self.theme_history = []
        self.theme_generator_agent = create_theme_generator_agent()
        self.theme_namer_agent = create_theme_namer_agent()
        self.target_agent = create_target_agent()
        self.enemy_generator = create_enemy_generator()

    def create_theme(self) -> tuple[str, str]:
        # Generate theme description
        context = ThemeGenerationContext(history=self.theme_history)
        ulid = str(uuid.uuid4())
        theme_prompt = f"Trial number {ulid}. Generate a theme for a card game. The history is: {self.theme_history}, so please make sure the new one is relatively unique."
        
        theme_result = self.theme_generator_agent.run_sync(theme_prompt, deps=context)
        theme_description = theme_result.output
        
        # Generate name for the theme
        name_prompt = f"Trial number {ulid}. Generate a name for a card game theme. The theme is: {theme_description}. Please return only the name, no other text."
        name_result = self.theme_namer_agent.run_sync(name_prompt, deps=None)
        theme_name = name_result.output
        
        # Update history
        self.theme_history.append(("theme", theme_description))
        
        return theme_name, theme_description

    async def target(self, card: CardBase) -> Literal["self", "enemy"]:
        context = TargetContext(card=card)
        result = await self.target_agent.run(
            f"Here is the card: name: {card.name}, description: {card.description}, cost: {card.cost}, code: {inspect.getsource(card.__class__)}", 
            deps=context
        )
        return result.output.target

    def generate_enemy(self, level_desc: str) -> tuple[str, str, dict[str, float], str]:
        """Generate an enemy with name, backstory, personality traits, and arcana"""
        personality = generate_big5_scores()
        arcana = get_random_arcana()
        
        context = EnemyGenerationContext(
            level_desc=level_desc,
            personality=personality,
            arcana=arcana
        )
        
        prompt = f"Generate an enemy that lives in/is lord of/is stuck in {level_desc} and aligns with these traits:\nMajor Arcana: {arcana}\nPersonality: {personality}"
        result = self.enemy_generator.run_sync(prompt, deps=context)
        
        return (
            result.output.name,
            result.output.backstory,
            personality,
            arcana
        )

    def generate_enemy_card(self, enemy: Enemy, level_desc: str) -> str:
        card_generator = create_card_generator_agent()

        # Get source code using inspect
        card_base_code = inspect.getsource(CardBase)
        being_code = inspect.getsource(Being)
        # For modules with multiple classes, get the whole module
        status_code = inspect.getsource(sys.modules['status'])
        card_code = inspect.getsource(sys.modules['card'])

        prompt = f"""Here is the context code for reference:

        Card Base:
        {card_base_code}

        Being:
        {being_code}

        Status:
        {status_code}

        Existing Cards:
        {card_code}

        Now generate a card for this enemy and level:
        Enemy Name: {enemy.name}
        Enemy Backstory: {enemy.backstory}
        Enemy Personality: {enemy.personality}
        Level Description: {level_desc}
        """

        result = card_generator.run_sync(prompt, deps=None)
        return result.output

    def create_enemy_card(self, enemy: Enemy, level_desc: str) -> CardBase:
        # Generate the code
        card_code = self.generate_enemy_card(enemy, level_desc)
        
        # Execute the class definition
        exec(card_code, globals())
        
        # Get the class name and instantiate
        class_name = card_code.strip().split('class ')[-1].split('(')[0]
        return eval(f"{class_name}()")


def create_theme_generator_agent():
    return Agent(
        'openai:o4-mini-2025-04-16',
        output_type=str,
        deps_type=ThemeGenerationContext,
        system_prompt="""You are a theme generator for a roguelike deckbuilding card game. It has a lovecraftian, eldritch theme, also pynchonian whimsy, postmodernism, and paranoia. 
        The theme should be 1-2 sentences and contain the physical setting of the level, the vibe, potentially some species of creatures that live there. 
        Keep in mind that you'll be generating a lot! so feel free to be creative and make it interesting. Not too serious, for instance 'The City of the Dead', 
        'Yggdrasil Tree Nursery And Store', 'Bottomless Pit Supervisory Trade School.' No need to provide a name, (that will be done later). 
        Just provide the description. Thanks!""",
        model_settings={'temperature': 1.0}
    )

def create_theme_namer_agent():
    return Agent(
        'openai:gpt-4o',
        output_type=str,
        system_prompt="""Your job is to name a level based on a given theme for a roguelike deckbuilding card game.
        The name should be 1-2 words. It could be a proper noun or a noun-adjective pair. For instance, 'The City of the Dead', 
        'Yggdrasil Tree Nursery And Store', 'Bottomless Pit Supervisory Trade School.' Please return only the name, no other text. 
        The name should be unique, and not similar to any other names you've generated. Avoid the word abyssal""",
        model_settings={'temperature': 1.0}
    )

def create_target_agent():
    return Agent(
        'openai:gpt-4o',
        output_type=TargetResult,
        deps_type=TargetContext,
        system_prompt="You are a targeting system for a roguelike deckbuilding card game. I am going to give you a description and other information about a card, and you will respond with 'self' or 'enemy' as to which target the card should be played on. If the card is a buff or a heal, you should target yourself. If the card is a damage or a debuff, you should target the enemy. Only respond with 'self' or 'enemy', nothing else.",
        model_settings={'temperature': 0}
    ) 

def generate_big5_scores() -> dict[str, float]:
    """Generate normally distributed Big 5 personality scores with increased variance"""
    traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    return {trait: min(1.0, max(0.0, gauss(0.5, 0.3))) for trait in traits}

def get_random_arcana() -> str:
    """Return a random Major Arcana card"""
    arcana = [
        "The Fool", "The Magician", "The High Priestess", "The Empress", 
        "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
        "Strength", "The Hermit", "Wheel of Fortune", "Justice",
        "The Hanged Man", "Death", "Temperance", "The Devil",
        "The Tower", "The Star", "The Moon", "The Sun",
        "Judgement", "The World"
    ]
    return random.choice(arcana)

def create_enemy_generator():
    return Agent(
        'openai:o4-mini-2025-04-16',
        output_type=EnemyResult,
        deps_type=EnemyGenerationContext,
        system_prompt="""You are a generator for a Lovecraftian/Eldritch horror roguelike card game. Generate a name and short backstory 
        for an enemy that would fit in this setting. The backstory should be 2-3 sentences maximum. Make it unsettling 
        and weird, but not explicitly violent. Also pynchonian whimsy, postmodernism, and paranoia. The enemy should subtly align with their assigned Major Arcana card 
        and personality traits, but don't mention these directly in the output.
         
         Please return the name and only the name (no asterisks or other formatting) on the first line, and the backstory on the second line."""
    )

def create_card_generator_agent():
    return Agent(
        'openai:o4-mini-2025-04-16',
        output_type=str,
        system_prompt="""You are a card generator for a Lovecraftian/Eldritch horror roguelike card game. 
        You will be given information about an enemy and the level they're in, along with their personality traits and backstory.
        Your task is to generate a new card class that thematically fits with this enemy and level.
        
        The card should:
        1. Inherit from CardBase
        2. Have a unique name and thematic description
        3. Have a reasonable energy cost (1-3)
        4. Implement the on_play method with interesting mechanics
        5. Potentially use or create status effects
        6. Be balanced and not overpowered
        7. Reference the enemy's personality or backstory in some way
        
        Return only valid Python code for the card class. No explanations or other text.
        The code must be properly indented and ready to exec().""",
        model_settings={'temperature': 0.9}
    ) 

if __name__ == "__main__":
    agents = Agents(lambda x: print(x))
    level_name, level_desc = agents.create_theme()
    print(level_name, level_desc)
    enemy_name, enemy_backstory, enemy_personality, enemy_arcana = agents.generate_enemy(level_desc=level_desc)
    print(enemy_name, enemy_backstory, enemy_personality, enemy_arcana)
    enemy = Enemy(enemy_name, 20, deck=None, log_hook=lambda x: print(x), personality=enemy_personality, backstory=enemy_backstory)
    card = agents.create_enemy_card(enemy, level_desc)
    print(card)