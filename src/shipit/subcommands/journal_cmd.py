import asyncio
import datetime
import inspect
import os
import subprocess

import anyio
import openai
import typer
from importlib import import_module
from pathlib import Path

import yaml
from typer import Context

from typetemp.template.smart_template import SmartTemplate
from utils.complete import create
from utils.prompt_tools import timer
from shipit.shipit_project_config import (
    ShipitProjectConfig,
)  # Adjust the import path as necessary

app = typer.Typer()


@app.command()
def auto(ctx: Context, prompt: str):
    typer.echo(f"Generating {prompt} prompt...")


class ShipitTemplate(SmartTemplate):
    """Template for the message sent to the language model."""

    prompt = ""
    page = ""
    source = """
    # {{ page }}
    {{ prompt }}

    We are making a AI assistant to help coders with their calendar and code.
    """


@timer
async def render_pages_from_yaml(ctx: Context, yaml_file):
    with open(yaml_file, "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    async with anyio.create_task_group() as tg:
        for item in data:
            config = ctx.obj
            output_path = (
                Path(config.directory) / item["file"]
                if config.directory
                else Path(item["file"])
            )
            template = ShipitTemplate(**item)
            # template = ShipitTemplate(**item, config=None)
            template.to = str(output_path)
            tg.start_soon(template.render)


@app.command()
def render(ctx: Context):
    config = ctx.obj
    yaml_file = Path(__file__).parent / "pages.yaml"
    asyncio.run(render_pages_from_yaml(ctx, yaml_file))
    typer.echo("Pages rendered successfully.")


@app.command()
def build(ctx: Context):
    config = ctx.obj
    build_dir = Path(config.directory) if config.directory else Path(__file__).parent
    subprocess.run(["mdbook", "build"], cwd=build_dir)
    typer.echo("mdbook built successfully.")


@app.command()
def serve(ctx: Context):
    config = ctx.obj
    serve_dir = Path(config.directory) if config.directory else Path(__file__).parent
    subprocess.run(["mdbook", "serve"], cwd=serve_dir)
    typer.echo("mdbook is being served.")


@app.command()
def init(ctx: Context):
    config = ctx.obj
    init_dir = Path(config.directory) if config.directory else Path(__file__).parent
    subprocess.run(["mdbook", "init"], cwd=init_dir)
    typer.echo("mdbook initialized successfully.")


def generate_commit_message(context: str) -> str:
    return create(
        prompt=f"Generate a commit message for the following changes:\n{context}"
    )


@app.command()
def commit(ctx: Context):
    config = ctx.obj
    git_dir = Path(config.directory) if config.directory else Path(__file__).parent

    # Ensure we're in the right directory for Git operations
    os.chdir(git_dir)  # Get changes to be committed (for context)
    status = subprocess.check_output(["git", "status", "--porcelain"]).decode()
    if not status:
        typer.echo("No changes to commit.")
        return

    commit_message = generate_commit_message(status)

    # Add all changes
    subprocess.run(["git", "add", "."], check=True)

    # Commit with the generated message
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    typer.echo(f"Changes committed with message: {commit_message}")

