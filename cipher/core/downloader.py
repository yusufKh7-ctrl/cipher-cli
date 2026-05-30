from typing import Any
import yt_dlp
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from cipher.core.config import AUDIO_DIR, VIDEO_DIR, ensure_dirs

console = Console()



class YTDL:
    def __init__(self):
        ensure_dirs()

        self.progress = None
        self.task_id = None
    
    def _hook(self, d):
        status = d['status']

        if status == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)

            if total and self.progress and self.task_id is not None:
                self.progress.update(
                    self.task_id,
                    total=total,
                    completed=downloaded,
                )

        elif status == 'finished':
            if self.progress and self.task_id is not None:
                self.progress.update(
                    self.task_id,
                    description=f"Processing: {d['filename']}"
                )        
    def _video_opts(self) -> dict[str, Any]:
        return {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': str(VIDEO_DIR / '%(title)s.%(ext)s'),
            'progress_hooks': [self._hook],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
        }
        
    def _audio_opts(self) -> dict[str, Any]:
        return {
            'format': 'bestaudio/best',
            'outtmpl': str(AUDIO_DIR / '%(title)s.%(ext)s'),
            'progress_hooks': [self._hook],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
    

    def _download(self, url: str, opts: dict[str, Any], label: str):
        with Progress(
            SpinnerColumn("moon"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(style="blue", complete_style="magenta", finished_style="bold cyan"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task_id = progress.add_task(f"[bold green]{label}...[/bold green]")

            def hook(d):
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)

                    if total:
                        progress.update(
                            task_id,
                            completed=downloaded,
                            total=total
                        )
                elif d['status'] == 'finished':
                    progress.update(
                        task_id,
                        description=f"Done: {d['filename']}"
                    )
            opts['progress_hooks'] = [hook]

            try:
                with yt_dlp.YoutubeDL(opts) as ydl: #type: ignore
                    ydl.download([url])
            except Exception as e:
                    console.print(f"[bold red]Error:[/bold red] {e}")

    def download_video(self, url: str):
        """Download video from YouTube."""
        self._download(url, self._video_opts(), "Downloading video")
    
    def download_audio(self, url: str):
        """Download audio from YouTube."""
        self._download(url, self._audio_opts(), "Downloading audio")