from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.table import Table


def show_banner(console: Console):
    banner = """
   
    
   █████████  █████ ███████████  █████   █████ ██████████ ███████████  
  ███▒▒▒▒▒███▒▒███ ▒▒███▒▒▒▒▒███▒▒███   ▒▒███ ▒▒███▒▒▒▒▒█▒▒███▒▒▒▒▒███ 
 ███     ▒▒▒  ▒███  ▒███    ▒███ ▒███    ▒███  ▒███  █ ▒  ▒███    ▒███ 
▒███          ▒███  ▒██████████  ▒███████████  ▒██████    ▒██████████  
▒███          ▒███  ▒███▒▒▒▒▒▒   ▒███▒▒▒▒▒███  ▒███▒▒█    ▒███▒▒▒▒▒███ 
▒▒███     ███ ▒███  ▒███         ▒███    ▒███  ▒███ ▒   █ ▒███    ▒███ 
 ▒▒█████████  █████ █████        █████   █████ ██████████ █████   █████
  ▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒ ▒▒▒▒▒        ▒▒▒▒▒   ▒▒▒▒▒ ▒▒▒▒▒▒▒▒▒▒ ▒▒▒▒▒   ▒▒▒▒▒ 
                                                                       
                                                                       
                                                                       
"""
    
    panel = Panel(
        Align.center(banner),
        style="bold green",
        border_style="magenta",
        title="[bold cyan]Welcome to Cipher - CLI[/bold cyan]",
        subtitle="[italic magenta]A modular command-line toolkit for automation, utilities, and digital workflows.[/italic magenta]",
    )
    console.print(panel)


def show_command_list(console: Console):
    table = Table(
        title="\n\n[bold cyan]Available Commands[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
    )

    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    table.add_row("ytdl mp3", "Download audio (mp3/m4a...) + embedded thumbnail & metadata")
    table.add_row("ytdl mp4", "Download video as MP4 with quality / subs options")
    table.add_row("ytdl info", "Show title, channel, duration, thumbnail URL (no download)")
    table.add_row("hash", "[dim](planned)[/dim]")
    table.add_row("encoding", "[dim](planned)[/dim]")

    console.print(Align.center(table))


def show_footer(console: Console):
    console.print(
        "\n[dim magenta]Use [italic green]'cipher --help'[/italic green] or [italic green]'cipher ytdl --help'[/italic green] for more information.[/dim magenta]"
    )
