import typer
from nexon_cli.core.tutorial_manager import TutorialManager, Step


def tutorial():
    """
    Launch an interactive in‐terminal Nexon tutorial.
    """
    steps = [
        Step(
            title="Welcome",
            content=(
                "Welcome to Nexon! This tutorial will guide you through:\n"
                "1) Creating an environment\n"
                "2) Installing a package\n"
                "3) Running a tool by recipe\n"
                "4) Deploying to Kubernetes\n"
                "\nPress Next to begin."
            ),
            command=""
        ),
        Step(
            title="Create Environment",
            content="Step 1: Create a new environment called 'demo':",
            command="nexon create-env demo --role dev"
        ),
        Step(
            title="Install Package",
            content="Step 2: Install the Python importer and bring in 'requests':",
            command="nexon import-pypi 'requests>=2.28,<3.0'"
        ),
        Step(
            title="Run Tool",
            content="Step 3: Use the recipe to run 'requests' within the env:",
            command="nexon run demo requests"
        ),
        Step(
            title="Deploy to K8s",
            content="Step 4: Deploy your 'demo' env to Kubernetes:",
            command="nexon cluster-deploy demo --replicas 1"
        ),
        Step(
            title="Finished",
            content="🎉 You’re all set! Explore more with `nexon --help`.",
            command=""
        ),
    ]
    app = TutorialManager(steps)
    app.run()


app = typer.Typer(help="Interactive Nexon tutorial")
app.command("start")(tutorial)
