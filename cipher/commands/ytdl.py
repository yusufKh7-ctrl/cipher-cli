from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from cipher.core.downloader import YTDL

app = typer.Typer(
    name="ytdl",
    help="Download audio/video from YouTube (and any site yt-dlp supports).",
    no_args_is_help=True,
)
console = Console()
ytdl = YTDL()


@app.command("mp3")
def mp3(
    url: str = typer.Argument(..., help="Video or playlist URL"),
    quality: str = typer.Option(
        "320",
        "--quality",
        "-q",
        help="Audio quality: 128, 192, 256, 320, or best",
    ),
    codec: str = typer.Option(
        "mp3",
        "--codec",
        "-c",
        help="Audio codec: mp3, m4a, opus, flac, wav...",
    ),
    no_embed: bool = typer.Option(
        False,
        "--no-embed",
        help="Do NOT embed thumbnail into the audio file",
    ),
    keep_thumbnail: bool = typer.Option(
        False,
        "--keep-thumbnail",
        "-k",
        help="Also save the thumbnail as a separate image file",
    ),
    no_playlist: bool = typer.Option(
        False,
        "--no-playlist",
        help="Download only the single video, ignore playlist",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Custom output directory",
    ),
):
    """
    Download audio (default: MP3 320kbps) with embedded thumbnail + metadata.

    Examples:
      cipher ytdl mp3 "https://youtube.com/watch?v=..."
      cipher ytdl mp3 "URL" -q best -c m4a --keep-thumbnail
      cipher ytdl mp3 "playlist-url" --no-playlist
    """
    ytdl.download_audio(
        url=url,
        codec=codec,
        quality=quality,
        embed_thumbnail=not no_embed,
        keep_thumbnail=keep_thumbnail,
        no_playlist=no_playlist,
        output_dir=output,
    )


@app.command("mp4")
def mp4(
    url: str = typer.Argument(..., help="Video or playlist URL"),
    quality: str = typer.Option(
        "best",
        "--quality",
        "-q",
        help="Video quality: best, 1080p, 720p, 480p, 360p...",
    ),
    no_playlist: bool = typer.Option(
        False,
        "--no-playlist",
        help="Download only the single video, ignore playlist",
    ),
    subs: bool = typer.Option(
        False,
        "--subs",
        help="Download subtitles (manual + auto)",
    ),
    embed_subs: bool = typer.Option(
        False,
        "--embed-subs",
        help="Embed subtitles into the video file",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Custom output directory",
    ),
):
    """
    Download video as MP4.

    Examples:
      cipher ytdl mp4 "URL"
      cipher ytdl mp4 "URL" -q 1080p --embed-subs
    """
    ytdl.download_video(
        url=url,
        quality=quality,
        no_playlist=no_playlist,
        output_dir=output,
        write_subs=subs or embed_subs,
        embed_subs=embed_subs,
    )


@app.command("info")
def info(
    url: str = typer.Argument(..., help="Video URL"),
):
    """
    Show title, channel, duration, views, thumbnail URL... without downloading.
    """
    ytdl.show_info(url)
