
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing import Annotated, Literal
from pydantic import SecretStr
from card_base import CardBase
from typing_extensions import TypedDict, List
import inspect


import os



class Agents:
    def __init__(self):
        self.theme_agent_state = {
            "name": None,
            "theme": None,
            "history": []
        }
        self.theme_agent= create_theme_agent()
        self.target_agent = create_target_agent()

    def create_theme(self) -> tuple[str, str]:
        self.theme_agent_state =  self.theme_agent.invoke(self.theme_agent_state)
        self.theme_agent_state["history"].append(("theme", self.theme_agent_state["theme"]))
        return self.theme_agent_state["name"], self.theme_agent_state["theme"]

    def target(self, card: CardBase) -> Literal["self", "enemy"]:
        return self.target_agent.invoke({"card": card})["target"]

class ThemeState(TypedDict):
    # messages: Annotated[list, add_messages]
    name: str
    theme: str
    history: list[tuple[str, str]]

def create_theme_agent(): 

    # theme_generator_llm = ChatOpenAI(
    #     model="gpt-4o-mini",
    #     temperature=1
    # )

    theme_generator_llm = ChatOpenAI(
        model='deepseek-chat', 
        api_key=os.getenv("DEEPSEEK_API_KEY"), # type: ignore
        base_url='https://api.deepseek.com',
        temperature=1,
        max_completion_tokens=1024
    )

    # theme_namer_llm = ChatOpenAI(
    #     model="gpt-4o-mini",
    #     temperature=0.5
    # )

    theme_namer_llm = ChatOpenAI(
        model='deepseek-chat', 
        api_key=os.getenv("DEEPSEEK_API_KEY"), # type: ignore
        base_url='https://api.deepseek.com',
        temperature=.8,
        max_completion_tokens=1024
    )

    def theme_generator(state: ThemeState) -> ThemeState:
        messages = [
            ("system", "You are a theme generator for a roguelike deckbuilding card game. It has a lovecraftian, eldritch theme. The theme should be 1-2 sentences and contain the physical setting of the level, the vibe, potentially some species of creatures that live there. Keep in mind that you'll be generating a lot! so feel free to be creative and make it interesting. Not too serious, for instance 'The City of the Dead', 'Yggdrasil Tree Nursery And Store', 'Bottomless Pit Supervisory Trade School.' No need to provide a name, (that will be done later). Just provide the description. Thanks!"),
            ("user", f"Generate a theme for a card game. The history is: {state['history']}, so please make sure the new one is relatively"),
        ]
        
        response = theme_generator_llm.invoke(messages)
        theme = response.content  # Assuming the last message is the generated theme
        state["theme"] = theme # type: ignore
        return state

    def theme_namer(state: ThemeState) -> ThemeState:
        messages = [
            ("system", "Your job is to name a level based on a given theme for a roguelike deckbuilding card game. The name should be 1-2 words. It could be a proper noun or a noun-adjective pair. For instance, 'The City of the Dead', 'Yggdrasil Tree Nursery And Store', 'Bottomless Pit Supervisory Trade School.' Please return only the name, no other text."),
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

class TargetState(TypedDict):
    card: CardBase
    target: Literal["self", "enemy"]

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
        print(f"Targeting card: {card.name}, {card.description}, {card.cost} ")
        messages = [
            ("system", "You are a targeting system for a roguelike deckbuilding card game. I am going to give you a description and other information about a card, and you will respond with 'self' or 'enemy' as to which target the card should be played on. If the card is a buff or a heal, you should target yourself. If the card is a damage or a debuff, you should target the enemy. Only respond with 'self' or 'enemy', nothing else."),
            ("user", f"Here is the card: name: {card.name}, description: {card.description}, cost: {card.cost}, code: {inspect.getsource(card.__class__)}"),
        ]   
        response = targeting_system.invoke(messages)
        state["target"] = response.content

        print(f"Targeting system response: {state['target']}")
        return state

    workflow = StateGraph(TargetState)
    workflow.add_node("target_picker", target_picker)
    workflow.add_edge(START, "target_picker")
    workflow.add_edge("target_picker", END)
    return workflow.compile() 

