import os
import inspect

import typer
from importlib import import_module
from pathlib import Path

from typer import Context

from utils.complete import create
from utils.date_tools import next_friday
from shipit.shipit_project_config import (
    ShipitProjectConfig,
)  # Adjust the import path as necessary

app = typer.Typer()


def load_subcommands():
    script_dir = Path(__file__).parent
    subcommands_dir = script_dir / "subcommands"

    for filename in os.listdir(subcommands_dir):
        if filename.endswith("_cmd.py"):
            module_name = f"shipit.subcommands.{filename[:-3]}"
            module = import_module(module_name)
            if hasattr(module, "app"):
                app.add_typer(module.app, name=filename[:-7])


load_subcommands()


@app.callback()
def main(ctx: Context):
    config_file = Path().cwd() / "shipit_project.yaml"
    ctx.obj = ShipitProjectConfig.load(str(config_file))



@app.command()
def init(ctx: Context):
    """
    Initializes a new Shipit project and creates a configuration file.
    """
    # Prompt user for configuration details (can be expanded as needed)
    project_name = typer.prompt("Enter project name")
    description = typer.prompt("Enter project description")

    ship_date = typer.prompt(
        "Enter project due data in YYYY-MM-DD format", default=next_friday()
    )
    directory = typer.prompt("Enter directory for the project", default=str(Path.cwd()))

    # Create a new configuration object
    config = ShipitProjectConfig(
        project_name=project_name,
        description=description,
        ship_date=ship_date,
        directory=directory,
    )

    config.save()

    typer.echo(f"Initialized new Shipit project in {directory}")
    ctx.obj = config


def generate_context(task_description, max_tokens=200):
    """
    Generate context based on the task description.
    """
    try:
        prompt = f"Create a context with examples, labels, and instructions for the task: {task_description}"
        return create(prompt=prompt, max_tokens=max_tokens)
    except Exception as e:
        return f"Error generating context: {e}"

def solve_task_with_context(task_description, context, max_tokens=200):
    """
    Solve a task using the generated context.
    """
    try:
        prompt = f"Given the context: {context}\nSolve the task: {task_description}"
        return create(prompt=prompt, max_tokens=max_tokens)
    except Exception as e:
        return f"Error solving task: {e}"

@app.command()
def solve(task_description: str = typer.Option(..., prompt="Enter task description"),
         max_context_tokens: int = 200,
         max_solution_tokens: int = 200):
    """
    Automatically generate context and solve a task based on user input.
    """
    # Generate context for the task
    context = generate_context(task_description, max_context_tokens)
    typer.echo("Generated Context:\n" + context)

    # Solve the task with the generated context
    solution = solve_task_with_context(task_description, context, max_solution_tokens)
    typer.echo("Solution:\n" + solution)


@app.command()
def work(ctx: Context):
    """Workbench"""
    print(inspect.getsource(work))

if __name__ == "__main__":
    app()
