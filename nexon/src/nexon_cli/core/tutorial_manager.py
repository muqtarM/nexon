from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button
from typing import List


class Step:
    def __init__(self, title: str, content: str, command: str):
        self.title = title
        self.content = content
        self.command = command


class TutorialManager(App):
    """
    A step-by-step TUI tutorial for Nexon.
    """

    CSS_PATH = None  # can add custom styling

    def __init__(self, steps: List[Step]):
        super().__init__()
        self.steps = steps
        self.current = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self.steps[self.current].content, id="content")
        yield Static(f"> Command: {self.steps[self.current].command}", id="command")
        yield Button("Next", id="next")
        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "next":
            self.current += 1
            if self.current >= len(self.steps):
                self.exit()
                return
            self.query_one("#content", Static).update(self.steps[self.current].content)
            self.query_one("#command", Static).update(f"> Command: {self.steps[self.current].command}")
