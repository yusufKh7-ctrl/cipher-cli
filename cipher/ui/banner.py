from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.table import Table


console = Console()

def show_banner(console):
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
    
    panel = Panel(Align.center(banner), style="bold green", border_style="magenta", title="[bold cyan]Welcome to Cipher - CLI[/bold cyan]"
                  , subtitle="[italic magenta]A modular command-line toolkit for automation, utilities, and digital workflows.[/italic magenta]")
    console.print(panel)

def show_command_list(console):
    table = Table(title="\n\n[bold cyan]Available Commands[/bold cyan]", show_header=True, header_style="bold magenta", border_style="blue")

    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column(Align.center("Description"), style="magenta")

    table.add_row("ytdl [mp3/mp4]", "Download audio or video from YouTube.")
    table.add_row("hash", "comming soon...")
    table.add_row("encoding", "comming soon...")
    table.add_row("decoding", "comming soon...")

    console.print(Align.center(table))

def show_footer(console):
    console.print(
        "\n[dim magenta]Use [italic green]'cipher --help'[/italic green] for more information.[/dim magenta]"
    )
