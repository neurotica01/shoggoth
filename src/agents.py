import uuid
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing import Annotated, Literal
from pydantic import SecretStr
from being import Being, Enemy
import status
from card_base import CardBase
from typing_extensions import TypedDict, List
import inspect
import os
import card
from random import gauss
import random
import sys


class ThemeState(TypedDict):
    # messages: Annotated[list, add_messages]
    name: str
    theme: str
    history: list[tuple[str, str]]

class EnemyState(TypedDict):
    name: str
    backstory: str
    level_desc: str
    personality: dict[str, float]
    arcana: str

class TargetState(TypedDict):
    card: CardBase
    target: Literal["self", "enemy"]


class Agents:
    def __init__(self, log):
        self.log = log
        self.theme_agent_state = {
            "name": None,
            "theme": None,
            "history": []
        }
        self.theme_agent= create_theme_agent()
        self.target_agent = create_target_agent()
        self.enemy_generator = create_enemy_generator()

    def create_theme(self) -> tuple[str, str]:
        self.theme_agent_state =  self.theme_agent.invoke(self.theme_agent_state)
        self.theme_agent_state["history"].append(("theme", self.theme_agent_state["theme"]))
        return self.theme_agent_state["name"], self.theme_agent_state["theme"]

    def target(self, card: CardBase) -> Literal["self", "enemy"]:
        return self.target_agent.invoke({"card": card})["target"]

    def generate_enemy(self, level_desc: str) -> tuple[str, str, dict[str, float], str]:
        """Generate an enemy with name, backstory, personality traits, and arcana"""
        personality = generate_big5_scores()
        arcana = get_random_arcana()
        
        state = {
            "name": "",
            "level_desc": level_desc,
            "backstory": "",
            "personality": personality,
            "arcana": arcana
        }
        
        result = self.enemy_generator.invoke(state)
        return (
            result["name"],
            result["backstory"],
            result["personality"],
            result["arcana"]
        )

    def generate_enemy_card(self, enemy: Enemy, level_desc: str) -> str:
        card_generator = ChatAnthropic(
            model_name='claude-3-5-sonnet-20240620',
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url='https://api.anthropic.com',
            temperature=0.9,
            disable_streaming=True,
        )

        # Get source code using inspect
        card_base_code = inspect.getsource(CardBase)
        being_code = inspect.getsource(Being)
        # For modules with multiple classes, get the whole module
        status_code = inspect.getsource(sys.modules['status'])
        card_code = inspect.getsource(sys.modules['card'])

        messages = [
            ("system", """You are a card generator for a Lovecraftian/Eldritch horror roguelike card game. 
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
            The code must be properly indented and ready to exec().
            """),
            ("user", f"""Here is the context code for reference:

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
            """)
        ]

        response = card_generator.invoke(messages)
        return response.content

    def create_enemy_card(self, enemy: Enemy, level_desc: str) -> CardBase:
        # Generate the code
        card_code = self.generate_enemy_card(enemy, level_desc)
        
        # Execute the class definition
        exec(card_code, globals())
        
        # Get the class name and instantiate
        class_name = card_code.strip().split('class ')[-1].split('(')[0]
        return eval(f"{class_name}()")


def create_theme_agent(): 

    theme_generator_llm = ChatAnthropic(
        model_name='claude-3-5-sonnet-20240620', 
        api_key=os.getenv("ANTHROPIC_API_KEY"), # type: ignore
        base_url='https://api.anthropic.com',
        temperature=1,
        disable_streaming=True,
    )

    theme_namer_llm = ChatAnthropic(
        model_name='claude-3-5-sonnet-20240620', 
        api_key=os.getenv("ANTHROPIC_API_KEY"), # type: ignore
        base_url='https://api.anthropic.com',
        temperature=1,
        disable_streaming=True,
    )

    # theme_generator_llm = ChatOpenAI(
    #     model='deepseek-chat', 
    #     api_key=os.getenv("DEEPSEEK_API_KEY"), # type: ignore
    #     base_url='https://api.deepseek.com',
    #     temperature=1,
    #     max_completion_tokens=1024
    # )

    # theme_namer_llm = ChatOpenAI(
    #     model='deepseek-chat', 
    #     api_key=os.getenv("DEEPSEEK_API_KEY"), # type: ignore
    #     base_url='https://api.deepseek.com',
    #     temperature=.8,
    #     max_completion_tokens=1024
    # )

    def theme_generator(state: ThemeState) -> ThemeState:
        ulid = str(uuid.uuid4())
        messages = [
            ("system", """You are a theme generator for a roguelike deckbuilding card game. It has a lovecraftian, eldritch theme, also pynchonian whimsy, postmodernism, and paranoia. 
            The theme should be 1-2 sentences and contain the physical setting of the level, the vibe, potentially some species of creatures that live there. 
            Keep in mind that you'll be generating a lot! so feel free to be creative and make it interesting. Not too serious, for instance 'The City of the Dead', 
            'Yggdrasil Tree Nursery And Store', 'Bottomless Pit Supervisory Trade School.' No need to provide a name, (that will be done later). 
            Just provide the description. Thanks!"""),
            ("user", f"Trial number {ulid}"),
            ("user", f"Generate a theme for a card game. The history is: {state['history']}, so please make sure the new one is relatively"),
        ]
        
        response = theme_generator_llm.invoke(messages)
        theme = response.content  # Assuming the last message is the generated theme
        state["theme"] = theme # type: ignore
        return state

    def theme_namer(state: ThemeState) -> ThemeState:
        ulid = str(uuid.uuid4())
        messages = [
            ("system", """Your job is to name a level based on a given theme for a roguelike deckbuilding card game.
              The name should be 1-2 words. It could be a proper noun or a noun-adjective pair. For instance, 'The City of the Dead', 
              'Yggdrasil Tree Nursery And Store', 'Bottomless Pit Supervisory Trade School.' Please return only the name, no other text. 
              The name should be unique, and not similar to any other names you've generated. Avoid the word abyssal"""
             ),
             ("user", f"Trial number {ulid}"),
            ("user", f"Generate a theme for a card game. The theme is: {state['theme']}. Please return only the name, no other text."),
        ]
        response = theme_namer_llm.invoke(messages)
        name = response.content  # Assuming the last message is the generated name
        state["name"] = name # type: ignore
        return state

    workflow = StateGraph(ThemeState)
    workflow.add_node("theme_generator", theme_generator)
    workflow.add_node("theme_namer", theme_namer)
    workflow.add_edge(START, "theme_generator")
    workflow.add_edge("theme_generator", "theme_namer")
    workflow.add_edge("theme_namer", END)
    return workflow.compile()

