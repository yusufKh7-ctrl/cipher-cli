from pathlib import Path
import os
import platform


def get_base_dir():
    if os.path.exists("/data/data/com.termux/files/usr"):
        return Path("/storage/emulated/0")
    else:
        return Path.home() / "Downloads" / "Cipher"


DOWNLOADS_DIR = get_base_dir()
IS_ANDROID = os.path.exists("/data/data/com.termux/files/usr")

AUDIO_DIR = DOWNLOADS_DIR / "Music" / "Cipher"
VIDEO_DIR = DOWNLOADS_DIR / ("DCIM" if IS_ANDROID else DOWNLOADS_DIR / "Videos") / "Cipher"
THUMBNAIL_DIR = DOWNLOADS_DIR / "Thumbnails"


def ensure_dirs():
    """Create directories if they don't exist."""
    for d in (DOWNLOADS_DIR, AUDIO_DIR, VIDEO_DIR, THUMBNAIL_DIR):
        d.mkdir(parents=True, exist_ok=True)


# Quick test
if __name__ == "__main__":
    print(f"🌍 platform: {'Android (Termux)' if IS_ANDROID else platform.system()}")
    print(f"📁 Downloads dir: {DOWNLOADS_DIR}")
    print(f"🎵 Audio dir: {AUDIO_DIR}")
    print(f"🎬 Videos dir: {VIDEO_DIR}")
    print(f"🖼️ Thumbnails dir: {THUMBNAIL_DIR}")
