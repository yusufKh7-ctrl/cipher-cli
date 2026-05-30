import typer
from rich.console import Console
from cipher.core.downloader import YTDL


app = typer.Typer()

ytdl =YTDL()


@app.command()
def mp3(url: str):
    """[italic cyan]Download Audio as [bold green]-mp3-[/bold green][/italic cyan]"""

    ytdl.download_audio(url)

@app.command()
def mp4(url: str):
    """[italic cyan]Download Video as [bold green]-mp4-[/bold green][/italic cyan]"""
    ytdl.download_video(url)