def create_target_agent():
    targeting_system = llm = ChatOpenAI(
        model='deepseek-chat', 
        api_key=os.getenv("DEEPSEEK_API_KEY"), # type: ignore
        base_url='https://api.deepseek.com',
        temperature=0,
        max_completion_tokens=1024
    )

    def target_picker(state: TargetState) -> TargetState:
        card = state['card']
        # print(f"Targeting card: {card.name}, {card.description}, {card.cost} ")
        messages = [
            ("system", "You are a targeting system for a roguelike deckbuilding card game. I am going to give you a description and other information about a card, and you will respond with 'self' or 'enemy' as to which target the card should be played on. If the card is a buff or a heal, you should target yourself. If the card is a damage or a debuff, you should target the enemy. Only respond with 'self' or 'enemy', nothing else."),
            ("user", f"Here is the card: name: {card.name}, description: {card.description}, cost: {card.cost}, code: {inspect.getsource(card.__class__)}"),
        ]   
        response = targeting_system.invoke(messages)
        state["target"] = response.content

        # print(f"Targeting system response: {state['target']}")
        return state

    workflow = StateGraph(TargetState)
    workflow.add_node("target_picker", target_picker)
    workflow.add_edge(START, "target_picker")
    workflow.add_edge("target_picker", END)
    return workflow.compile() 

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
    enemy_generator = ChatOpenAI(
        model='deepseek-chat',
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url='https://api.deepseek.com',
        max_completion_tokens=1024
    )

    def generate_enemy(state: EnemyState) -> EnemyState:
        messages = [
            ("system", """You are a generator for a Lovecraftian/Eldritch horro roguelike card game. Generate a name and short backstory 
            for an enemy that would fit in this setting. The backstory should be 2-3 sentences maximum. Make it unsettling 
            and weird, but not explicitly violent. Also pynchonian whimsy, postmodernism, and paranoia. The enemy should subtly align with their assigned Major Arcana card 
            and personality traits, but don't mention these directly in the output.
             
             Please return the name and only the name (no asterisks or other formatting) on the first line, and the backstory on the second line.
             """),
            ("user", f"Generate an enemy that lives in/is lord of/is stuck in {state['level_desc']} and aligns with these traits:\nMajor Arcana: {state['arcana']}\nPersonality: {state['personality']}")
        ]
        
        response = enemy_generator.invoke(messages)
        lines = response.content.split('\n')
        state["name"] = lines[0].strip()
        state["backstory"] = ' '.join(lines[1:]).strip()
        return state

    workflow = StateGraph(EnemyState)
    workflow.add_node("enemy_generator", generate_enemy)
    workflow.add_edge(START, "enemy_generator")
    workflow.add_edge("enemy_generator", END)
    return workflow.compile() 

if __name__ == "__main__":
    agents = Agents(lambda x: print(x))
    level_name, level_desc = agents.create_theme()
    print(level_name, level_desc)
    enemy_name, enemy_backstory, enemy_personality, enemy_arcana = agents.generate_enemy(level_desc=level_desc)
    print(enemy_name, enemy_backstory, enemy_personality, enemy_arcana)
    enemy = Enemy(enemy_name, 20, deck=None, log_hook=lambda x: print(x), personality=enemy_personality, backstory=enemy_backstory)
    card = agents.create_enemy_card(enemy, level_desc)
    print(card)