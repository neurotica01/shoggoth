from ast import Tuple
import asyncio
from typing import Dict, List, Optional
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Log, RichLog, OptionList, ContentSwitcher, TextArea
from textual.widget import Widget
from textual.widgets.option_list import Option
from textual.events import Key
from rich.table import Table

from state import State


class Shoggoth(App):
    """A Game of Shoggoth"""
    CSS = """
    Log {
        height: 1fr; /* Make the Log fill remaining space */
    }
    """


    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("enter", "ack", "Ack"),
    ]

    def __init__(self, ):
        super().__init__()
        self.ack_event = asyncio.Event()
        self.selection_event = asyncio.Event()
        self.selection = None

        self.state = State(log_callback=self.log_callback,
                           user_select=self.user_select)

    async def log_callback(self, message: str, user_ack=False):
        l = self.query_one(RichLog)
        l.write(message)
        if user_ack:
            l.write("▼")
            self.ack_event.clear()
            await self.ack_event.wait()
            l.lines.pop()

    async def on_option_list_option_selected(self, message: OptionList.OptionSelected):
        self.selection_event.set()
        self.selection = message


    async def user_select(self, options: Dict[str, object], required=True):
        ol = self.query_one(OptionList)
        ol.clear_options()
        ol.add_options(options)
        ol.add_option(Option(prompt="Skip"))
        cs = self.query_one(ContentSwitcher)
        cs.current = "kh-inputs-options"
        ol.focus()
        await self.selection_event.wait()
        cs.current = "kh-inputs-textarea"
        self.query_one(RichLog).focus()
        if self.selection.option.prompt == "Skip": # type: ignore
            choice = None
        else:
            choice = options[self.selection.option.prompt] # type: ignore

        self.selection = None
        self.selection_event.clear()
        return choice

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with ContentSwitcher(initial="kh-inputs-options", id="kh-inputs"):
            yield OptionList(
                id="kh-inputs-options"
            )
            yield TextArea("Press 'q' to quit", disabled=True, id='kh-inputs-textarea')

        yield RichLog(max_lines=100,
                       auto_scroll=True,
                       wrap=True)
        yield Footer()

    async def on_mount(self) -> None:
        """
        Instead of doing async here directly, schedule the
        real start AFTER the UI is rendered.
        """
        self.query_one(RichLog).focus()
        self.run_worker(self.run_intro)


    async def run_intro(self) -> None:
        """This runs after the UI is definitely ready."""
        await self.log_callback("Welcome to S H O G G O T H", user_ack=True)
        await self.log_callback(f"First level: {self.state.theme[-1][0]}", user_ack=True)
        await self.log_callback(f"{self.state.theme[-1][1]}", user_ack=True)
        await self.state.loop()


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_ack(self) -> None:
        self.ack_event.set()


if __name__ == "__main__":
    app = Shoggoth()
    app.run()