from enum import Enum
import re
from typing import Optional, Tuple

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


class AudioCodec(str, Enum):
    """Container/codec for extracted audio."""

    mp3 = "mp3"
    m4a = "m4a"
    opus = "opus"
    flac = "flac"
    wav = "wav"
    vorbis = "vorbis"


class AudioQuality(str, Enum):
    """Target audio bitrate (kbps), or best available."""

    q128 = "128"
    q192 = "192"
    q256 = "256"
    q320 = "320"
    best = "best"


class VideoQuality(str, Enum):
    """Maximum video resolution."""

    best = "best"
    q2160p = "2160p"
    q1440p = "1440p"
    q1080p = "1080p"
    q720p = "720p"
    q480p = "480p"
    q360p = "360p"


# Same syntax as yt-dlp's --cookies-from-browser:
#   BROWSER[+KEYRING][:PROFILE][::CONTAINER]
_BROWSER_SPEC_RE = re.compile(
    r"""(?x)
        (?P<name>[^+:]+)
        (?:\s*\+\s*(?P<keyring>[^:]+))?
        (?:\s*:\s*(?!:)(?P<profile>.+?))?
        (?:\s*::\s*(?P<container>.+))?
    """
)


def resolve_cookies(
    cookie_file: Optional[str],
    cookies_from_browser: Optional[str],
) -> Tuple[Optional[str], Optional[tuple]]:
    """Validate the CLI cookie options and convert them for yt-dlp."""
    if cookie_file and cookies_from_browser:
        raise typer.BadParameter(
            "Use either --cookies or --cookies-from-browser, not both.",
            param_hint="--cookies",
        )

    if cookies_from_browser:
        m = _BROWSER_SPEC_RE.fullmatch(cookies_from_browser.strip())
        if not m:
            raise typer.BadParameter(
                f"Invalid value '{cookies_from_browser}'. Expected "
                "BROWSER[:PROFILE][+KEYRING][::CONTAINER], e.g. 'firefox' or 'chrome:Default'.",
                param_hint="--cookies-from-browser",
            )
        from yt_dlp.cookies import SUPPORTED_BROWSERS, SUPPORTED_KEYRINGS

        name = m.group("name").strip().lower()
        if name not in SUPPORTED_BROWSERS:
            raise typer.BadParameter(
                f"Unsupported browser '{name}'. Supported: {', '.join(sorted(SUPPORTED_BROWSERS))}.",
                param_hint="--cookies-from-browser",
            )
        keyring = m.group("keyring")
        if keyring is not None:
            keyring = keyring.strip().upper()
            if keyring not in SUPPORTED_KEYRINGS:
                raise typer.BadParameter(
                    f"Unsupported keyring '{keyring}'. Supported: {', '.join(sorted(SUPPORTED_KEYRINGS))}.",
                    param_hint="--cookies-from-browser",
                )
        # yt-dlp expects the tuple (browser, profile, keyring, container)
        return None, (name, m.group("profile"), keyring, m.group("container"))

    return (str(cookie_file) if cookie_file else None), None


@app.command("mp3")
def mp3(
    url: str = typer.Argument(..., help="Video or playlist URL."),
    quality: AudioQuality = typer.Option(
        AudioQuality.q320,
        "--quality",
        "-q",
        show_choices=True,
        case_sensitive=False,
        help="Audio bitrate in kbps, or 'best' for the highest available.",
    ),
    codec: AudioCodec = typer.Option(
        AudioCodec.mp3,
        "--codec",
        "-c",
        show_choices=True,
        case_sensitive=False,
        help="Output audio format.",
    ),
    no_embed: bool = typer.Option(
        False,
        "--no-embed",
        help="Do NOT embed the thumbnail as cover art inside the audio file.",
    ),
    keep_thumbnail: bool = typer.Option(
        False,
        "--keep-thumbnail",
        "-k",
        help="Also save the thumbnail as a separate image file in the Thumbnails folder.",
    ),
    no_playlist: bool = typer.Option(
        False,
        "--no-playlist",
        help="If the URL is a playlist link, download ONLY the single video it points to.",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        metavar="DIR",
        help="Save files to this directory instead of the default one.",
    ),
    cookie_file: Optional[str] = typer.Option(
        None,
        "--cookies",
        metavar="FILE",
        help="Netscape-format cookies file (exported from a browser). Helps with "
        "age-restricted videos and bot-check blocks.",
    ),
    cookies_from_browser: Optional[str] = typer.Option(
        None,
        "--cookies-from-browser",
        metavar="BROWSER[:PROFILE][+KEYRING][::CONTAINER]",
        help="Load cookies directly from an installed browser "
        "(firefox, chrome, edge, chromium, brave, vivaldi, opera, safari...). "
        "e.g. 'firefox' or 'chrome:Default'.",
    ),
):
    """
    Download audio with embedded cover art + metadata.

    By default you get MP3 at 320 kbps with the thumbnail embedded as
    album art and full ID3/metadata tags applied.

    \b
    Examples:
      cipher ytdl mp3 "https://youtube.com/watch?v=..."          # MP3 320k
      cipher ytdl mp3 "URL" -q best -c m4a                       # best m4a
      cipher ytdl mp3 "URL" --no-embed -k                        # keep thumb as file
      cipher ytdl mp3 "playlist-url"                             # whole playlist
      cipher ytdl mp3 "URL" --no-playlist                        # just that video
      cipher ytdl mp3 "URL" -o ~/Music                           # custom folder
      cipher ytdl mp3 "URL" --cookies-from-browser firefox       # authenticated
    """
    try:
        cfile, cbrowser = resolve_cookies(cookie_file, cookies_from_browser)
    except typer.BadParameter as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        raise typer.Exit(code=2)

    ok = ytdl.download_audio(
        url=url,
        codec=codec.value,
        quality=quality.value,
        embed_thumbnail=not no_embed,
        keep_thumbnail=keep_thumbnail,
        no_playlist=no_playlist,
        output_dir=output,
        cookie_file=cfile,
        cookies_from_browser=cbrowser,
    )
    if not ok:
        raise typer.Exit(code=1)


