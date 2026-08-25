import typer
from typer import Context
from typing import Optional
from importlib import metadata
from rich.console import Console
from cipher.commands.ytdl import app as ytdl_app

from cipher.ui.banner import show_banner, show_command_list, show_footer


# Get version from pyproject.toml
__version__ = metadata.version('cipher-cli')
console = Console()

app = typer.Typer(
    name="cipher",
    help="Cipher CLI - A modular command-line toolkit.",
    invoke_without_command=True,
    rich_markup_mode="rich",
    no_args_is_help=False,
)


app.add_typer(ytdl_app, name="ytdl")


def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]Cipher CLI[/bold cyan] version: [magenta]{__version__}[/magenta]")
        raise typer.Exit()

@app.callback()
def main(
    ctx: Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version of cipher and exit.",
        callback=version_callback,
        is_eager=True
    ),
):
    if ctx.invoked_subcommand is None:
        show_banner(console)
        show_command_list(console)
        show_footer(console)


if __name__ == "__main__":
    app()