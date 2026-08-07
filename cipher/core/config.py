from pathlib import Path


DOWNLOADS_DIR = Path.home() / "Downloads" / "Cipher"
AUDIO_DIR = DOWNLOADS_DIR / "Audio"
VIDEO_DIR = DOWNLOADS_DIR / "Video"
THUMBNAIL_DIR = DOWNLOADS_DIR / "Thumbnails"


def ensure_dirs():
    """Create directories if they don't exist."""
    for d in (DOWNLOADS_DIR, AUDIO_DIR, VIDEO_DIR, THUMBNAIL_DIR):
        d.mkdir(parents=True, exist_ok=True)
