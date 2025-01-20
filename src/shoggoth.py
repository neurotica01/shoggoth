import asyncio
from typing import Dict
from textual.containers import HorizontalScroll, Container
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, RichLog, OptionList, Static
from textual.widgets.option_list import Option

from state import State


class Shoggoth(App):
    """A Game of Shoggoth"""
    CSS = """
    HorizontalScroll {
        height: auto;
    }
    Container {
        height: auto;
    }
    OptionList {
        height: 8;
    }
    RichLog {
        height: 26;
    }
    """

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("enter", "ack", "Ack"),
    ]


    # ----- init UI -----

    def __init__(self, ):
        super().__init__()
        self.ack_event = asyncio.Event()
        self.selection_event = asyncio.Event()
        self.selection = None

        self.state = State(log_callback=self.log_callback,
                           user_select=self.user_select,
                           status_bar_update=self.update_status_bar)
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        s = Static(id='status-bar')
        s.styles.height = '2'
        with HorizontalScroll():
            yield s
        with Container():
            s = Static(id='title')
            yield s
            yield OptionList(
                id="user-select"
                )
        yield RichLog(
            id="log",
            max_lines=8,
            auto_scroll=True,
            wrap=True
        )
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
        await self.update_status_bar()
        await self.log_callback("Welcome to S H O G G O T H", user_ack=True)
        await self.log_callback(f"First level: {self.state.theme[-1][0]}", user_ack=True)
        await self.log_callback(f"{self.state.theme[-1][1]}", user_ack=True)
        await self.state.loop()

    async def update_status_bar(self):
        sb = self.query_one(Static)
        sb.update(self.state.status())
        
    # ----- hooks -----

    async def log_callback(self, message: str, user_ack=False):
        l = self.query_one(RichLog)
        l.write(message)
        if user_ack:
            l.write("> ")
            self.ack_event.clear()
            await self.ack_event.wait()

    async def user_select(self, message: str, options: Dict[str, object], required=True):
        await self.log_callback(message, user_ack=False)
        container = self.query_one(Container)
        container.disabled = False

        t = self.query_one('#title') # type: ignore
        t.update(message) # type: ignore

        ol = self.query_one(OptionList)
        ol.add_options(options)
        ol.add_option(Option(prompt="Skip"))
        ol.focus()

        await self.selection_event.wait()
        
        self.query_one(RichLog).focus()
        if self.selection.option.prompt == "Skip": # type: ignore
            choice = None
        else:
            choice = options[self.selection.option.prompt] # type: ignore


        ol.clear_options()
        t.update("") # type: ignore
        container.disabled = True
        self.selection = None
        self.selection_event.clear()

        container.disabled = True

        return choice

    # ----- callbacks -----

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_ack(self) -> None:
        self.ack_event.set()


    async def on_option_list_option_selected(self, message: OptionList.OptionSelected):
        self.selection_event.set()
        self.selection = message


if __name__ == "__main__":
    app = Shoggoth()
    app.run()