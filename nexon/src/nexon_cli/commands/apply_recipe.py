import typer
from nexon_cli.core.recipe_manager import RecipeManager


def apply_recipe_cmd(recipe_name: str):
    """
    Apply a project-specific recipe to its base environment.
    """
    rm = RecipeManager()
    try:
        rm.apply_recipe(recipe_name)
        typer.secho(f"Recipe applied: {recipe_name}", fg="green")
    except Exception as e:
        typer.secho(f"Error applying recipe: {e}", fg="red")
        raise typer.Exit(1)