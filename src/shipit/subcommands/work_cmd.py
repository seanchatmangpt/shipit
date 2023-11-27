import asyncio
from textwrap import dedent
from lchop.tasks.hello_world_tasks import *

import typer
import pyperclip

from lchop.context.work_context import load_workflow
from utils.complete import acreate
from utils.create_prompts import create_python

app = typer.Typer(help="YAML workflow execution.")


@app.command("run")
def run_workflow_code(file: str = typer.Option(None, "--file", "-f")):
    """
    Run a workflow from a YAML file.
    """
    asyncio.run(_run_workflow_code(file))


async def _run_workflow_code(file):
    await load_workflow(file)
