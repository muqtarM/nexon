import typer
from nexon_cli.core.launcher import launch_application


def launch_app(app_name: str):
    """
    Launch an app (Maya, Houdini, Unreal) inside the active environment.
    :return:
    """
    launch_application(app_name)
