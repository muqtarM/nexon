from rich.console import Console
from rich.text import Text


console = Console()


class Logger:
    @staticmethod
    def info(message: str):
        console.print(f"[bold blue][INFO][/bold blue] {message}")

    @staticmethod
    def success(message: str):
        console.print(f"[bold green][SUCCESS][/bold green] {message}")

    @staticmethod
    def warning(message: str):
        console.print(f"[bold yellow][WARNING][/bold yellow] {message}")

    @staticmethod
    def error(message: str):
        console.print(f"[bold red][ERROR][/bold red] {message}")

    @staticmethod
    def title(message: str):
        console.print(f"[bold magenta]{message}")

    @staticmethod
    def critical(message: str):
        console.print(f"[bold red on white][CRITICAL][/bold red on white] {message}")


logger = Logger()
