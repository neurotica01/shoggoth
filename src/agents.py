
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict, List


class Agents:
    def __init__(self):
        self.theme_agent_state = {
            "name": None,
            "theme": None,
            "history": []
        }
        self.theme_agent= create_theme_agent(self.theme_agent_state)


    def create_theme(self) -> tuple[str, str]:
        self.theme_agent_state =  self.theme_agent.invoke(self.theme_agent_state)
        self.theme_agent_state["history"].append(("theme", self.theme_agent_state["theme"]))
        return self.theme_agent_state["name"], self.theme_agent_state["theme"]

def create_theme_agent(State) -> StateGraph:
    class State(TypedDict):
        # messages: Annotated[list, add_messages]
        name: str
        theme: str
        history: list[tuple[str, str]]

    theme_generator_llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=1
    )

    theme_namer_llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5
    )

    def theme_generator(state: State) -> State:
        messages = [
            ("system", "You are a theme generator for a roguelike deckbuilding card game. It has a lovecraftian, eldritch theme. The theme should be 1-2 sentences and contain the physical setting of the level, the vibe, potentially some species of creatures that live there. Keep in mind that you'll be generating a lot! so feel free to be creative and make it interesting. Not too serious, for instance 'The City of the Dead', 'Yggdrasil Tree Nursery And Store', 'Bottomless Pit Supervisory Trade School.'"),
            ("user", f"Generate a theme for a card game. The history is: {state['history']}, so please make sure the new one is relatively"),
        ]
        
        response = theme_generator_llm.invoke(messages)
        theme = response.content  # Assuming the last message is the generated theme
        state["theme"] = theme
        return state

    def theme_namer(state: State) -> State:
        messages = [
            ("system", "Your job is to name a level based on a given theme for a roguelike deckbuilding card game. The name should be 1-2 words. It could be a proper noun or a noun-adjective pair. For instance, 'The City of the Dead', 'Yggdrasil Tree Nursery And Store', 'Bottomless Pit Supervisory Trade School.' Please return only the name, no other text."),
            ("user", f"Generate a theme for a card game. The theme is: {state['theme']}. Please return only the name, no other text."),
        ]
        response = theme_namer_llm.invoke(messages)
        name = response.content  # Assuming the last message is the generated name
        state["name"] = name
        return state

    workflow = StateGraph(State)
    workflow.add_node("theme_generator", theme_generator)
    workflow.add_node("theme_namer", theme_namer)
    workflow.add_edge(START, "theme_generator")
    workflow.add_edge("theme_generator", "theme_namer")
    workflow.add_edge("theme_namer", END)
    return workflow.compile()

if __name__ == "__main__":

    # agents = Agents()
    # name, theme = agents.create_theme()
    # print(name, theme)
    # name, theme = agents.create_theme()
    # print(name, theme)
    # name, theme = agents.create_theme()
    # print(name, theme)
    # name, theme = agents.create_theme()
    # print(name, theme)
    # name, theme = agents.create_theme()
    # print(name, theme)
