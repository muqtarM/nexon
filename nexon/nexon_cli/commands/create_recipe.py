import typer
from nexon_cli.core.recipe_manager import create_recipe


def create_recipe_cmd(recipe_name: str):
    """
    Create a new project-specific environment recipe.
    :param recipe_name:
    :return:
    """
    create_recipe(recipe_name)
