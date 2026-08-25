from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Optional

import yt_dlp
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.panel import Panel

from cipher.core.config import AUDIO_DIR, VIDEO_DIR, THUMBNAIL_DIR, ensure_dirs

console = Console()

# Prefixes playlist downloads with "01 - ", "02 - ", ...
# Standalone downloads (no playlist_index) get no prefix at all.
PLAYLIST_PREFIX = "%(playlist_index&{} - |)s"


def _fmt_duration(seconds: Any) -> Optional[str]:
    """Format seconds as H:MM:SS or M:SS."""
    if seconds is None:
        return None
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return str(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def _fmt_date(raw: Any) -> Optional[str]:
    """Format a yt-dlp upload date (YYYYMMDD) as YYYY-MM-DD."""
    if isinstance(raw, str) and len(raw) == 8 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
    return raw


class _YtdlLogger:
    """Collects yt-dlp error messages so we can show a clean summary at the end."""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def debug(self, msg: str) -> None:
        pass

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        pass

    def error(self, msg: str) -> None:
        if msg and msg not in self.errors:
            self.errors.append(msg)


class YTDL:
    def __init__(self):
        ensure_dirs()

    # ------------------------------------------------------------------ #
    # UI helpers
    # ------------------------------------------------------------------ #

    def _make_progress(self, label: str):
        progress = Progress(
            SpinnerColumn("moon"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(
                style="blue",
                complete_style="magenta",
                finished_style="bold cyan",
            ),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False,
        )
        task_id = progress.add_task(f"[bold green]{label}...[/bold green]", total=None)
        return progress, task_id

    def _progress_hook(self, progress: Progress, task_id):
        def hook(d: dict):
            status = d.get("status")

            if status == "downloading":
                # Prefer the video title; fall back to the temp filename.
                title = (d.get("info_dict") or {}).get("title")
                filename = Path(d.get("filename", "")).name
                label = title or filename
                if len(label) > 50:
                    label = label[:47] + "..."
                progress.update(
                    task_id, description=f"[bold green]↓ {label}[/bold green]"
                )

                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    progress.update(task_id, completed=downloaded, total=total)
                else:
                    progress.update(task_id, completed=downloaded)

            elif status == "finished":
                filename = Path(d.get("filename", "")).name
                progress.update(
                    task_id,
                    description=f"[bold cyan]Processing:[/bold cyan] {filename}",
                )

        return hook

    def _thumbnail_saver(self):
        """
        Copy the thumbnail to Thumbnails/ *before* the EmbedThumbnail
        postprocessor runs, because EmbedThumbnail deletes the source file
        right after embedding it.
        """

        def hook(d: dict):
            # PP hooks carry the processor name under 'postprocessor'
            if d.get("postprocessor") != "EmbedThumbnail" or d.get("status") != "started":
                return
            info = d.get("info_dict") or {}
            for thumb in info.get("thumbnails") or []:
                src = thumb.get("filepath")
                if not src or not Path(src).exists():
                    continue
                try:
                    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
                    dest = THUMBNAIL_DIR / Path(src).name
                    if src != str(dest):
                        shutil.copy2(src, dest)
                except OSError:
                    pass  # non-fatal: embedding still proceeds normally

        return hook

    # ------------------------------------------------------------------ #
    # yt-dlp option builders
    # ------------------------------------------------------------------ #

    def _base_opts(
        self,
        outtmpl: Any,
        no_playlist: bool = False,
        cookie_file: Optional[str] = None,
        cookies_from_browser: Optional[tuple] = None,
    ) -> dict[str, Any]:
        opts = {
            "outtmpl": outtmpl,
            "noplaylist": no_playlist,
            "quiet": True,
            "no_warnings": True,
            # Skip broken/private entries in a playlist instead of aborting
            # the entire batch.
            "ignoreerrors": "only_download",
            "retries": 3,
            "fragment_retries": 3,
            "noprogress": True,  # we render our own Rich progress
        }

        # Authentication: use a Netscape-format cookie file exported from a
        # browser, or read cookies straight from an installed browser.
        # This helps with age-restricted / members-only videos and with
        # YouTube's "confirm you're not a bot" blocks.
        if cookie_file:
            opts["cookiefile"] = str(Path(cookie_file).expanduser())
        if cookies_from_browser:
            opts["cookiesfrombrowser"] = tuple(cookies_from_browser)

        return opts

    def _audio_opts(
        self,
        codec: str = "mp3",
        quality: str = "320",
        embed_thumbnail: bool = True,
        keep_thumbnail: bool = False,
        no_playlist: bool = False,
        output_dir: Optional[Path] = None,
        cookie_file: Optional[str] = None,
        cookies_from_browser: Optional[tuple] = None,
    ) -> dict[str, Any]:
        out_dir = output_dir or AUDIO_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        # "best" lets yt-dlp pick the highest quality available.
        preferredquality = "0" if quality == "best" else quality

        postprocessors: list[dict[str, Any]] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
                "preferredquality": preferredquality,
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
                "add_chapters": True,
            },
        ]

        if embed_thumbnail:
            postprocessors.append(
                {
                    "key": "EmbedThumbnail",
                    "already_have_thumbnail": False,
                }
            )

        opts = self._base_opts(
            outtmpl=str(out_dir / (PLAYLIST_PREFIX + "%(title)s.%(ext)s")),
            no_playlist=no_playlist,
            cookie_file=cookie_file,
            cookies_from_browser=cookies_from_browser,
        )

        opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": postprocessors,
                "writethumbnail": embed_thumbnail or keep_thumbnail,
            }
        )

        if keep_thumbnail:
            if embed_thumbnail:
                # Thumbnail lands next to the audio, EmbedThumbnail consumes
                # it, and our postprocessor hook copies it to Thumbnails/
                # before that happens.
                opts["postprocessor_hooks"] = [self._thumbnail_saver()]
            else:
                # No embedding -> nothing deletes the file, so send it
                # straight to Thumbnails/.
                opts["outtmpl"] = {
                    "default": str(out_dir / (PLAYLIST_PREFIX + "%(title)s.%(ext)s")),
                    "thumbnail": str(THUMBNAIL_DIR / "%(title)s.%(ext)s"),
                }

        return opts

    def _video_opts(
        self,
        quality: str = "best",
        no_playlist: bool = False,
        output_dir: Optional[Path] = None,
        write_subs: bool = False,
        embed_subs: bool = False,
        sub_langs: Optional[list[str]] = None,
        cookie_file: Optional[str] = None,
        cookies_from_browser: Optional[tuple] = None,
    ) -> dict[str, Any]:
        out_dir = output_dir or VIDEO_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        # Simple quality mapping
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        elif quality.endswith("p"):
            height = quality[:-1]
            fmt = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
        else:
            fmt = "bestvideo+bestaudio/best"

        opts = self._base_opts(
            outtmpl=str(out_dir / (PLAYLIST_PREFIX + "%(title)s.%(ext)s")),
            no_playlist=no_playlist,
            cookie_file=cookie_file,
            cookies_from_browser=cookies_from_browser,
        )
        opts.update(
            {
                "format": fmt,
                "merge_output_format": "mp4",
                "writesubtitles": write_subs or embed_subs,
                "writeautomaticsub": write_subs or embed_subs,
                "subtitleslangs": sub_langs or ["en", "ar"],
                "embedsubtitles": embed_subs,
            }
        )
        return opts

    # ------------------------------------------------------------------ #
    # Execution
    # ------------------------------------------------------------------ #

    def _run(self, url: str, opts: dict[str, Any], label: str) -> bool:
        """Run a download. Returns True on success, False otherwise."""
        logger = _YtdlLogger()

        opts = dict(opts)  # shallow copy
        opts["logger"] = logger

        ok = True
        progress, task_id = self._make_progress(label)
        opts["progress_hooks"] = [self._progress_hook(progress, task_id)]

        with progress:
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    retcode = ydl.download([url])
                ok = retcode == 0
            except yt_dlp.utils.DownloadError as e:
                console.print(f"[bold red]Download error:[/bold red] {e}")
                ok = False
            except KeyboardInterrupt:
                console.print("\n[yellow]Cancelled.[/yellow]")
                ok = False
            except Exception as e:
                console.print(f"[bold red]Unexpected error:[/bold red] {e}")
                ok = False

        if logger.errors:
            ok = False
            console.print(
                f"[bold red]{len(logger.errors)} item(s) failed:[/bold red]"
            )
            for err in logger.errors[:10]:
                console.print(f"  [red]•[/red] {err}")
            if len(logger.errors) > 10:
                console.print(f"  [dim]...and {len(logger.errors) - 10} more[/dim]")

        if ok:
            console.print("[bold green]✓ Done[/bold green]")
        return ok

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def download_audio(
        self,
        url: str,
        codec: str = "mp3",
        quality: str = "320",
        embed_thumbnail: bool = True,
        keep_thumbnail: bool = False,
        no_playlist: bool = False,
        output_dir: Optional[str] = None,
        cookie_file: Optional[str] = None,
        cookies_from_browser: Optional[tuple] = None,
    ) -> bool:
        """Download audio and (by default) embed thumbnail + metadata."""
        out = Path(output_dir).expanduser() if output_dir else None
        opts = self._audio_opts(
            codec=codec,
            quality=quality,
            embed_thumbnail=embed_thumbnail,
            keep_thumbnail=keep_thumbnail,
            no_playlist=no_playlist,
            output_dir=out,
            cookie_file=cookie_file,
            cookies_from_browser=cookies_from_browser,
        )
        ok = self._run(url, opts, "Downloading audio")
        if ok:
            console.print(f"[dim]Saved to:[/dim] [bold]{out or AUDIO_DIR}[/bold]")
        return ok

    def download_video(
        self,
        url: str,
        quality: str = "best",
        no_playlist: bool = False,
        output_dir: Optional[str] = None,
        write_subs: bool = False,
        embed_subs: bool = False,
        sub_langs: Optional[list[str]] = None,
        cookie_file: Optional[str] = None,
        cookies_from_browser: Optional[tuple] = None,
    ) -> bool:
        """Download video (mp4)."""
        out = Path(output_dir).expanduser() if output_dir else None
        opts = self._video_opts(
            quality=quality,
            no_playlist=no_playlist,
            output_dir=out,
            write_subs=write_subs,
            embed_subs=embed_subs,
            sub_langs=sub_langs,
            cookie_file=cookie_file,
            cookies_from_browser=cookies_from_browser,
        )
        ok = self._run(url, opts, "Downloading video")
        if ok:
            console.print(f"[dim]Saved to:[/dim] [bold]{out or VIDEO_DIR}[/bold]")
        return ok

    def show_info(
        self,
        url: str,
        playlist: bool = False,
        cookie_file: Optional[str] = None,
        cookies_from_browser: Optional[tuple] = None,
    ) -> bool:
        """Print useful metadata without downloading."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": not playlist,
            "extract_flat": "in_playlist" if playlist else False,
        }
        if cookie_file:
            opts["cookiefile"] = str(Path(cookie_file).expanduser())
        if cookies_from_browser:
            opts["cookiesfrombrowser"] = tuple(cookies_from_browser)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            console.print(f"[bold red]Error extracting info:[/bold red] {e}")
            return False
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
            return False

        if not info:
            console.print("[red]No info returned.[/red]")
            return False

        # Playlist mode: compact listing of every entry.
        if playlist and info.get("_type") == "playlist":
            entries = [e for e in (info.get("entries") or []) if e]
            table = Table(
                title=f"Playlist: {info.get('title') or url} "
                f"({len(entries)} items)",
                header_style="bold magenta",
                border_style="cyan",
            )
            table.add_column("#", style="bold cyan", justify="right")
            table.add_column("Title", style="white", overflow="fold")
            table.add_column("Duration", style="green", justify="right")
            for i, entry in enumerate(entries, start=1):
                duration = entry.get("duration")
                dur_str = _fmt_duration(duration) or "-"
                table.add_row(str(i), entry.get("title") or "?", dur_str)
            console.print(table)
            return True

        # Single video mode: detailed panel.
        duration_str = _fmt_duration(info.get("duration"))
        upload_str = _fmt_date(info.get("upload_date"))
        views = info.get("view_count")
        views_str = f"{views:,}" if isinstance(views, int) else None

        description = (info.get("description") or "").strip()
        if len(description) > 300:
            description = description[:300].rstrip() + "..."

        table = Table(
            title="Video / Audio Info",
            show_header=False,
            border_style="cyan",
        )
        table.add_column("Field", style="bold magenta", no_wrap=True)
        table.add_column("Value", style="white", overflow="fold")

        fields = [
            ("Title", info.get("title")),
            ("Uploader / Channel", info.get("uploader") or info.get("channel")),
            ("Duration", duration_str),
            ("Views", views_str),
            ("Like count", info.get("like_count")),
            ("Upload date", upload_str),
            ("Description", description or None),
            ("Thumbnail URL", info.get("thumbnail")),
            ("Webpage URL", info.get("webpage_url")),
        ]

        for k, v in fields:
            if v not in (None, ""):
                table.add_row(k, str(v))

        console.print(Panel(table, border_style="green"))
        return True
