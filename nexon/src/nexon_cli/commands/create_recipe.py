import typer
from typing import Optional
from nexon_cli.core.recipe_manager import RecipeManager


def create_recipe_cmd(
    recipe_name: str,
    base_environment: Optional[str] = typer.Option(
        None, "--base-env", "Base environment to inherit from"
    ),
):
    """
    Create a new project-specific recipe.
    """
    rm = RecipeManager()
    try:
        rm.create_recipe(recipe_name, base_environment or "")
        typer.secho(f"Recipe created: {recipe_name}", fg="green")
    except Exception as e:
        typer.secho(f"Error creating recipe: {e}", fg="red")
        raise typer.Exit(1)