@app.command("mp4")
def mp4(
    url: str = typer.Argument(..., help="Video or playlist URL."),
    quality: VideoQuality = typer.Option(
        VideoQuality.best,
        "--quality",
        "-q",
        show_choices=True,
        case_sensitive=False,
        help="Maximum video resolution (falls back to the closest available).",
    ),
    subs: bool = typer.Option(
        False,
        "--subs",
        help="Download subtitles as separate .vtt/.srt files next to the video.",
    ),
    embed_subs: bool = typer.Option(
        False,
        "--embed-subs",
        help="Embed subtitles INSIDE the MP4 file (implies --subs).",
    ),
    sub_langs: str = typer.Option(
        "en,ar",
        "--sub-langs",
        metavar="LANGS",
        help="Comma-separated subtitle language codes to fetch (e.g. 'en' or 'en,ar').",
    ),
    no_playlist: bool = typer.Option(
        False,
        "--no-playlist",
        help="If the URL is a playlist link, download ONLY the single video it points to.",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        metavar="DIR",
        help="Save files to this directory instead of the default one.",
    ),
    cookie_file: Optional[str] = typer.Option(
        None,
        "--cookies",
        metavar="FILE",
        help="Netscape-format cookies file (exported from a browser). Helps with "
        "age-restricted videos and bot-check blocks.",
    ),
    cookies_from_browser: Optional[str] = typer.Option(
        None,
        "--cookies-from-browser",
        metavar="BROWSER[:PROFILE][+KEYRING][::CONTAINER]",
        help="Load cookies directly from an installed browser "
        "(firefox, chrome, edge, chromium, brave, vivaldi, opera, safari...).",
    ),
):
    """
    Download video as MP4.

    Video and audio streams are downloaded separately (best quality) and
    merged with ffmpeg into a single MP4 file.

    \b
    Examples:
      cipher ytdl mp4 "URL"                        # best quality MP4
      cipher ytdl mp4 "URL" -q 1080p               # cap at 1080p
      cipher ytdl mp4 "URL" --embed-subs           # subtitles baked in
      cipher ytdl mp4 "URL" --subs --sub-langs en  # separate English subs
      cipher ytdl mp4 "playlist-url"               # whole playlist
    """
    langs = [lang.strip() for lang in sub_langs.split(",") if lang.strip()]
    if not langs:
        console.print("[bold red]Error:[/bold red] --sub-langs cannot be empty.")
        raise typer.Exit(code=2)

    try:
        cfile, cbrowser = resolve_cookies(cookie_file, cookies_from_browser)
    except typer.BadParameter as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        raise typer.Exit(code=2)

    ok = ytdl.download_video(
        url=url,
        quality=quality.value,
        no_playlist=no_playlist,
        output_dir=output,
        write_subs=subs or embed_subs,
        embed_subs=embed_subs,
        sub_langs=langs,
        cookie_file=cfile,
        cookies_from_browser=cbrowser,
    )
    if not ok:
        raise typer.Exit(code=1)


@app.command("info")
def info(
    url: str = typer.Argument(..., help="Video or playlist URL."),
    playlist: bool = typer.Option(
        False,
        "--playlist",
        "-p",
        help="Treat the URL as a playlist and list every item in it.",
    ),
    cookie_file: Optional[str] = typer.Option(
        None,
        "--cookies",
        metavar="FILE",
        help="Netscape-format cookies file, for private/age-restricted videos.",
    ),
    cookies_from_browser: Optional[str] = typer.Option(
        None,
        "--cookies-from-browser",
        metavar="BROWSER[:PROFILE][+KEYRING][::CONTAINER]",
        help="Load cookies directly from an installed browser.",
    ),
):
    """
    Show metadata without downloading anything.

    For a single video this shows title, channel, duration, views,
    upload date and URLs. Pass --playlist on a playlist URL to get a
    numbered listing of all items (handy before a big batch download).

    \b
    Examples:
      cipher ytdl info "URL"
      cipher ytdl info "playlist-url" --playlist
      cipher ytdl info "URL" --cookies-from-browser chrome   # private video
    """
    try:
        cfile, cbrowser = resolve_cookies(cookie_file, cookies_from_browser)
    except typer.BadParameter as e:
        console.print(f"[bold red]Error:[/bold red] {e.message}")
        raise typer.Exit(code=2)

    ok = ytdl.show_info(url, playlist=playlist, cookie_file=cfile, cookies_from_browser=cbrowser)
    if not ok:
        raise typer.Exit(code=1)
