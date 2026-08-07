from __future__ import annotations

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


class YTDL:
    def __init__(self):
        ensure_dirs()

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
            elif status == "error":
                progress.update(task_id, description="[bold red]Error[/bold red]")

        return hook

    def _base_opts(
        self,
        outtmpl: str,
        no_playlist: bool = False,
        quiet: bool = True,
    ) -> dict[str, Any]:
        return {
            "outtmpl": outtmpl,
            "noplaylist": no_playlist,
            "quiet": quiet,
            "no_warnings": True,
            "ignoreerrors": False,
            "retries": 3,
            "fragment_retries": 3,
        }

    def _audio_opts(
        self,
        codec: str = "mp3",
        quality: str = "320",
        embed_thumbnail: bool = True,
        keep_thumbnail: bool = False,
        no_playlist: bool = False,
        output_dir: Optional[Path] = None,
    ) -> dict[str, Any]:
        out_dir = output_dir or AUDIO_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        # Prefer high quality. "best" lets yt-dlp pick.
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
            outtmpl=str(out_dir / "%(title)s.%(ext)s"),
            no_playlist=no_playlist,
        )

        write_thumb = embed_thumbnail or keep_thumbnail

        opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": postprocessors,
                "writethumbnail": write_thumb,
            }
        )

        # If user wants to keep the thumbnail as a separate file, put it in Thumbnails/
        if keep_thumbnail:
            opts["outtmpl"] = {
                "default": str(out_dir / "%(title)s.%(ext)s"),
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
            outtmpl=str(out_dir / "%(title)s.%(ext)s"),
            no_playlist=no_playlist,
        )
        opts.update(
            {
                "format": fmt,
                "merge_output_format": "mp4",
                "writesubtitles": write_subs or embed_subs,
                "writeautomaticsub": write_subs or embed_subs,
                "subtitleslangs": ["en", "ar", "*"],
                "embedsubtitles": embed_subs,
            }
        )
        return opts

    def _run(self, url: str, opts: dict[str, Any], label: str) -> None:
        progress, task_id = self._make_progress(label)
        opts = dict(opts)  # copy
        opts["progress_hooks"] = [self._progress_hook(progress, task_id)]

        with progress:
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                console.print("[bold green]✓ Done[/bold green]")
            except yt_dlp.utils.DownloadError as e:
                console.print(f"[bold red]Download error:[/bold red] {e}")
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

    def download_audio(
        self,
        url: str,
        codec: str = "mp3",
        quality: str = "320",
        embed_thumbnail: bool = True,
        keep_thumbnail: bool = False,
        no_playlist: bool = False,
        output_dir: Optional[str] = None,
    ) -> None:
        """Download audio and (by default) embed thumbnail + metadata."""
        out = Path(output_dir) if output_dir else None
        opts = self._audio_opts(
            codec=codec,
            quality=quality,
            embed_thumbnail=embed_thumbnail,
            keep_thumbnail=keep_thumbnail,
            no_playlist=no_playlist,
            output_dir=out,
        )
        self._run(url, opts, "Downloading audio")

    def download_video(
        self,
        url: str,
        quality: str = "best",
        no_playlist: bool = False,
        output_dir: Optional[str] = None,
        write_subs: bool = False,
        embed_subs: bool = False,
    ) -> None:
        """Download video (mp4)."""
        out = Path(output_dir) if output_dir else None
        opts = self._video_opts(
            quality=quality,
            no_playlist=no_playlist,
            output_dir=out,
            write_subs=write_subs,
            embed_subs=embed_subs,
        )
        self._run(url, opts, "Downloading video")

    def show_info(self, url: str) -> None:
        """Print useful metadata without downloading."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if not info:
                console.print("[red]No info returned.[/red]")
                return

            table = Table(title="Video / Audio Info", show_header=False, border_style="cyan")
            table.add_column("Field", style="bold magenta")
            table.add_column("Value", style="white")

            fields = [
                ("Title", info.get("title")),
                ("Uploader / Channel", info.get("uploader") or info.get("channel")),
                ("Duration (sec)", info.get("duration")),
                ("View count", info.get("view_count")),
                ("Like count", info.get("like_count")),
                ("Upload date", info.get("upload_date")),
                ("Description", (info.get("description") or "")[:300] + "..."),
                ("Thumbnail", info.get("thumbnail")),
                ("Webpage URL", info.get("webpage_url")),
            ]

            for k, v in fields:
                if v is not None:
                    table.add_row(k, str(v))

            console.print(Panel(table, border_style="green"))
        except Exception as e:
            console.print(f"[bold red]Error extracting info:[/bold red] {e}")
