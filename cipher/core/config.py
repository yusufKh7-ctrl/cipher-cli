from pathlib import Path


DOWNLOADS_DIR = Path.home() / "Downloads" / "Cipher"
AUDIO_DIR = DOWNLOADS_DIR / "Audio"
VIDEO_DIR = DOWNLOADS_DIR / "Video"

def ensure_dirs():
    """Create directories if they don't exist."""
    for dir in [DOWNLOADS_DIR, AUDIO_DIR, VIDEO_DIR]:
        dir.mkdir(parents=True, exist_ok=True)
