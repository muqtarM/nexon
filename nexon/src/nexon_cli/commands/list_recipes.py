import typer
from nexon_cli.core.recipe_manager import RecipeManager


def list_recipes_cmd():
    """
    List all available project-specific recipes.
    """
    rm = RecipeManager()
    names = rm.list_recipes()
    if not names:
        typer.secho("(no recipes found)", fg="yellow")