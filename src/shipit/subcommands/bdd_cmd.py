import asyncio

import typer
import os

from utils.file_tools import read, write
from utils.gherkin_parser import GherkinParser

app = typer.Typer()

@app.command("parse")
def generate_pytest_code(
    input_file: str = typer.Option(..., "-i", "--input", help="Input Gherkin feature file path"),
    output_file: str = typer.Option(None, "-o", "--output", help="Output Pytest code file path"),
):
    """
    Read the Gherkin feature from the input file and parse it.
    """
    asyncio.run(_generate_pytest_code(input_file, output_file))


async def _generate_pytest_code(input_file: str, output_file: str | None = None):
    """
    Read the Gherkin feature from the input file and parse it.
    """
    gherkin_text = await read(input_file)
    # Create a GherkinParser and generate Pytest code
    parser = GherkinParser(gherkin_text)
    pytest_code = parser.generate_pytest_code()

    output_file = await write(pytest_code, filename=output_file, extension="py")
    typer.echo(f"Pytest code written to {output_file}")


if __name__ == "__main__":
    app()
